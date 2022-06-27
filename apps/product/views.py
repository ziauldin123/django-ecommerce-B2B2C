from cgi import print_form
from email.mime import application
import random
from copy import copy

from datetime import datetime
from turtle import width
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, query
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView
from stripe import Review

from .forms import AddToCartForm, AddToCartInListForm,SearchForm, TestForm
from apps.newProduct.models import *
from django.core.paginator import (PageNotAnInteger, EmptyPage, Paginator)
from apps.rental.models import Capacity, Item, Year,Make,Item_Model,Engine,Amenity,Room,Type,Application
from apps.cart.cart import Cart
from .services.product_service import product_service
from .services.rental_filter import rental_service
from ..vendor.models import Customer, UserWishList
from apps.ordering.models import ShopCart, ShopCartForm
import re

def search(request):
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

    sorting = request.GET.get('sorting')
    if sorting == None:
        sorting = ("-created_at")

    products_list = Product.objects.filter(status=True,visible=True)
    rental_list = Item.objects.filter(review=True,visible=True)
    
    for product in products_list:
        variants = Variants.objects.filter(product=product)

    search_form = SearchForm(request.GET)    
    brands=Brand.objects.all()
    colors=Color.objects.all()
    weight=Weight.objects.all()
    length=Length.objects.all()
    width=Width.objects.all()
    size=Size.objects.all()
    height=Height.objects.all()
    year = Year.objects.all()
    make = Make.objects.all()
    item_model = Item_Model.objects.all()
    engine = Engine.objects.all()
    rooms = Room.objects.all()
    amenity = Amenity.objects.all()
    application = Application.objects.all()
    capacity = Capacity.objects.all()
    item_type = Type.objects.all()

    query=request.GET.get('query')
    price_to=request.GET.get('price_to')
    price_from=request.GET.get('price_from')
    query_brand=request.GET.getlist('brand')
    query_color=request.GET.getlist('color')
    query_weight=request.GET.getlist('weight')
    query_height=request.GET.getlist('height')
    query_width=request.GET.getlist('width')
    query_length=request.GET.getlist('length')
    query_year = request.GET.get('year')
    query_make = request.GET.get('make')
    query_model = request.GET.get('model')
    query_engine = request.GET.get('engine')
    query_rooms = request.GET.get('rooms')
    query_amenity = request.GET.get('amenity')
    query_application = request.GET.get('application')
    query_capacity = request.GET.get('capacity')
    query_item_type = request.GET.get('item_type')
    
    print('price_from',price_from)
    print('price_to',price_to)

    if not query:
        query = ''
        print('no query')
    else:
        # if Item.objects.filter(Q(title__icontains=query)):
        #     rentals=Item.objects.filter(Q(title__icontains=query))
        print(query)    
    if price_from == None:
        price_from = 0
    if price_to == None:
        price_to = "10000"
    max_amount = "500000"
    
    sorting = request.GET.get('sorting', '-created_at') 
    variants_id = [] 
    if search_form.is_valid():
        for product in products_list:
            if Variants.objects.filter(product_id=product.id).exists():
                variants_id.append(product.id)      
        products_list,price_from,price_to,brands,weight,width,size,height,colors,length,year,engine,make,item_model = product_service.filter_products(query_brand,products_list,variants_id,sorting=sorting,**search_form.cleaned_data)
        if Item.objects.filter(Q(title__icontains=query)):
            rental_list,price_from,price_to,engine,year,rooms,amenity,application,capacity,item_type=rental_service.filter_rental(rental_list,sorting=sorting,**search_form.cleaned_data)
            
    else:
        print(search_form.errors)          
    search_form = SearchForm(request.GET, products=products_list)
    paginator = Paginator(products_list,3)
    paginator_rentals = Paginator(rental_list,3)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
        rentals = paginator_rentals.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
        rentals = paginator_rentals.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages) 
        rentals = paginator_rentals.page(paginator_rentals.num_pages)  
       
    return render(
        request,
        'product/search.html',
        {
            'form': search_form,
            'query': query,
            'products': products,
            'rentals':rentals,
            'brands':brands,
            'width':width,
            'size':size,
            'height':height,
            'colors':colors,
            'weight':weight,
            'length':length,
            'width':width,
            'size':size,
            'height':height,
            'year':year,
            'make':make,
            'item_model':item_model,
            'engine':engine,
            'rooms':rooms,
            'amenity':amenity,
            'application':application,
            'capacity':capacity,
            'item_type':item_type,
            'sorting': sorting,
            'price_to':re.sub('[\$,]', '', str(price_to)) ,
            'price_from':re.sub('[\$,]', '', str(price_from)) ,
            # 'price_max':re.sub('[\$,]', '', str(price_to+1000)) ,
            # 'price_min':re.sub('[\$,]', '', str(price_from-1000)),
            'query_brand':query_brand,
            'query_color':query_color,
            'query_weight':query_weight,
            'query_height':query_height,
            'query_width':query_width,
            'query_length':query_length,
            'query_year':query_year,
            'query_make':query_make,
            'query_model':query_model,
            'query_engine':query_engine,
            'query_rooms':query_rooms,
            'query_amenity':query_amenity,
            'query_application':query_application,
            'query_capacity':query_capacity,
            'query_item_type':query_item_type,
            'max_amount':max_amount,
            'shopcart':shopcart,
            'subtotal':total,
            'tax':tax,
            'total':grandTotal,
            'wishlist':wishlist,
            'total_compare':total_compare,
        }
    )


