from math import prod
import email
from multiprocessing import context
from tkinter import Image
from typing import Any
from django.core.paginator import (Paginator, PageNotAnInteger, EmptyPage)
from django.contrib.auth.views import (
    LogoutView as BaseLogoutView, PasswordChangeView as BasePasswordChangeView,
    PasswordResetDoneView as BasePasswordResetDoneView, PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .services.account_service import account_service
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.db import IntegrityError
from django.utils.encoding import force_text
from .forms import ProductForm, TransporterSignUpForm, ProductImageForm, VariantForm, VendorSignUpForm, CustomerSignUpForm, RestorePasswordForm, RequestRestorePasswordForm, OpeningHoursForm, ProductWithVariantForm
from apps.ordering.models import Order, OrderItem
from apps.newProduct.models import Color, Height, Images, Length, Product, ProductImage, Size, Variants, Weight, Width, UnitTypes
from .models import Profile, Transporter, UserWishList, Vendor, Customer, OpeningHours, VendorDelivery
from apps.vendor.models import VendorDelivery
from apps.ordering.models import OrderItem, ShopCart, ShopCartForm
import code
from distutils import command
from itertools import chain, product
import re
from django.http.response import HttpResponse
from django.views.generic import TemplateView
from decimal import Decimal
from django.contrib import messages
from django.conf import settings
from apps.coupon.models import Coupon
from django.shortcuts import render, redirect,  get_object_or_404, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.utils.text import slugify
from apps.cart.models import District, Sector, Cell, Village
from django.contrib.auth.models import User, Permission
from django import template
from apps.cart.cart import Cart
register = template.Library()


def login_request(request):
    if request.user.is_authenticated:
        return redirect('frontpage')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        username = request.POST['username']
        password = request.POST['password']

        username = User.objects.get(email=username)

        user = authenticate(
            request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_superuser:
                print("=== superuser")
                try:
                    request.session['username'] = username.username
                except:
                    pass
                return redirect("/dashboard/")

            try:
                customer = Customer.objects.get(email=username)
                request.session['username'] = customer.customername
                request.session['phone'] = customer.phone
                request.session['email'] = customer.email
                request.session['address'] = customer.address
                request.session['company_code'] = customer.company_code
                request.session['customer'] = True
                try:
                    orders = []
                    for row in Order.objects.filter(email=username):
                        order = {}
                        order["created_at"] = row.created_at.strftime(
                            "%Y/%m/%d, %H:%M:%S")
                        order["status"] = row.status
                        items = []
                        total_quantity = 0
                        subtotal_amount = 0
                        subtotal = 0
                        for item_ in OrderItem.objects.filter(id=row.id).select_related("product"):
                            item = {}
                            item["product_title"] = item_.product.title
                            item["quantity"] = str(item_.quantity)
                            item["price"] = str(item_.price)
                            total_quantity += item_.quantity
                            subtotal += item_.subtotal
                            subtotal_amount += item_.price
                            items.append(item)
                        order["items"] = items
                        order["subtotal_amount"] = str(subtotal_amount)
                        order["total_quantity"] = str(total_quantity)
                        order["paid_amount"] = str(row.paid_amount)
                        order["delivery_cost"] = str(row.delivery_cost)
                        coupon_discount = ""
                        coupon_code = str(row.used_coupon)
                        if coupon_code != "None":
                            try:
                                coupon = Coupon.objects.get(code=coupon_code)
                                if coupon:
                                    coupon_discount = str(
                                        coupon.discount) + " %"
                            except:
                                pass
                        order["coupon_discount"] = coupon_discount
                        orders.append(order)


                    request.session['orders'] = orders
                    messages.info(
                        request, f"You are now logged in as { username }.")
                    return redirect('frontpage')
                except Exception as e:
                    print(e)

            except Exception as e:
                pass

            try:
                transporter = Transporter.objects.get(email=request.user)
                request.session['username'] = transporter.transporter_name
                print(transporter)
                return redirect("transporter-admin")
            except Exception as e:
                pass

            try:
                vendor = Vendor.objects.get(email=username)
                if vendor.logo:
                    request.session['logo'] = vendor.logo.url
                request.session['status'] = vendor.status
                request.session['email'] = vendor.email
                request.session['username'] = vendor.company_name
                request.session['vendor'] = True

            except Exception as e:
                pass

            messages.info(request, f"You are now logged in as { username }.")
            return redirect("vendor_admin")

        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "vendor/login.html", {'form': form})


def logout_request(request):
    try:
        if request.session['username']:
            del request.session['username']
    except Exception as e:
        pass

    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('frontpage')


def email_user(who, subject, message, from_email=settings.DEFAULT_EMAIL_FROM, **kwargs):
    """Send an email to this user."""
    send_mail(subject, message, from_email, [who.email], **kwargs)


def activation_sent_view(request):
    return render(request, 'activation_sent.html')


def changing_password_view(request):
    return render(request, 'changing_password.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true
        user.is_active = True
        # set signup_confirmation true
        user.profile.signup_confirmation = True
        user.save()
        
        messages.success(request, ('Your account has been confirmed.'))
        return redirect('login')
    else:
        
        messages.warning(
            request, ('The confirmation link was invalid, possibly because it has already been used.'))
        return redirect('frontpage')


def activate_password(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print("uid = ", uid)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    print("user = ", user)
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        
        user.password = ""
        user.save()
        messages.success(
            request, ('Your password reset request has been approved.'))
        return redirect('restore_password')
    else:
        
        messages.warning(
            request, ('The confirmation link was invalid, possibly because it has already been used.'))
        return redirect('frontpage')


def become_vendor(request):
    if request.user.is_authenticated:
        logout(request)

    districts = District.objects.all()
    if request.method == 'POST':
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data.get('email')).exists():
                user = User.objects.get(
                    username=form.cleaned_data.get('email'))
            else:
                
                user = form.save(commit=False)
                user.username = form.cleaned_data.get('email')
                user.is_active = False
                user.save()
            if not Profile.objects.filter(email=form.cleaned_data.get('email')).exists():
                profile = Profile(
                    user=user, email=form.cleaned_data.get('email'))
                profile.save()

            district_id = form.cleaned_data['district']
            sector_id = form.cleaned_data['sector']
            cell_id = form.cleaned_data['cell']
            village_id = form.cleaned_data['village']
            company_registration = request.FILES.get('reg_image')
            privacy_checked = request.POST.get('is_privacy')
            

            vendor = Vendor(email=form.cleaned_data.get('email'),
                            company_name=form.cleaned_data.get('company_name'),
                            company_code=form.cleaned_data.get('company_code'),
                            village_id=village_id,
                            district_id=district_id,
                            sector_id=sector_id,
                            cell_id=cell_id,
                            address=form.cleaned_data.get('address'),
                            phone=form.cleaned_data.get('phone'),
                            company_registration=company_registration,
                            privacy_checked=privacy_checked,
                            user=user)
            vendor.save()

            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            # load a template like get_template()
            # and calls its render() method immediately.
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                # method will generate a hash value with user related data
                'token': token,
            })
            
            email_user(user, subject, message)

            return redirect('activation_sent')
    else:
        form = VendorSignUpForm()
    return render(request, 'vendor/become_vendor.html', {'form': form, 'districts': districts})


