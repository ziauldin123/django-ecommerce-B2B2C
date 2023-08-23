import re
from tkinter.messagebox import NO
from django.http import HttpResponse
from django.http import request
from django.shortcuts import render
from apps.cart.cart import Cart
from apps.ordering.models import ShopCart
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from apps.newProduct.models import Product, Category, SubCategory, SubSubCategory, Variants
from apps.blog.models import Post
from apps.ordering.models import ShopCart
from apps.vendor.models import UserWishList, Vendor


def frontpage(request):
    current_user = request.user
    variants = Variants.objects.filter(status=True)
    product = Product.objects.filter(status=True, visible=True)
    posts = Post.objects.all()

    if product:
        for i in product:
            if i.is_variant:
                var = i.get_variant
            else:
                var = []
    else:
        var = []

    newest_products = Product.objects.filter(
        status=True, visible=True).order_by('-id')[:4]
    featured_products = Product.objects.filter(
        status=True, visible=True, is_featured=True)[0:8]
    featured_categories = Category.objects.filter(is_featured=True)
    featured_categories_products = []
    for category in featured_categories:
        for sub_category in SubCategory.objects.filter(category=category):
            for subsubcategory in SubSubCategory.objects.filter(sub_category=sub_category):
                for product in Product.objects.filter(category=subsubcategory):
                    if product.vendor.enabled and product.visible:
                        if len(featured_categories_products) == 4:
                            break
                        featured_categories_products.append(product)

    popular_products = Product.objects.filter(
        status=True, visible=True).order_by('-num_visits')[0:4]
    recently_viewed_products = Product.objects.filter(status=True, visible=True).order_by(
        '-last_visit')[0:5]
    
    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = UserWishList.objects.filter(user=current_user)
        # cart.clear()
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total = cart.get_cart_cost()
        if cart.__len__() == 0:
            for rs in shopcart:
                if rs.variant is None:
                    cart.add(product_id=rs.product.id, variant_id=None, user_id=current_user.id,
                             quantity=rs.quantity, update_quantity=True)
                else:
                    cart.add(product_id=rs.product.id, variant_id=rs.variant.id, user_id=current_user.id,
                             quantity=rs.quantity, update_quantity=True)
                             

        if not request.session.get('comparing'):
            comparing = 0
        else:
            comparing = request.session['comparing'].__len__()

        if not request.session.get('comparing_variants'):
            compare_var = 0
        else:
            compare_var = request.session['comparing_variants'].__len__()

        total_compare = comparing + compare_var
        print(total) 

    else:
        cart = 0
        total = 0
        wishlist = 0
        total_compare = 0
        shopcart = []
   

    return render(
        request,
        'core/frontpage.html',
        {
            'newest_products': newest_products,
            'featured_products': featured_products,
            'featured_categories': featured_categories,
            'popular_products': popular_products,
            'recently_viewed_products': recently_viewed_products,
            'featured_categories_products': featured_categories_products,
            'variants': variants,
            'var': var,
            'posts': posts,
            'cart': cart,
            'shopcart': shopcart,
            'subtotal': total,
            'wishlist': wishlist,
            'total_compare': total_compare
        }
    )


def contact(request):
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

    if request.method == 'POST':
        name = request.POST.get('full-name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        from_email = settings.DEFAULT_EMAIL_FROM

        data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            "from_email": from_email,
        }
        message = '''
        New message: {}

        From: {}
        '''.format(data['message'], data['email'])
        send_mail(subject, message, from_email, ['info@sokopark.com'])

        messages.success(
            request, ('Your message has been sent. We will get back to you as quickly as possible. Thank you.'))

    return render(request, 'core/contact.html',
                  {
                      'shopcart': shopcart,
                      'subtotal': total,
                      'tax': tax,
                      'total': grandTotal,
                      'wishlist': wishlist,
                      'total_compare': total_compare
                  })


def about(request):
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

    return render(request, 'core/about.html',
                  {

                      'shopcart': shopcart,
                      'subtotal': total,
                      'tax': tax,
                      'total': grandTotal,
                      'wishlist': wishlist,
                      'total_compare': total_compare
                  })


def pricing(request):
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

    return render(request, 'core/pricing.html',
                  {

                      'shopcart': shopcart,
                      'subtotal': total,
                      'tax': tax,
                      'total': grandTotal,
                      'wishlist': wishlist,
                      'total_compare': total_compare
                  })


def frequently_asked_questions(request):
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

    return render(request, 'core/frequently_asked_questions.html', {

        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
    })


def termsandconditions(request):
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

    return render(request, 'core/termsandconditions.html',
                  {

                      'shopcart': shopcart,
                      'subtotal': total,
                      'tax': tax,
                      'total': grandTotal,
                      'wishlist': wishlist,
                      'total_compare': total_compare
                  })


def privacy_policy(request):
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

    return render(request, 'core/privacy_policy.html', {

        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
    })


def sitemap(request):
    product = Product.objects.filter(status=True, visible=True)
    vendors = Vendor.objects.filter(enabled=True)
    category = Category.objects.all()
    posts = Post.objects.all()
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

    return render(request, 'parts/sitemaps.html', {
        'product': product,
        'category': category,
        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'posts': posts,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare,
        'vendors': vendors
    })


def error_404_view(request, exception):
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

    return render(request, 'core/404.html', {

        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
    })


def vendor_guidelines(request,):
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

    return render(request, 'core/vendor_guidelines.html', {

        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
    })
