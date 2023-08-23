import imp
from django.contrib.sitemaps import Sitemap
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, request
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
# Create your views here.
from django.template.loader import render_to_string
from datetime import datetime
import random
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from apps.cart.cart import Cart
from apps.ordering.models import ShopCart

from apps.newProduct.models import Category, Comment, Product, SubCategory, SubSubCategory, Images, Comment, Variants
from apps.vendor.models import UserWishList, Customer
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
# Create your views here.


def index(request):
    products_latest = Product.objects.filter()[0:4]
    products_slider = Product.objects.all().order_by('id')[:4]
    product_picked = Product.objects.all().order_by('-last_visit')[0:4]
    product_popular = Product.objects.all().order_by('-num_visits')[0:4]

    context = {
        'products_latest': products_latest,
        'products_slider': products_slider,
        'product_picked': product_picked,
        'product_popular': product_popular
    }
    return render(request, 'index.html', context)


def product_detail(request, id, slug, vendor_slug, category_slug, subcategory_slug, subsubcategory_slug):
    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = UserWishList.objects.filter(user=current_user)
        # cart.clear()
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total = cart.get_cart_cost()
        tax = cart.get_cart_tax()
        grandTotal = cart.get_cart_cost
        if not request.session.get('comparing'):
            comparing = 0
        else:
            comparing = request.session['comparing'].__len__()

        if not request.session.get('comparing_variants'):
            compare_var = 0
        else:
            compare_var = request.session['comparing_variants'].__len__()

        total_compare = comparing + compare_var

    query = request.GET.get('q')
    mainProduct = []
    query = request.GET.get('q')
    product = Product.objects.get(pk=id)
    max = product.product.all().aggregate(Max('rate'))
    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total = cart.get_cart_cost()
        tax = cart.get_cart_tax()
        grandTotal = cart.get_cart_cost()

    else:
        cart = 0
        subtotal = 0
        tax = 0
        total = 0
        grandTotal = 0
        shopcart = None
        wishlist = 0
        total_compare = 0


    if product.status == False:
        messages.add_message(request, messages.ERROR,
                             "Product is not available")
        return redirect('/')

    if product.vendor.enabled == False:
        messages.add_message(request, messages.ERROR,
                             "Product is not available")
        return redirect('/')

    variant = Variants.objects.filter(product_id=id, status=True, visible=True)
    category = Category.objects.all()
    subcategory = SubCategory.objects.all()
    subsubCategory = SubSubCategory.objects.all()
    slugV = vendor_slug,
    images = Images.objects.filter(product_id=id)
    product.num_visits = product.num_visits + 1
    product.last_visit = datetime.now()
    username = request.user
    customer = Customer.objects.filter(email=username)
    similar_products = list(product.category.product.exclude(id=product.id))

    if len(similar_products) >= 4:
        similar_products = random.sample(similar_products, 4)

    comments_list = Comment.objects.filter(product_id=id, status='True')
    paginator = Paginator(comments_list, 2)
    page = request.GET.get('page')

    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    product.save()
    context = {'product': product, 'category': category,
               'subcategory': subcategory, 'subsubCategory': subsubCategory,
               'images': images, 'vendor_slug': slugV, 'similar_products': similar_products,
               'comments': comments,
               'mainProduct': mainProduct,
               'customer': customer,
               'is_comparing': product.id in request.session.get('comparing', []),
               'shopcart': shopcart,
               'subtotal': total,
               'tax': tax,
               'total': grandTotal,
               'wishlist': wishlist,
               'total_compare': total_compare,
               'max': max
               }
    if product.variant != "None":  # pr has variantsu
        if request.method == 'POST':  # if we select color
            variant_id = request.POST.get('variantid')
            variant = Variants.objects.get(
                id=variant_id, status=True, visible=True)  # selected product by color
            colors = Variants.objects.filter(
                product_id=id, size_id=variant.size_id, status=True, visible=True)
            colors1 = Variants.objects.filter(
                product_id=id, weight_id=variant.weight_id, status=True, visible=True)
            sizes = Variants.objects.raw(
                'SELECT * FROM newProduct_variants WHERE product_id=%s AND status=True AND visible=True GROUP BY size_id', [id])
            weight = Variants.objects.raw(
                'SELECT * FROM newProduct_variants WHERE product_id=%s AND status=True AND visible=True  GROUP BY weight_id', [id])
            length = Variants.objects.raw(
                'SELECT * FROM newProduct_variants WHERE product_id=%s AND status=True AND visible=True  GROUP BY length_id', [id])
            width = Variants.objects.raw(
                'SELECT * FROM newProduct_variants WHERE product_id=%s AND status=True AND visible=True  GROUP BY width_id', [id])
            height = Variants.objects.raw(
                'SELECT * FROM newProduct_variants WHERE product_id=%s AND status=True AND visible=True  GROUP BY height_id', [id])
            # query +=variant.title+' Size:' +str(variant.size) +' Color:' +str(variant.color) +' Weight:' +str(variant.weight)+' length:' +str(variant.length)+' Width:' +str(variant.width)
        else:
            variants = Variants.objects.filter(
                product_id=id, status=True, visible=True)
            colors = Variants.objects.filter(
                product_id=id, size_id=variants[0].size_id, status=True, visible=True)
            colors1 = Variants.objects.filter(
                product_id=id, weight_id=variants[0].weight_id, status=True, visible=True)
            sizes = Variants.objects.raw(
                'SELECT * FROM  newProduct_variants  WHERE product_id=%s AND status=True AND visible=True  GROUP BY size_id', [id])
            weight = Variants.objects.raw(
                'SELECT * FROM newProduct_variants WHERE product_id=%s AND status=True AND visible=True  GROUP BY weight_id', [id])
            length = Variants.objects.raw(
                'SELECT * FROM newProduct_variants WHERE product_id=%s AND status=True AND visible=True  GROUP BY length_id', [id])
            width = Variants.objects.raw(
                'SELECT * FROM newProduct_variants WHERE product_id=%s AND status=True AND visible=True GROUP BY width_id', [id])
            height = Variants.objects.raw(
                'SELECT * FROM newProduct_variants WHERE product_id=%s AND status=True AND visible=True GROUP BY height_id', [id])
            variant = Variants.objects.get(
                id=variants[0].id, status=True, visible=True)

        context.update({'sizes': sizes, 'colors': colors, 'colors1': colors1, 'weight': weight, 'width': width, 'length': length, 'height': height, 'variant': variant, 'query': query,
                        'is_comparing': variant.id in request.session.get('comparing', []),
                        'shopcart': shopcart, 'subtotal': total, 'tax': tax, 'total': grandTotal})
    return render(request, 'product_detail.html', context)


def ajaxcolor(request):
    data = {}
    if request.POST.get('action') == 'post':
        size_id = request.POST.get('size')
        productid = request.POST.get('productid')
        colors = Variants.objects.filter(product_id=productid, size_id=size_id)
        context = {
            'size_id': size_id,
            'productid': productid,
            'colors': colors,
        }
        data = {'rendered_table': render_to_string(
            'color_list.html', context=context)}
        return JsonResponse(data)
    return JsonResponse(data)


def ajaxcolorWeigth(request):
    data = {}
    if request.POST.get('action') == 'post':
        weight_id = request.POST.get('weigth')
        productid = request.POST.get('productid')
        colors = Variants.objects.filter(
            product_id=productid, weight_id=weight_id)
        context = {
            'weight_id': weight_id,
            'productid': productid,
            'colors': colors,
        }
        data = {'rendered_table': render_to_string(
            'color_list.html', context=context)}
        return JsonResponse(data)
    return JsonResponse(data)