@login_required
def vendor_admin(request):
    try:
        vendor = request.user.vendor
    except Exception as e:
        print(e)
        return redirect(
            'frontpage',
        )

    if request.method == 'POST':
        delivery_price = request.POST.get('delivery_price')
        vendor_delivery = VendorDelivery.objects.filter(vendor=vendor).first()
        print('dp:', delivery_price)
        print(delivery_price is None)
        if delivery_price:
            if vendor_delivery:
                vendor_delivery.price = delivery_price
                vendor_delivery.save()
            else:
                VendorDelivery.objects.create(
                    vendor=vendor, price=delivery_price)
            return redirect('vendor_admin', vendor_slug=vendor)
        elif delivery_price is '':
            VendorDelivery.objects.filter(vendor=vendor).delete()
            return redirect('vendor_admin')

        day = request.POST.get("day")
        from_ = request.POST.get("from")
        to_ = request.POST.get("to")
        hour = OpeningHours()
        hour.vendor = vendor
        hour.from_hour = from_
        hour.weekday = day
        hour.to_hour = to_
        hour.save()
        return redirect('working_hours')
    else:
        products = Product.objects.filter(vendor=vendor)
        variants = []
        for pr in products:
            if pr.variant != 'None':
                variants = Variants.objects.filter(product=pr.id)

        product_limit = not vendor.products_limit <= ((products.__len__(
        ) + vendor.variants_vendor.all().__len__()) - Product.objects.filter(vendor=vendor, is_variant=True).__len__())

        orders = vendor.orders.all()

        

        opening_hours = vendor.Opening.all()
        form = OpeningHoursForm
        if len(opening_hours) <= 0:
            opening_hours = 0
        else:
            print(opening_hours[0].id)
        for order in orders:
            order.vendor_amount = 0
            order.vendor_paid_amount = 0
            order.fully_paid = True
            coupon_discount = 0
            coupon_code = str(order.used_coupon)
            if coupon_code != "None":
                try:
                    coupon = Coupon.objects.get(code=coupon_code)

                    if coupon:
                        coupon_discount = coupon.discount
                except:
                    pass
            order.coupon_discount = coupon_discount

            for item in order.items.all():
                if item.vendor == request.user.vendor:
                    if item.vendor_paid:
                        order.vendor_paid_amount += item.get_total_price()
                    else:
                        order.vendor_amount += item.get_total_price()
                        order.fully_paid = False
        vendor_delivery = VendorDelivery.objects.filter(vendor=vendor).first()
        delivery_price = vendor_delivery.price if vendor_delivery else ''
        
        
        user = request.user
        v = Vendor.objects.get(email=user)

        vendor_item_price = 0
        vendor_items_total_price = 0
        total_quantity = 0
        delivery_cost = 0
        for i in orders:
            orderItems = i.items.all()
            for items in orderItems:
                if v == items.vendor:
                    vendor_item_price = items.get_product_total_price()
                    vendor_items_total_price = vendor_item_price*items.quantity
                    total_quantity = items.quantity
                    if not items.product.is_free_delivery:
                        if i.delivery_type == "Vendor_Delivery":
                            delivery_cost = VendorDelivery.objects.get(
                                vendor=vendor).price
                            is_delivery = True
                            if delivery_cost == None:
                                delivery_cost = False
                        else:
                            delivery_cost = 0
                            is_delivery = False
            total_cost = float(
                vendor_items_total_price-(order.coupon_discount*vendor_items_total_price/100))
            total_cost += float(delivery_cost)

        vendor_items_total_price = round(Decimal(vendor_items_total_price), 2)
        total_cost = round(Decimal(vendor_items_total_price), 2)
        if vendor.logo:
            print(vendor.logo.url)   
        return render(
            request,
            'vendor/vendor_admin.html',
            {
                'vendor': vendor,
                'vendor_delivery_price': delivery_price,
                'form': form,
                'opening_hours': opening_hours,
                'products': products,
                'orders': orders,
                'variants': variants,
                'total': total_cost,
                'product_limit': product_limit
            }
        )


