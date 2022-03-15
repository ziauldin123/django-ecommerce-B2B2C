from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.query import RawQuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from apps.cart.cart import Cart
from django.utils.crypto import get_random_string
from apps.ordering.models import ShopCart, ShopCartForm, Order, OrderItem
from apps.newProduct.models import Category, Product, Variants
from apps.vendor.models import Customer, Profile, UserWishList
from apps.cart.models import District, Sector, Cell, Village
from decimal import Decimal
from django.views.decorators.cache import never_cache, cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@never_cache
def index(request):
    return HttpResponse("Order Page")


@login_required(login_url='/login')  # check login
@never_cache
@csrf_exempt
def addtoshopcart(request, id):
    cart = Cart(request)
    url = request.META.get('HTTP_REFERER')  # get last url
    current_user = request.user  # Access User Session infor
    product = Product.objects.get(pk=id)
    variantid = request.POST.get('variantid')
    

    if product.vendor.enabled != True:
        messages.success(request, 'Product not available')
        return redirect(url)

    customer = Customer.objects.filter(email=current_user)
    print("variant id", variantid)

    if product.is_variant:
        # get variant object
        # from variant add to cart
        checkinvariant = ShopCart.objects.filter(
            variant_id=variantid, user=current_user)  # check product from cart
        if checkinvariant:
            control = 1  # product is in cart
        else:
            control = 0  # product is not in cart
    else:
        # No Variant
        variant = None
        checkinproduct = ShopCart.objects.filter(
            product_id=id, user_id=current_user)  # check product in cart
        if checkinproduct:
            control = 1  # product is in cart
        else:
            control = 0  # product is not in cart

    if request.method == 'POST':  # if there is a post
        print("control", control)
        p_quantity = int(request.POST.get('quantity'))

        if control == 1:  # update shopcart

            if product.variant == 'None':
                data = ShopCart.objects.get(
                    product_id=id, user_id=current_user)
                data.quantity += p_quantity
                data.save()  # save data
                cart.add(product_id=id, variant_id=None, user_id=current_user.id,
                         quantity=p_quantity, update_quantity=True)
            else:
                variant = Variants.objects.get(id=variantid)
                data = ShopCart.objects.get(
                    variant_id=variantid, user_id=current_user.id)
                data.quantity += p_quantity
                data.save()  # save data
                cart.add(product_id=id, variant_id=variantid,
                         user_id=current_user.id, quantity=p_quantity, update_quantity=True)

        else:  # insert to shopcart
            data = ShopCart()
            if product.variant != 'None':
                variant = Variants.objects.get(id=variantid)
                data.variant = variant
                data.variant_id = variantid
            data.user = current_user
            data.product = product
            data.quantity = p_quantity
            data.save()
            
            cart.add(product_id=id, variant_id=variantid,
                     user_id=current_user.id, quantity=p_quantity, update_quantity=True)

        messages.success(request, "Product added to Shopcart")
        return HttpResponse("Success!")

    else:  # if there is no post
        if control == 1:
            print("get 1")
            data = ShopCart.objects.get(product_id=id, user_id=current_user.id)
            data.quantity += 1
            data.save()
            cart.add(product_id=product.id, variant_id=None, quantity=1,
                     update_quantity=True, user_id=current_user.id)
        else:  # insert to shopcart
            print("get")
            data = ShopCart.objects.create(
                user_id=current_user.id,
                product_id=id,
                quantity=1,
                variant_id=None,
            )
            cart.add(product_id=product.id, variant_id=None, quantity=1,
                     update_quantity=True, user_id=current_user.id)
        messages.success(request, 'Product added to Shopcart')
        return HttpResponse("Success!")


@never_cache
def shopcart(request):
    category = Category.objects.all()
    current_user = request.user
    cart = Cart(request)
    
    if request.user.is_anonymous:
        messages.info(request,"Please login to view your Cart")
        return redirect('/')

    if request.method == 'POST':
        if request.user.is_authenticated:
            if "id_quantity" in request.POST:
                print("coupon code = ", request.POST["coupon_code"])
                print("coupon value = ", request.POST["coupon_discount"])
                coupon_code = request.POST["coupon_code"]
                coupon_discount = request.POST["coupon_discount"]
                if coupon_discount == "":
                    coupon_code = ""

                coupon = request.session.get(settings.COUPON_SESSION_ID)
                if not coupon:
                    coupon = request.session[settings.COUPON_SESSION_ID] = {}
                coupon["code"] = coupon_code
                coupon["discount"] = coupon_discount
                request.session[settings.COUPON_SESSION_ID] = coupon
                request.session.modified = True
                for elem in request.POST["id_quantity"].split(":"):
                    elem_id = elem.split("_")[0]
                    elem_quantity = elem.split("_")[1]
                    cart.set(elem_id, elem_quantity)

                return redirect('contact_info')
        else:
            messages.success(request, 'Please sign in')
            return redirect('login')

    if not request.user.is_anonymous:
        wishlist = UserWishList.objects.filter(user=current_user)
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

        context = {'shopcart': shopcart,
                   'category': category,
                   'subtotal': round(total, 2),
                   'tax': tax,
                   'grandTotal': grandTotal,
                   'wishlist': wishlist,
                   'total_compare': total_compare
                   }
    else:
        context = {'shopcart': None,
                   'category': None,
                   'total': None,
                   'tax': None,
                   'grandTotal': None,
                   'wishlist': 0,
                   'total_compare': 0
                   }          
    return render(request, 'shopcart_products.html', context)


@login_required(login_url='/login')
@never_cache
def deletefromcart(request,id):
    url=request.META.get('HTTP_REFERER')
    cart=Cart(request)

    shopcart = ShopCart.objects.get(id=id)

    cart.delete_product(shopcart.id)

    ShopCart.objects.filter(id=id).delete()

    messages.success(request, "Your item deleted form Shopcart.")
    return HttpResponseRedirect(url)


@csrf_exempt
@never_cache
def update(request):
    cart_data = Cart(request)
    if request.method == "POST":
        prod_id = int(request.POST.get('product_id'))
        if(ShopCart.objects.filter(user=request.user, id=prod_id)):
            prod_qty = int(request.POST.get('product_qty'))
            cart = ShopCart.objects.get(id=prod_id, user=request.user)
            cart.quantity = prod_qty
            cart.save()

            if cart.product.is_variant:
                cart_data.add(product_id=cart.product.id, variant_id=cart.variant.id,
                              user_id=request.user.id, quantity=prod_qty, update_quantity=True)
            else:
                cart_data.add(product_id=cart.product.id, variant_id=None,
                              user_id=request.user.id, quantity=prod_qty, update_quantity=True)
            return JsonResponse({'status': "Updated"})

    return redirect('/')
