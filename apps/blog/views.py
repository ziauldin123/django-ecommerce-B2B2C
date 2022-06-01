from multiprocessing import context
from django.shortcuts import get_object_or_404, render
from taggit.models import Tag
from . models import Post
from apps.cart.cart import Cart
from apps.ordering.models import ShopCart
from apps.vendor.models import UserWishList
from django.core.paginator import (PageNotAnInteger, Paginator, EmptyPage)

def index(request):
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

    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, 5)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/index.html', {
        'posts': posts,
        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
    })

detail_template='blog/detail.html'
def detail(request, id):
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

    post = Post.objects.get(id=id)
    
    return render(request, detail_template, {
        'post': post,
        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
    })

def tagged(request,slug):
    tag = get_object_or_404(Tag,slug=slug)
    post = Post.objects.get(tags=tag)

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

    return render(request,'blog/detail.html',
                  {
                      'shopcart': shopcart,
                      'subtotal': total,
                      'tax': tax,
                      'total': grandTotal,
                      'wishlist': wishlist,
                      'total_compare': total_compare,
                      'post':post,
                      'tags':tag
                  })