@login_required
def working_hours(request):
    vendor = request.user.vendor

    if request.method == 'POST':
        day = request.POST.get("day")
        from_ = request.POST.get("from")
        to_ = request.POST.get("to")
        hour = OpeningHours()
        hour.vendor = vendor
        hour.from_hour = from_
        hour.weekday = day
        hour.to_hour = to_
        hour.save()
        return redirect('working_hours')
    else:
        opening_hours = vendor.Opening.all()
        form = OpeningHoursForm
        if len(opening_hours) <= 0:
            opening_hours = 0

    return render(request,
                  'vendor/working_hours.html', {
                      'form': form,
                      'opening_hours': opening_hours,
                      'vendor':vendor
                  })


@login_required
def delivery_cost(request):
    vendor = request.user.vendor

    if vendor.status == 'DIAMOND' or vendor.status == 'SAPPHIRE':
        messages.info(request,f"You are not eligible to setup your Delivery Cost")
        return redirect('vendor_admin')

    if request.method == 'POST':
        delivery_price = request.POST.get('delivery_price')
        vendor_delivery = VendorDelivery.objects.filter(vendor=vendor).first()
        
        if delivery_price:
            if vendor_delivery:
                vendor_delivery.price = delivery_price
                vendor_delivery.save()
            else:
                VendorDelivery.objects.create(
                    vendor=vendor, price=delivery_price
                )
            return redirect('delivery_cost')
        elif delivery_price is '':
            VendorDelivery.objects.filter(vendor=vendor).delete()
            return redirect('delivery_cost')

    vendor_delivery = VendorDelivery.objects.filter(vendor=vendor).first()
    delivery_price = vendor_delivery.price if vendor_delivery else ''
    
    return render(
        request,
        'vendor/delivery_cost.html',
        {
            'vendor': vendor,
            'vendor_delivery_price': delivery_price,
        }
    )


@ login_required
def remove_opening(request, pk):
    vendor = request.user.vendor
    opening = OpeningHours.objects.filter(id=pk).first()
    opening.delete()
    return redirect('working_hours')


@login_required
def vendor_products(request):
    vendor = request.user.vendor
    products_list = products = Product.objects.filter(vendor=vendor,visible=True)
    paginator = Paginator(products_list, 5)
    page = request.GET.get('page')

    images = request.FILES.getlist('images')
    if images:
        print(images)
    else:
        print('Not selected')    

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    variants = []
    for pr in products:
        if pr.variant != 'None':
            variants = Variants.objects.filter(product=pr.id,visible=True)
                
    product_limit = not vendor.products_limit <= ((products.__len__(
    ) + vendor.variants_vendor.all().__len__()) - Product.objects.filter(vendor=vendor, is_variant=True).__len__())

    product_list = products = Product.objects.filter(vendor=vendor,visible=True,is_variant=False)
    lists=list(chain(product_list,variants))
    paginator = Paginator(lists, 5)
    page = request.GET.get('page')

    try:
        lists_products = paginator.page(page)
    except PageNotAnInteger:
        lists_products = paginator.page(1)
    except EmptyPage:
        lists_products = paginator.page(paginator.num_pages)    

          

    return render(request, 'vendor/products.html',
                  {
                      'product_limit': product_limit,
                      'products': products,
                      'variants': variants,
                      'vendor':vendor,
                      'lists_products':lists_products
                  })

