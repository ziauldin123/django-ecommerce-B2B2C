from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template

import datetime

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count, Min, Sum, Value
from django.db.models.functions import Concat
# from .forms import AddToCartForm, AddToCartInListForm
# from .models import Category, SubCategory, SubSubCategory, Product
from apps.ordering.models import Order
from apps.vendor.models import Vendor, Customer
from apps.newProduct.models import Product

from apps.cart.cart import Cart


@login_required(login_url="/login/")
def index(request):

    context = {}
    context['segment'] = 'index'

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def changeOrderStatus(request, id, val):
    Order.objects.filter(id=id).update(status=val)
    return HttpResponse("")


@login_required(login_url="/login/")
def changeVendorEnalbed(request, id, val):
    Vendor.objects.filter(id=id).update(enabled=val)
    return HttpResponse("")


@login_required(login_url="/login/")
def changeProductVisible(request, id, val):
    print(id, val)
    Product.objects.filter(id=id).update(visible=val)
    return HttpResponse("")


@login_required(login_url="/login/")
def changeProductLimit(request, id, val):
    print(id, val)
    Vendor.objects.filter(id=id).update(products_limit=val)
    return HttpResponse("")


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        if load_template == "order":
            print("orders")
            load_template = "orders"
            context = page_orders(request)
        elif load_template == "vendors":
            context = page_vendors(request)
        elif load_template == "customers":
            context = page_customers(request)
        elif load_template == "product_review":
            context = page_product_review(request)
        elif load_template == "products":
            context = page_products(request)
        elif load_template == "stats" or load_template == "":
            load_template = "stats"
            context = page_stats(request)
        context['segment'] = load_template

        html_template = loader.get_template(load_template + ".html")
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    # except:
    #     html_template = loader.get_template( 'page-500.html' )
    #     return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def page_orders(request):
    context = {}
    orders = Order.objects.all().order_by("-id")
    context['orders'] = orders

    today = datetime.date.today()
    start_week = today - datetime.timedelta(today.weekday())
    end_week = start_week + datetime.timedelta(7)

    # users = {}
    # for order in orders:
    #     username = order.first_name + " " + order.last_namecreated_at
    #     if username.lower() not in users:
    #         users[username.lower()] = {"f": order.first_name, "l": order.last_name}

    # for user in users:
    #     daily_orders = Order.objects.filter(first_name__iexact=users[user]["f"], last_name__iexact=users[user]["l"], created_at__year=today.year, created_at__month=today.month, created_at__day=today.day).aggregate
    #     weekly_orders = Order.objects.filter(first_name__iexact=users[user]["f"], last_name__iexact=users[user]["l"], created_at__range=[start_week, end_week])
    # o = Order.objects.extra(select={'username': Concat('first_name', Value(' '),  'last_name')}).annotate(count=Count('paid_quantity'))
    # o = Order.objects.all().values("first_name", "last_name").annotate(count=Count('first_name'), quantity=Sum('paid_quantity')).order_by()

    daily_orders = Order.objects.filter(created_at__year=today.year, created_at__month=today.month, created_at__day=today.day).values(
        "first_name", "last_name").annotate(count=Count('first_name'), quantity=Sum('paid_quantity')).order_by()
    weekly_orders = Order.objects.filter(created_at__range=[start_week, end_week]).values(
        "first_name", "last_name").annotate(count=Count('first_name'), quantity=Sum('paid_quantity')).order_by()
    monthly_orders = Order.objects.filter(created_at__year=today.year, created_at__month=today.month).values(
        "first_name", "last_name").annotate(count=Count('first_name'), quantity=Sum('paid_quantity')).order_by()

    statistics = []
    for order in daily_orders:
        statistics.append({'period': 'daily', 'username': order["first_name"] + " " +
                           order["last_name"], 'count': order["count"], 'quantity': order["quantity"]})

    for order in weekly_orders:
        statistics.append({'period': 'weekly', 'username': order["first_name"] + " " +
                           order["last_name"], 'count': order["count"], 'quantity': order["quantity"]})

    for order in monthly_orders:
        statistics.append({'period': 'monthly', 'username': order["first_name"] + " " +
                           order["last_name"], 'count': order["count"], 'quantity': order["quantity"]})

    context['statistics'] = statistics

    return context


@login_required(login_url="/login/")
def page_vendors(request):
    context = {}
    vendors = Vendor.objects.all()

    vendor_list = []
    for vendor in vendors:
        products = len(Product.objects.filter(vendor=vendor.id))
        print("=== ", vendor.company_name, products)
        vendor_list.append({"id": vendor.id, "name": vendor.company_name, "code": vendor.company_code, "email": vendor.email,
                            "address": vendor.address, "phone": vendor.phone, "enabled": vendor.enabled, "products": products, "limit": vendor.products_limit})
    context['vendors'] = vendor_list

    return context