def product(request, id, vendor_slug, category_slug, subcategory_slug, subsubcategory_slug, product_slug):
    cart = Cart(request)

    product = get_object_or_404(
        Product,
        category__slug=subsubcategory_slug,
        slug=product_slug,
        slugV=vendor_slug,
        visible=True,
        vendor__enabled=True,
        status=True
    )
    product.num_visits = product.num_visits + 1
    product.last_visit = datetime.now()
    product.save()

    child_with_parent_products = Product.objects.filter(Q(id=product.id))

    if request.method == 'POST':
        cart_form = AddToCartForm(
            request.POST, products=child_with_parent_products)
        
        if cart_form.is_valid():
            form_data = copy(cart_form.cleaned_data)
            print(form_data)
            quantity = form_data.pop('quantity')
            form_data = {k: v for k, v in form_data.items() if v}
            print(form_data)
            if form_data:
                
                purchasing_product = product_service.filter_by_variants(
                    child_with_parent_products, **form_data).first()
            else:
                purchasing_product = product

            if not purchasing_product:
                messages.error(request, 'No such product available')
                return redirect(product.get_url())

            if quantity > purchasing_product.num_available:
                quantity = purchasing_product.num_available

            cart.add(product_id=purchasing_product.id,
                     quantity=quantity, update_quantity=False)

            messages.success(request, 'The product was added to the cart')

            return redirect(
                'product',
                category_slug=category_slug,
                subcategory_slug=subcategory_slug,
                subsubcategory_slug=subsubcategory_slug,
                product_slug=product_slug,
                vendor_slug=vendor_slug,

            )
    else:
        cart_form = AddToCartForm(products=child_with_parent_products)

    review_form = ReviewForm()
    similar_products = list(product.category.products.exclude(id=product.id))

    if len(similar_products) >= 4:
        similar_products = random.sample(similar_products, 4)

    cart = Cart(request)

    if cart.has_product(product.id):
        product.in_cart = True
    else:
        product.in_cart = False
    product_imgs = ProductImage.objects.filter(product=product)
    reviews = Review.objects.filter(
        product=product).prefetch_related('user', 'user__customer')

    wishlist = None
    if not request.user.is_anonymous:
        wishlist = UserWishList.objects.filter(
            user=request.user, product=product).first()

    return render(
        request,
        'product/product.html',
        {
            'form': cart_form,
            'form2': review_form,
            'product': product,
            'child_products': child_with_parent_products,
            'reviews': reviews,
            'wishlist': wishlist,
            'imgs': product_imgs,
            'similar_products': similar_products,
            'is_comparing': product.id in request.session.get('comparing', [])
        }
    )