@login_required
def order_history(request):
    vendor = request.user.vendor
    orders_list = vendor.orders.all()
    paginator = Paginator(orders_list, 7)
    page = request.GET.get('page')

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    for order in orders:
        order.vendor_amount = 0
        order.vendor_paid_amount = 0
        order.fully_paid = True
        coupon_discount = 0
        coupon_code = str(order.used_coupon)
        if coupon_code != "None":
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon:
                    coupon_discount = coupon_discount
            except:
                pass
        order.coupon_discount = coupon_discount

        for item in order.items.all():
            if item.vendor == request.user.vendor:
                if item.vendor_paid:
                    order.vendor_paid_amount += item.get_total_price()
                else:
                    order.vendor_amount += item.get_total_price()
                    order.fully_paid = False
    vendor_delivery = VendorDelivery.objects.filter(vendor=vendor).first()
    delivery_price = vendor_delivery.price if vendor_delivery else ''

    user = request.user
    v = Vendor.objects.get(email=user)

    vendor_item_price = 0
    vendor_items_total_price = 0
    total_quantity = 0
    delivery_cost = 0

    for i in orders:
        orderItems = i.items.all()
        for items in orderItems:
            if v == items.vendor:
                vendor_item_price = items.get_product_total_price()
                vendor_items_total_price = vendor_item_price*items.quantity
                total_quantity = items.quantity
                if not items.product.is_free_delivery:
                    if i.delivery_type == "Vendor_Delivery":
                        delivery_cost = VendorDelivery.objects.get(
                            vendor=vendor).price
                        is_delivery = True
                        if delivery_cost == None:
                            delivery_cost = False
                    else:
                        delivery_cost = 0
                        is_delivery = False
        total_cost = float(vendor_items_total_price -
                           (order.coupon_discount*vendor_items_total_price/100))
        total_cost += float(delivery_cost)

    vendor_items_total_price = round(Decimal(vendor_items_total_price), 2)
    total_cost = round(Decimal(vendor_items_total_price), 2)

    return render(
        request,
        'vendor/orders-history.html', {
            'vendor': vendor,
            'vendor_delivery_price': delivery_price,
            'orders': orders,
        }
    )


@ login_required
def add_product(request):

    vendor = request.user.vendor
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            if len(Product.objects.filter(vendor=vendor)) < vendor.products_limit:
                product = form.save(commit=False)
                product.vendor = request.user.vendor
                product.slug = slugify(product.title)
                product.visible = True
                product.is_variant = False
                vendor = request.user.vendor
                product.save()
                messages.add_message(
                    request, messages.SUCCESS, "The product {} is successfully added and now under review".format(product.title))
                return redirect('products')
            else:
                messages.add_message(
                    request, messages.ERROR, "You can't add new product.you reached product limit")
                return redirect('vendor_admin')

        else:
            messages.add_message(request, messages.ERROR,
                                 "* Error: Input fields are not valid.")
            return redirect('add_product')

    else:
        vendor = request.user.vendor
        products = len(Product.objects.filter(vendor=vendor))
        
        form = ProductForm()

    return render(request, 'vendor/add_product.html', {'form': form,'vendor':vendor})


@ login_required
def add_product_with_variant(request):
    vendor = request.user.vendor
    if request.method == 'POST':
        form = ProductWithVariantForm(request.POST, request.FILES)
        if form.is_valid():
            if len(Product.objects.filter(vendor=vendor)) < vendor.products_limit:
                product = form.save(commit=False)
                product.vendor = request.user.vendor
                product.slug = slugify(product.title)
                product.visible = True
                product.is_variant = True
                vendor = request.user.vendor
                product.save()
                messages.add_message(
                    request, messages.SUCCESS, "The product {} is successfully added and now under review".format(product.title))
                return redirect('products')
            else:
                messages.add_message(
                    request, messages.ERROR, "You can't add new product.you reached product limit")
                return redirect('vendor_admin')
        else:
            messages.add_message(request, messages.ERROR,
                                 "* Error: Input fields are not valid.")
            return redirect('add_product_without_variant')
    else:
        vendor = request.user.vendor
        products = len(Product.objects.filter(vendor=vendor))
        
        form = ProductWithVariantForm()

    return render(request, 'vendor/add_product_with_variant.html', {'form': form,'vendor':vendor})


