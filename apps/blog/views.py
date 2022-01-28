from django.shortcuts import render

from . models import Post
from apps.cart.cart import Cart
from apps.ordering.models import ShopCart


def index(request):
    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        # cart.clear()
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total=cart.get_cart_cost()
        tax=cart.get_cart_tax()
        grandTotal=cart.get_cart_cost() + cart.get_cart_tax()

    else:
        cart = 0
        subtotal = 0
        tax = 0
        total = 0
        grandTotal = 0
        shopcart = None    

    posts = Post.objects.all()

    return render(request, 'blog/index.html', {
    'posts': posts,
    'shopcart':shopcart,
    'subtotal':total,
    'tax':tax,
    'total':grandTotal
    })


def detail(request, slug):
    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        # cart.clear()
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total=cart.get_cart_cost()
        tax=cart.get_cart_tax()
        grandTotal=cart.get_cart_cost() + cart.get_cart_tax()
        
    else:
        cart = 0
        subtotal = 0
        tax = 0
        total = 0
        grandTotal = 0
        shopcart = None

    post = Post.objects.get(slug=slug)

    return render(request, 'blog/detail.html', {
    'post': post,
    'shopcart':shopcart,
    'subtotal':total,
    'tax':tax,
    'total':grandTotal
    })