@login_required(login_url="/login/")
def page_customers(request):
    context = {}
    customers = Customer.objects.all()
    customer_list = []
    for customer in customers:
        customer_list.append({"id": customer.user_id, "name": customer.customername, "email": customer.email,
                              "address": customer.address, "phone": customer.phone, "created": customer.created_at})
    context['customers'] = customer_list

    return context


@login_required(login_url="/login/")
def page_product_review(request):
    context = {}
    products = Product.objects.filter(visible=False)
    product_list = []
    for product in products:
        # print(product.category_id, product.category, product.category)
        print(product.category_id, product.category,
              product.category.sub_category, product.category.sub_category.category)
        product_list.append({"id": product.id, "title": product.title, "description": product.description, "price": product.price, "date_added": product.created_at, "vendor": product.vendor.company_name, "slug": product.category.sub_category.category.slug + "/" + product.category.sub_category.slug +
                             "/" + product.category.slug + "/" + product.slug, "main_category": product.category.sub_category.category.title, "sub_category": product.category.sub_category.title, "sub_sub_category": product.category.title, "num_available": product.quantity, "visible": product.visible})
        # product_list.append({"id": product.id, "title": product.title, "description": product.description, "price": product.price, "date_added": product.date_added, "image": product.image, "vendor": product.vendor.company_name, "slug": product.category.sub_category.category.slug + "/" + product.category.sub_category.slug + "/" + product.category.slug + "/" + product.slug, "main_category": product.category.sub_category.category.title, "sub_category": product.category.sub_category.title, "sub_sub_category": product.category.title, "num_available": product.num_available, "visible": product.visible})
    context['products'] = product_list

    return context


@login_required(login_url="/login/")
def page_products(request):
    context = {}
    products = Product.objects.filter(visible=True)
    product_list = []
    for product in products:
        # print(product.category_id, product.category, product.category)
        print(product.category_id, product.category,
              product.category.sub_category, product.category.sub_category.category)
        product_list.append({"id": product.id, "title": product.title, "description": product.description, "price": product.price, "date_added": product.created_at, "vendor": product.vendor.company_name, "slug": product.category.sub_category.category.slug + "/" + product.category.sub_category.slug +
                             "/" + product.category.slug + "/" + product.slug, "main_category": product.category.sub_category.category.title, "sub_category": product.category.sub_category.title, "sub_sub_category": product.category.title, "num_available": product.quantity, "visible": product.visible})
    context['products'] = product_list

    return context


@login_required(login_url="/login/")
def page_stats(request):
    context = {}
    today = datetime.date.today()
    start_week = today - datetime.timedelta(today.weekday())
    end_week = start_week + datetime.timedelta(7)

    products = len(Product.objects.all())
    vendors = len(Vendor.objects.all())
    customers = len(Customer.objects.all())

    daily_orders = Order.objects.filter(created_at__year=today.year, created_at__month=today.month,
                    created_at__day=today.day).aggregate(count=Count('paid_amount'), sum=Sum('paid_amount'))
    weekly_orders = Order.objects.filter(created_at__range=[start_week, end_week]).aggregate(
        count=Count('paid_amount'), sum=Sum('paid_amount'))
    monthly_orders = Order.objects.filter(created_at__year=today.year, created_at__month=today.month).aggregate(
        count=Count('paid_amount'), sum=Sum('paid_amount'))
    all_orders = Order.objects.all().aggregate(
        count=Count('paid_amount'), sum=Sum('paid_amount'))

    context["products"] = products
    context["vendors"] = vendors
    context["customers"] = customers
    context["daily"] = daily_orders
    context["weekly"] = weekly_orders
    context["monthly"] = monthly_orders
    context["all"] = all_orders

    return context


@login_required(login_url="/login/")
def product_admin(request, category_slug, subcategory_slug, subsubcategory_slug, product_slug):
    cart = Cart(request)

    product = get_object_or_404(
        Product, category__slug=subsubcategory_slug, slug=product_slug)

    cart = Cart(request)

    if cart.has_product(product.id):
        product.in_cart = True
    else:
        product.in_cart = False
    product_imgs = ProductImage.objects.filter(product=product)

    return render(request, 'product/product_admin.html', {'product': product, 'imgs': product_imgs})


@login_required(login_url="/login/")
def orderDetails(request, order_id):
    context = {}
    order = Order.objects.filter(id=order_id).first()
    vendors = OrderProduct.objects.filter(order_id=order.id).select_related(
        "vendor").values("vendor__company_name").annotate(count=Count("vendor")).order_by()
    orderItems = OrderProduct.objects.filter(order_id=order.id)

    context["order"] = order
    context["vendors"] = vendors
    context["orderItems"] = orderItems
    context['segment'] = "orders"
    html_template = loader.get_template('order_detail.html')
    return HttpResponse(html_template.render(context, request))