@ login_required
def add_variant(request):
    vendor = request.user.vendor
    product = Product.objects.filter(vendor=vendor)
    color = Color.objects.all()
    size = Size.objects.all()
    weight = Weight.objects.all()
    height = Height.objects.all()
    length = Length.objects.all()
    width = Width.objects.all()
    images = Images.objects.all()
    unitTpye = UnitTypes.objects.all()

    if request.method == 'POST':
        variant_form = VariantForm(request.POST, request.FILES, user=vendor)
        if variant_form.is_valid():
            if len(Product.objects.filter(vendor=vendor)) < vendor.products_limit:
                product=variant_form.cleaned_data['product']
                if product.vendor == vendor:
                    variant = variant_form.save(commit=False)
                    variant.vendor = request.user.vendor
                    variant.is_vat = True
                    variant.visible = True
                    variant.save()
                    messages.add_message(
                        request, messages.SUCCESS, "The product variant {} is successfully added ".format(
                        variant.title)
                    )
                else:
                    messages.add_message(
                        request, messages.ERROR, "Please Select from your Product"
                    )  
                
                return redirect('products')
            else:
                messages.add_message(
                    request, messages.ERROR, "You can't add new product.you reached product limit")
                return redirect('vendor_admin')
        else:
            messages.add_message(request, messages.ERROR,
                                 "* Error: Input fields are not valid.")

            return redirect('add_variant')
    else:
        vendor = request.user.vendor
        
        products = len(Product.objects.filter(vendor=vendor))
        
        variant_form=VariantForm(user=vendor)

    return render(request, 'vendor/add_variant.html', {'form': variant_form, 'product': product,
                                                       'color': color, 'size': size,
                                                       'weight': weight, 'length': length, 'height': height,
                                                       'width': width, 'images': images,
                                                       'unitType': unitTpye})


@ login_required
def edit_product(request, pk):
    check = Product.objects.filter(id=pk).first()
    vendor = request.user.vendor
    product = vendor.newProducts.filter(pk=pk).first()
    productImages = ProductImage.objects.filter(product=product)
    ImageForm = inlineformset_factory(Product,ProductImage,can_delete=False,fields=['image'],extra=0)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        imageForm = ImageForm(request.POST, request.FILES, instance=product)
        if form.is_valid() and imageForm.is_valid():
            form.save()
            imageForm.save()
        
            messages.info(request,"Product Updated")
            return redirect('products')
    else:
        form = ProductForm(instance=product)
        imageForm = ImageForm(instance=product)

    return render(request, 'vendor/edit_product.html', {'form': form,'product': product,'imagesForm':imageForm})



@login_required
def edit_product_variant(request,pk):
   vendor=request.user.vendor
   variant=vendor.variants_vendor.filter(pk=pk).first()
   
   productImages = ProductImage.objects.filter(variant=variant).first()
   ImageForm = inlineformset_factory(Variants,ProductImage,can_delete=False,fields=['image'],extra=0)
   if request.method == 'POST':
       form = VariantForm(request.POST, request.FILES,instance=variant,user=vendor)
       imageForm = ImageForm(request.POST, request.FILES, instance=variant)
       if form.is_valid() and imageForm.is_valid():
           form.save()
           imageForm.save()
           messages.info(request,"Product Updated")
           return redirect('products')
   else:
       form = VariantForm(instance=variant,user=vendor)
       imageForm = ImageForm(instance=variant)

   return render(request, 'vendor/edit_product_variant.html',{'form':form,'variant':variant,'imageForm':imageForm})                     

@ login_required
def delete_product(request, pk):
    Product.objects.filter(id=pk).update(visible=False)
    messages.info(request,"product Deleted")    
    return redirect('products')
        

@login_required
def delete_product_variant(request, pk):
    Variants.objects.filter(id=pk).update(visible=False)
    messages.info(request,"Product Deleted")
    return redirect('products')

@ login_required
def upload_logo(request):
    vendor = request.user.vendor
    if request.method == 'POST':
        if "image" in request.FILES and len(request.FILES["image"]) > 0:
            vendor.logo = request.FILES["image"]
            vendor.save()
            request.session['logo'] = Vendor.objects.get(
                email=vendor.email).logo.url
            messages.info(request, f"Company Logo Updated Sucessfully.")
            
    return redirect('vendor_admin')


@ login_required
def add_productimage(request, pk):
    vendor = request.user.vendor
    product = Product.objects.get(vendor=vendor, id=pk)
    
    

    if request.method == 'POST':
        images = request.FILES.getlist('images')
        if len(images) > 3 :
            messages.info(request,f"You can't can't add more than 3 images")

        elif len(ProductImage.objects.filter(product=product)) >= 3:
            messages.info(request,f"You have reached product images limit")
            
        elif len(images) + len(ProductImage.objects.filter(product=product)) > 3:
            if len(images) > len(ProductImage.objects.filter(product=product)):
                img=len(images) - len(ProductImage.objects.filter(product=product))
            elif len(images) == len(ProductImage.objects.filter(product=product)):
                img=3 - len(images)    
            else:
                img=len(ProductImage.objects.filter(product=product)) -  len(images) 
                
            messages.info(request, f"You can't add more than 3 images only:" + str(img))
        elif len(images) <= 0:
            messages.info(request,f"No image Uploaded")
        else:
            for image in images:
                ProductImage.objects.create(product=product,image=image)
            messages.info(request,f"Product image uploaded Successfully")
                
    return redirect('products')            