class CompareView(View):
    def post(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER')  # get last url
        product_id = kwargs['pk']
        product = Product.objects.get(pk=product_id)
        if product.vendor.enabled == False:
            messages.success(request, "Product not available")
            redirect(url)
        
        
        if not request.session.get('comparing'):
            request.session['comparing'] = []

        if not request.session.get('comparing_variants'):
            request.session['comparing_variants'] = []

        if product_id in request.session['comparing']:
            
            request.session['comparing'].remove(product_id)
            messages.warning(
                request, "A product has been removed from comparison.")
            
            return redirect(url)
        
        limit = not 3 <= (request.session['comparing_variants'].__len__(
        ) + request.session['comparing'].__len__())
        if limit:
            request.session['comparing'].append(product_id)
            messages.success(
                request, "A product has been added to comparison.")
        else:
            
            messages.warning(
                request, "You can only compare 3 products maximum.")

        return redirect(url)


def variantCompare(request):
    url = request.META.get('HTTP_REFERER')  # get last url
    if request.method == "POST":
        variantid = request.POST.get('variant_id')
        variant = Variants.objects.get(id=variantid)


        if not request.session.get('comparing'):
            request.session['comparing'] = []

        if not request.session.get('comparing_variants'):
            request.session['comparing_variants'] = []

        if int(variantid) in request.session['comparing_variants']:
            
            request.session['comparing_variants'].remove(int(variantid))
            messages.success(request, "Your item removed to compare list.")
            return redirect(url)
        
        limit = not 3 <= (request.session['comparing_variants'].__len__(
        ) + request.session['comparing'].__len__())
        if limit:
            request.session['comparing_variants'].append(int(variantid))
            messages.success(request, 'Product added to compare')
            return redirect(url)
        else:
            
            messages.success(request, "Your reach compare product limits(3)")
    return redirect(url)


class ComparingView(TemplateView):
    # template_name = 'product/comparing.html'

    def get(self, request, *args, **kwargs):
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

        context = self.get_context_data(**kwargs)
        variants = []
        products = []
        comparing_product_ids = request.session.get('comparing')
        comparing_variant_ids = request.session.get('comparing_variants')
        if comparing_product_ids:
            products = Product.objects.filter(id__in=comparing_product_ids)
        if comparing_variant_ids:
            variants = Variants.objects.filter(id__in=comparing_variant_ids)
        for product in products:
            print(product.id)
        for product in variants:
            print(product.id)
            
        return render(request,'product/comparing.html',
        {
            'products':products,
            'variants':variants,
            'shopcart': shopcart,
            'subtotal': total,
            'tax': tax,
            'total': grandTotal,
            'wishlist': wishlist,
            })



@login_required(login_url='/login')
@never_cache
def deleteCompare(request, id):
    url = request.META.get('HTTP_REFERER')
    request.session['comparing'].remove(id)

    messages.warning(request, "A product has been removed from comparison.")
    return redirect(url)


@login_required(login_url='/login')
@never_cache
def deleteVariantCompare(request, id):
    url = request.META.get('HTTP_REFERER')

    request.session['comparing_variants'].remove(id)

    messages.warning(request, "A product has been removed from comparison.")
    return redirect(url)




class WishListAddView(FormView):
    

    def post(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER')  # get last url
        product = Product.objects.get(pk=kwargs['pk'])

        if product.vendor.enabled == False:
            messages.success(request, "Product not available")
            redirect(url)

        try:
            request.user.customer
        except:
            return self.redirect(product)
        
        is_already_in_wishlist = UserWishList.objects.filter(
            user=request.user, product=product)
        
        if is_already_in_wishlist:
            UserWishList.objects.filter(
                user=request.user, product=product).delete()
            messages.warning(
                request, "A product has been removed from your wishlist.")
        else:
            UserWishList.objects.create(
                user=request.user, is_variant=False, product=product)
            messages.success(
                request, "A product has been added to your wishlist.")

        return redirect(url)


class WishlistAddVariant(FormView):
    def post(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER')  # get last url
        if request.method == "POST":
            variantid = request.POST.get('variant_id')
            productid = request.POST.get('product_id')
            variant = Variants.objects.get(pk=variantid)
            product = Product.objects.get(id=productid)

            if product.vendor.enabled == False:
                messages.success(request, "Product not available")
                redirect(url)
            try:
                request.user.customer

            except:
                return self.redirect(variant)
            is_already_in_wishlist = UserWishList.objects.filter(
                user=request.user, variant=variant)
            if is_already_in_wishlist:
                UserWishList.objects.filter(
                    user=request.user, variant=variant).delete()
                messages.warning(
                    request, "A product has been removed from your wishlist.")
            else:
                UserWishList.objects.create(
                    user=request.user, is_variant=True, product=product, variant=variant)
                print(UserWishList.objects.filter(
                    user=request.user, variant=variant))
                messages.success(
                    request, "A product has been added to your wishlist.")

        return redirect(url)


def wishlistDelete(request, id):
    url = request.META.get('HTTP_REFERER')
    UserWishList.objects.filter(user=request.user, id=id).delete()
    messages.warning(
        request, "An product has been removed from your wishlist.")
    return redirect(url)


class CollectionView(TemplateView):
    template_name = 'product/collection.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        collection = Collection.objects.get(pk=kwargs['pk'])
        context['collection'] = collection
        context['products'] = collection.products.all()
        return self.render_to_response(context)


def category(request, category_slug):
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

    category = get_object_or_404(Category, slug=category_slug)
    category_name = str(category)

    products_list = Product.objects.filter(visible=True,status=True)

    brands = Brand.objects.all()
    colors = Color.objects.all()
    weight = Weight.objects.all()
    length = Length.objects.all()
    width = Width.objects.all()
    size = Size.objects.all()
    height = Height.objects.all()

    if request.method == 'POST':
        cart = Cart(request)

        form = AddToCartInListForm(request.POST)

        if form.is_valid():
            product_slug = form.cleaned_data['slug']

            product = get_object_or_404(
                Product, category__sub_category__category__slug=category_slug, slug=product_slug)
            product.num_visits = product.num_visits + 1
            product.last_visit = datetime.now()
            product.save()

            cart.add(product_id=product.id, quantity=1, update_quantity=False)

            messages.success(request, 'The product was added to the cart')

            return redirect('category', category_slug=category_slug)

    search_form = SearchForm(request.GET)
    brands=Brand.objects.all()
    colors=Color.objects.all()
    weight=Weight.objects.all()
    length=Length.objects.all()
    width=Width.objects.all()
    size=Size.objects.all()
    height=Height.objects.all()
    year = Year.objects.all()
    make = Make.objects.all()
    item_model = Item_Model.objects.all()
    engine = Engine.objects.all()

    query=request.GET.get('query')
    price_to=request.GET.get('price_to')
    price_from=request.GET.get('price_from')
    query_brand=request.GET.getlist('brand')
    query_color=request.GET.getlist('color')
    query_weight=request.GET.getlist('weight')
    query_height=request.GET.getlist('height')
    query_width=request.GET.getlist('width')
    query_length=request.GET.getlist('length')
    query_year = request.GET.getlist('year')
    query_make = request.GET.getlist('make')
    query_model = request.GET.getlist('model')
    query_engine = request.GET.getlist('engine')

    print('price_from',price_from)
    print('price_to',price_to)

    if not query:
        query = ''
    if price_from == None:
        price_from = 0
    if price_to == None:
        price_to = "10000"
    max_amount = "500000"
    
    sorting = request.GET.get('sorting', '-created_at')
    
    products_ids = []
    
    for subcategory in category.subcategory.all():
        for subsubcategory in subcategory.subsubcategory.all():
            products_ids.extend(
                subsubcategory.product.all().values_list('id', flat=True))
            
    products_list = Product.objects.filter(id__in=products_ids, visible=True, vendor__enabled=True,status=True)
    rental_list = Item.objects.filter(review=True,visible=True)
    variants_id = []
    if search_form.is_valid():
        for product in products_list:
            if Variants.objects.filter(product_id=product.id).exists():
                variants_id.append(product.id)
        products_list,price_from,price_to,brands,weight,width,size,height,colors,length,year,engine,make,item_model = product_service.filter_products(query_brand,products_list,variants_id,sorting=sorting, **search_form.cleaned_data)
           
    else:
        print(search_form.errors)
    
    paginator = Paginator(products_list,6)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    search_form = SearchForm(request.GET, products=products_list)
    return render(
        request,
        'product/category.html',
        {
            'category': category_slug,
            'category_name':category_name,
            'query':query,
            'form': search_form,
            'query':query,
            'products': products,
            'brands':brands,
            'width':width,
            'size':size,
            'height':height,
            'colors':colors,
            'weight':weight,
            'width':width,
            'length':length,
            'size':size,
            'height':height,
            'year':year,
            'make':make,
            'item_model':item_model,
            'engine':engine,
            'sorting': sorting,
            'price_to':re.sub('[\$,]', '', str(price_to)) ,
            'price_from':re.sub('[\$,]', '', str(price_from)) ,
            # 'price_max':re.sub('[\$,]', '', str(price_to+1000)) ,
            # 'price_min':re.sub('[\$,]', '', str(price_from-1000)),
            'query_brand':query_brand,
            'query_color':query_color,
            'query_weight':query_weight,
            'query_height':query_height,
            'query_width':query_width,
            'query_length':query_length,
            'query_year':query_year,
            'query_make':query_make,
            'query_model':query_model,
            'query_engine':query_engine,
            'max_amount':max_amount,
            'shopcart': shopcart,
            'subtotal': total,
            'tax': tax,
            'total': grandTotal,
            'wishlist': wishlist,
            'total_compare': total_compare
        }
    )


def subcategory(request, category_slug, subcategory_slug):
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

    category = get_object_or_404(SubCategory, slug=subcategory_slug)
    sub_category=SubSubCategory.objects.filter(sub_category=category).first()
    sub_category_name=str(category)
    products_list = Product.objects.filter(visible=True,category=sub_category,status=True)
    rental_list = Item.objects.filter(review=True,visible=True)
    for product in products_list:
        variants = Variants.objects.filter(product=product)
    brands = Brand.objects.all()
    colors = Color.objects.all()
    weight = Weight.objects.all()
    length = Length.objects.all()
    width = Width.objects.all()
    size = Size.objects.all()
    height = Height.objects.all()

    if request.method == 'POST':
        cart = Cart(request)

        form = AddToCartInListForm(request.POST)

        if form.is_valid():
            product_slug = form.cleaned_data['slug']

            product = get_object_or_404(
                Product, category__sub_category__slug=subcategory_slug, slug=product_slug, status=True)
            product.num_visits = product.num_visits + 1
            product.last_visit = datetime.now()
            product.save()

            cart.add(product_id=product.id, quantity=1, update_quantity=False)

            messages.success(request, 'The product was added to the cart')

            return redirect('subcategory', category_slug=category_slug, subcategory_slug=subcategory_slug)

    search_form = SearchForm(request.GET)
    brands=Brand.objects.all()
    colors=Color.objects.all()
    weight=Weight.objects.all()
    length=Length.objects.all()
    width=Width.objects.all()
    size=Size.objects.all()
    height=Height.objects.all()

    year = Year.objects.all()
    make = Make.objects.all()
    item_model = Item_Model.objects.all()
    engine = Engine.objects.all()

    query=request.GET.get('query')
    price_to=request.GET.get('price_to')
    price_from=request.GET.get('price_from')
    query_brand=request.GET.getlist('brand')
    query_color=request.GET.getlist('color')
    query_weight=request.GET.getlist('weight')
    query_height=request.GET.getlist('height')
    query_width=request.GET.getlist('width')
    query_length=request.GET.getlist('length')

    query_year = request.GET.get('year')
    query_make = request.GET.get('make')
    query_model = request.GET.get('model')
    query_engine = request.GET.get('engine')


    if not query:
        query = ''
    if price_from == None:
        price_from = 0
    if price_to == None:
        price_to = "10000"
    max_amount = "500000"

    sorting = request.GET.get('sorting', '-created_at')

    variants_id = []
    if search_form.is_valid():
        for product in products_list:
            if Variants.objects.filter(product_id=product.id).exists():
                variants_id.append(product.id)
        products_list,price_from,price_to,brands,weight,width,size,height,colors,length,year,make,engine,item_model = product_service.filter_products(query_brand,products_list,variants_id,sorting=sorting, **search_form.cleaned_data)

        paginator = Paginator(products_list,6) 
        page = request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
    else:
        print(search_form.errors)
    search_form = SearchForm(request.GET, products=products)
    return render(request, 'product/subcategory.html',
        {
            'category': category_slug,
            'subcategory':subcategory_slug,
            'sub_category_name':sub_category_name,
            'form': search_form,
            'query':query,
            'products': products,
            'brands':brands,
            'width':width,
            'size':size,
            'height':height,
            'colors':colors,
            'weight':weight,
            'length':length,
            'year':year,
            'make':make,
            'item_model':item_model,
            'engine':engine,
            'sorting': sorting,
            'price_to':re.sub('[\$,]', '', str(price_to)) ,
            'price_from':re.sub('[\$,]', '', str(price_from)) ,
            # 'price_max':re.sub('[\$,]', '', str(price_to+1000)) ,
            # 'price_min':re.sub('[\$,]', '', str(price_from-1000)),
            'query_brand':query_brand,
            'query_color':query_color,
            'query_weight':query_weight,
            'query_height':query_height,
            'query_width':query_width,
            'query_length':query_length,
            'query_year':query_year,
            'query_make':query_make,
            'query_model':query_model,
            'query_engine':query_engine,
            'max_amount':max_amount,
            'shopcart': shopcart,
            'subtotal': total,
            'tax': tax,
            'total': grandTotal,
            'wishlist': wishlist,
            'total_compare': total_compare
        }
    )


def subsubcategory(request, category_slug, subcategory_slug, subsubcategory_slug):
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

    category = get_object_or_404(SubSubCategory, slug=subsubcategory_slug)
    sub_sub_category_name = str(category)
    products_list = Product.objects.filter(visible=True,category=category,status=True)
    rental_list = Item.objects.filter(review=True,visible=True)
    for product in products_list:
        variants = Variants.objects.filter(product=product)

    brands = Brand.objects.all()
    colors = Color.objects.all()
    weight = Weight.objects.all()
    length = Length.objects.all()
    width = Width.objects.all()
    size = Size.objects.all()
    height = Height.objects.all()

    if request.method == 'POST':
        cart = Cart(request)

        form = AddToCartInListForm(request.POST)

        if form.is_valid():
            product_slug = form.cleaned_data['slug']

            product = get_object_or_404(
                Product, category__slug=subsubcategory_slug, slug=product_slug, status=True)
            product.num_visits = product.num_visits + 1
            product.last_visit = datetime.now()
            product.save()

            cart.add(product_id=product.id, quantity=1, update_quantity=False)

            messages.success(request, 'The product was added to the cart')

            return redirect('subsubcategory', category_slug=category_slug, subcategory_slug=subcategory_slug, subsubcategory_slug=subsubcategory_slug)

    search_form = SearchForm(request.GET)
    brands=Brand.objects.all()
    colors=Color.objects.all()
    weight=Weight.objects.all()
    length=Length.objects.all()
    width=Width.objects.all()
    size=Size.objects.all()
    height=Height.objects.all()

    year = Year.objects.all()
    make = Make.objects.all()
    item_model = Item_Model.objects.all()
    engine = Engine.objects.all()

    query=request.GET.get('query')
    price_to=request.GET.get('price_to')
    price_from=request.GET.get('price_from')
    query_brand=request.GET.getlist('brand')
    query_color=request.GET.getlist('color')
    query_weight=request.GET.getlist('weight')
    query_height=request.GET.getlist('height')
    query_width=request.GET.getlist('width')
    query_length=request.GET.getlist('length')

    query_year = request.GET.get('year')
    query_make = request.GET.get('make')
    query_model = request.GET.get('model')
    query_engine = request.GET.get('engine')

    if not query:
        query = ''
    if price_from == None:
        price_from = 0
    if price_to == None:
        price_to = "10000"
    max_amount = "500000"

    sorting = request.GET.get('sorting', '-created_at')
    variants_id = []
    if search_form.is_valid():
        for product in products_list:
            if Variants.objects.filter(product_id=product.id).exists():
                variants_id.append(product.id)
        products_list,price_from,price_to,brands,weight,width,size,height,colors,length,year,engine,make,item_model = product_service.filter_products(query_brand,products_list,variants_id,sorting=sorting, **search_form.cleaned_data)
        
        paginator = Paginator(products_list,6) 
        page = request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
    else:
        print(search_form.errors)
    search_form = SearchForm(request.GET, products=products)

    return render(request, 'product/subsubcategory.html',
        {
            'category': category_slug,
            'subcategory':subcategory_slug,
            'subsubcategory':subsubcategory_slug,
            'sub_sub_category_name':sub_sub_category_name,
            'form': search_form,
            'query':query,
            'products': products,
            'brands':brands,
            'width':width,
            'size':size,
            'height':height,
            'colors':colors,
            'weight':weight,
            'length':length,
            'width':width,
            'size':size,
            'height':height,
            'year':year,
            'make':make,
            'item_model':item_model,
            'engine':engine,
            'sorting': sorting,
            'price_to':re.sub('[\$,]', '', str(price_to)) ,
            'price_from':re.sub('[\$,]', '', str(price_from)) ,
            # 'price_max':re.sub('[\$,]', '', str(price_to+1000)) ,
            # 'price_min':re.sub('[\$,]', '', str(price_from-1000)),
            'query_brand':query_brand,
            'query_color':query_color,
            'query_weight':query_weight,
            'query_height':query_height,
            'query_width':query_width,
            'query_length':query_length,
            'query_year':query_year,
            'query_make':query_make,
            'query_model':query_model,
            'query_engine':query_engine,
            'max_amount':max_amount,
            'shopcart':shopcart,
            'subtotal':total,
            'tax':tax,
            'total':grandTotal,
            'wishlist':wishlist,
            'total_compare':total_compare,
        }
    )

def brands(request):
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

    brands_list=Brand.objects.all().order_by('brand')
    paginator = Paginator(brands_list,6) 
    page = request.GET.get('page')

    try:
        brands = paginator.page(page)
    except PageNotAnInteger:
        brands = paginator.page(1)
    except EmptyPage:
        brands = paginator.page(paginator.num_pages)

    return render(request,'product/brands.html',
    {
    'brands':brands,
    'shopcart': shopcart,
    'subtotal': total,
    'tax': tax,
    'total': grandTotal,
    'wishlist': wishlist,
    'total_compare': total_compare
    })    