@login_required
def add_productimage_variant(request, pk):
    variant = Variants.objects.get(id=pk)
    if request.method == 'POST':
        images=request.FILES.getlist('imgs')
        print(images)
        productImages=ProductImage.objects.filter(variant=variant)
        if len(images) > 3:
            messages.info(request,f"You can't add more than 3 images")
        elif len(productImages) >=3 :
            messages.info(request,f"You have reached product images limit")
        elif len(images) + len(productImages) > 3:
            if len(images) > len(productImages):
                img=len(images) - len(productImages)
            elif len(images) == len(productImages):
                img=3 - len(images)
            else:
                img=len(productImages) - len(images)
            messages.info(request,f"You can't add more than 3 images only:" + str(img))
        elif len(images) <= 0:
            messages.info(request,f"No Image Uploaded")    
        else:
            for image in images:
                ProductImage.objects.create(variant=variant,image=image)
            messages.info(request,f"Product image uploaded successfully")                        
        
    return redirect('products')               


@ login_required
def del_productimage(request, pk):
    vendor = request.user.vendor
    product = Product.objects.get(vendor=vendor, id=pk)
    print(product.product_images.all())
    if product.is_variant:
        print('variant')
    else:
        if request.method == 'POST':
            images = request.FILES.getlist('images')
            for image in images:
                product_image = ProductImage.objects.create(product=product)
                product_image = Image(image=image, imgtype=Any)
                product_image.save()
            messages.info(request, f"Product image uploaded Successfully")
            print("success")
    return redirect('products')


@ login_required
def del_productimage(request, pk):
    vendor = request.user.vendor
    product = Product.objects.get(vendor=vendor, id=pk)
    print(product.product_images.all())
    if product.is_variant:
        print('variant')
    else:
        if request.method == 'POST':
            images = request.FILES.getlist('images')
            for image in images:
                product_image = ProductImage.objects.create(product=product)
                product_image = Image(image=image, imgtype=Any)
                product_image.save()
            messages.info(request, f"Product image uploaded Successfully")
            print("success")
    return redirect('products')



@ login_required
def edit_vendor(request):
    vendor = request.user.vendor

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        delivery_price = request.POST.get('delivery_price')

        if name:
            vendor.created_by.email = email
            vendor.created_by.save()

            vendor_delivery = VendorDelivery.objects.filter(
                vendor=vendor).first()
            if delivery_price:
                if vendor_delivery:
                    vendor_delivery.price = delivery_price
                    vendor_delivery.save()
                else:
                    VendorDelivery.objects.create(
                        vendor=vendor, price=delivery_price)

            vendor.name = name
            vendor.save()

            return redirect('vendor_admin')

    return render(request, 'vendor/edit_vendor.html', {'vendor': vendor})


def vendors(request):
    vendors_list = Vendor.objects.filter(enabled=True)
    paginator = Paginator(vendors_list, 5)
    page = request.GET.get('page')

    try:
        vendors = paginator.page(page)
    except PageNotAnInteger:
        vendors = paginator.page(1)
    except EmptyPage:
        vendors = paginator.page(paginator.num_pages)

    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = UserWishList.objects.filter(user=current_user)
        # cart.clear()
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total = cart.get_cart_cost()
        tax = cart.get_cart_tax()
        grandTotal = cart.get_cart_cost() + cart.get_cart_tax()
        if not request.session.get('comparing'):
            comparing = 0
        else:
            comparing = request.session['comparing'].__len__()

        if not request.session.get('comparing_variants'):
            compare_var = 0
        else:
            compare_var = request.session['comparing_variants'].__len__()

        total_compare = comparing + compare_var
    else:
        cart = 0
        subtotal = 0
        tax = 0
        total = 0
        grandTotal = 0
        shopcart = None
        wishlist = 0
        total_compare = 0

    return render(request, 'vendor/vendors.html', {'vendors': vendors,
                                                   'shopcart': shopcart,
                                                   'subtotal': total,
                                                   'tax': tax,
                                                   'total': grandTotal,
                                                   'wishlist': wishlist,
                                                   'total_compare': total_compare
                                                   })


def vendor(request, slug):
    vendor = Vendor.objects.get(slug=slug)
    product_list = Product.objects.filter(vendor=vendor)
    paginator = Paginator(product_list, 6)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = UserWishList.objects.filter(user=current_user)
        # cart.clear()
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total = cart.get_cart_cost()
        tax = cart.get_cart_tax()
        grandTotal = cart.get_cart_cost() + cart.get_cart_tax()
        if not request.session.get('comparing'):
            comparing = 0
        else:
            comparing = request.session['comparing'].__len__()

        if not request.session.get('comparing_variants'):
            compare_var = 0
        else:
            compare_var = request.session['comparing_variants'].__len__()

        total_compare = comparing + compare_var
    else:
        cart = 0
        tax = 0
        total = 0
        grandTotal = 0
        shopcart = None
        wishlist = 0
        total_compare = 0

    return render(request, 'vendor/vendor.html',
                  {'vendor': vendor,
                   'products': products,
                   'shopcart': shopcart,
                   'subtotal': total,
                   'tax': tax,
                   'total': grandTotal,
                   'wishlist': wishlist,
                   'total_compare': total_compare
                   })


def become_customer(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)

        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data.get('email')).exists():
                user = User.objects.get(
                    username=form.cleaned_data.get('email'))
            else:
                user = form.save(commit=False)
                user.username = form.cleaned_data.get('email')
                user.is_active = False
                user.save()
            if not Profile.objects.filter(email=form.cleaned_data.get('email')).exists():
                profile = Profile(
                    user=user, email=form.cleaned_data.get('email'))
                profile.save()

            privacy_checked = request.POST.get('is_privacy')
            

            customer = Customer(
                customername=form.cleaned_data.get('customername'),
                email=form.cleaned_data.get('email'),
                address=form.cleaned_data.get('address'),
                phone=form.cleaned_data.get('phone'),
                company_code=form.cleaned_data.get('company_code'),
                privacy_checked=privacy_checked,
                user=user
            )
            customer.save()

            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            # load a template like get_template()
            # and calls its render() method immediately.
            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            email_user(user, subject, message)

            return redirect('activation_sent')
    else:
        form = CustomerSignUpForm()

    return render(request, 'customer/become_customer.html', {'form': form})


class MyAccount(TemplateView):
    template_name = 'customer/myaccount.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            cart = Cart(request)
            current_user = request.user
            wishlist = UserWishList.objects.filter(user=current_user)
            shopcart = ShopCart.objects.filter(user_id=current_user.id)
            total = cart.get_cart_cost()
            if not request.session.get('comparing'):
                comparing = 0
            else:
                comparing = request.session['comparing'].__len__()

            if not request.session.get('comparing_variants'):
                compare_var = 0
            else:
                compare_var = request.session['comparing_variants'].__len__()

            total_compare = comparing + compare_var

        orders = account_service.calculate_order_sum(request.user.email)
        cart = Cart(request)
        context = self.get_context_data()
        context['orders'] = orders
        context['shopcart'] = shopcart
        context['wishlist'] = wishlist
        context['subtotal'] = total
        context['total_compare'] = total_compare
        context['user_id'] = request.user.id
        return self.render_to_response(context)


class OrderHistory(TemplateView):
    template_name = 'customer/order_history.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            cart = Cart(request)
            current_user = request.user
            wishlist = UserWishList.objects.filter(user=current_user)
            shopcart = ShopCart.objects.filter(user_id=current_user.id)
            total = cart.get_cart_cost()
            if not request.session.get('comparing'):
                comparing = 0
            else:
                comparing = request.session['comparing'].__len__()

            if not request.session.get('comparing_variants'):
                compare_var = 0
            else:
                compare_var = request.session['comparing_variants'].__len__()

            total_compare = comparing + compare_var

        orders_list = account_service.calculate_order_sum(request.user.email)
        paginator = Paginator(orders_list, 7)
        page = request.GET.get('page')

        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            orders = paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)

        cart = Cart(request)
        context = self.get_context_data()
        context['orders'] = orders
        context['wishlist'] = wishlist
        context['shopcart'] = shopcart
        context['subtotal'] = total
        context['total_compare'] = total_compare
        context['user_id'] = request.user.id
        return self.render_to_response(context)


def order_detail(request, id):
    order = Order.objects.get(pk=id)
    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = UserWishList.objects.filter(user=current_user)
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total = cart.get_cart_cost()
        if not request.session.get('comparing'):
            comparing = 0
        else:
            comparing = request.session['comparing'].__len__()

        if not request.session.get('comparing_variants'):
            compare_var = 0
        else:
            compare_var = request.session['comparing_variants'].__len__()

        total_compare = comparing + compare_var

    else:
        wishlist = 0
        total_compare = 0
    return render(request, 'customer/order_details.html', {
        'order': order,
        'wishlist': wishlist,
        'shopcart': shopcart,
        'subtotal': total,
        'total_compare': total_compare
    })


def vendor_order_detail(request, id):
    order = Order.objects.get(pk=id)
    
    for i in order.getCustomer():
        print(i.address)
    return render(request, 'vendor/vendor_order_details.html', {'order': order})


class WishListView(TemplateView):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        wishlist = UserWishList.objects.filter(user=kwargs['pk'])
        if not request.user.is_anonymous:
            cart = Cart(request)
            current_user = request.user
            # cart.clear()
            shopcart = ShopCart.objects.filter(user_id=current_user.id)
            total = cart.get_cart_cost()
            tax = cart.get_cart_tax()
            grandTotal = cart.get_cart_cost() + cart.get_cart_tax()
            if not request.session.get('comparing'):
                comparing = 0
            else:
                comparing = request.session['comparing'].__len__()

            if not request.session.get('comparing_variants'):
                compare_var = 0
            else:
                compare_var = request.session['comparing_variants'].__len__()

            total_compare = comparing + compare_var
        else:
            cart = 0
            tax = 0
            total = 0
            grandTotal = 0
            shopcart = None
            wishlist = 0
            total_compare = 0

        return render(request, 'customer/wishlist.html',
                      {
                          'wishlist': wishlist,
                          'shopcart': shopcart,
                          'subtotal': total,
                          'tax': tax,
                          'total': grandTotal,
                          'wishlist': wishlist,
                          'total_compare': total_compare
                      })


def request_restore_password(request):
    if request.method == 'POST':
        form = RequestRestorePasswordForm(request.POST)

        if form.is_valid():
            user = User.objects.filter(
                email=form.cleaned_data.get('email')).first()
            user.username = user.first_name + " " + user.last_name
            

            current_site = get_current_site(request)
            subject = 'Please Activate Your Password Reset'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            message = render_to_string('activation_restore_password.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            
            email_user(user, subject, message)

            messages.success(
                request, ('Please check your email for verification'))

            return redirect('changing_password')
        else:
            print("Invalid")

    else:
        form = RequestRestorePasswordForm()

        if not request.user.is_anonymous:
            cart = Cart(request)
            current_user = request.user
            wishlist = UserWishList.objects.filter(user=current_user)
            # cart.clear()
            shopcart = ShopCart.objects.filter(user_id=current_user.id)
            total = cart.get_cart_cost()
            tax = cart.get_cart_tax()
            grandTotal = cart.get_cart_cost() + cart.get_cart_tax()
            if not request.session.get('comparing'):
                comparing = 0
            else:
                comparing = request.session['comparing'].__len__()

            if not request.session.get('comparing_variants'):
                compare_var = 0
            else:
                compare_var = request.session['comparing_variants'].__len__()

            total_compare = comparing + compare_var
        else:
            cart = 0
            tax = 0
            total = 0
            grandTotal = 0
            shopcart = None
            wishlist = 0
            total_compare = 0

    return render(request, 'vendor/request_restore_password.html', {
        'form': form,
        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
    })


def restore_password(request):
    if request.method == 'POST':
        form = RestorePasswordForm(request.POST)

        if form.is_valid():
            user = User.objects.filter(
                email=form.cleaned_data.get('email')).first()
            if user.password == "":
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                messages.success(request, ('Your password has been reset.'))
            else:
                messages.warning(
                    request, ("Your password can't be changed. Please check your email."))
        return redirect('login')
    else:
        form = RestorePasswordForm()

    return render(request, 'vendor/restore_password.html', {'form': form})


def become_transporter(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = TransporterSignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email')
            user.save()

            profile = Profile(user=user, email=form.cleaned_data.get('email'))
            profile.save()

            transporter = Transporter(transporter_name=form.cleaned_data.get('transporter_name'),
                                      email=form.cleaned_data.get('email'),
                                      phone=form.cleaned_data.get('phone'),
                                      number_plate=form.cleaned_data.get(
                                          'number_plate'),
                                      user=user
                                      )
            transporter.save()

            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'

            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email_user(user, subject, message)

            messages.success(
                request, ('Please check your email for verification')
            )
            return redirect('activation_sent')
    else:
        form = TransporterSignUpForm()

    return render(request, 'become_transporter.html', {'form': form})


@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    return qty * unit_price


@login_required
def changeQty(request):
    url=request.META.get('HTTP_REFERER')
    if request.method == "POST":
        productid=request.POST.get('product_id')
        qty=request.POST.get('product_qty')
        product=Product.objects.get(id=productid)
        product.quantity=qty
        product.save()
        
    return redirect(url) 

@login_required
def changeQtyVariant(request):
    url=request.META.get('HTTP_REFERER')
    if request.method == "POST":
        productid=request.POST.get('product_id')
        qty=request.POST.get('product_qty')
        variant=Variants.objects.get(id=productid)
        variant.quantity=qty
        variant.save()
        
    return redirect(url)

@login_required
def changeStatus(request):
    url=request.META.get('HTTP_REFERER')
    if request.method == "POST":
        status = request.POST.get('status')
        order_id = request.POST.get('order_id')
        Order.objects.filter(id=order_id).update(status=status)
        
    return redirect(url)    


