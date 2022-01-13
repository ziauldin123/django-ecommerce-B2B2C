from django.http import HttpResponse
from django.http import request
from django.shortcuts import render
from apps.cart.cart import Cart
from apps.ordering.models import ShopCart
from django.core.mail import send_mail

# from apps.product.models import Product, Category, SubCategory, SubSubCategory
from apps.newProduct.models import Product, Category, SubCategory, SubSubCategory, Variants


def frontpage(request):
    variants = Variants.objects.filter(status=True)
    product = Product.objects.filter(status=True, visible=True)

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
        status=True, visible=True, is_featured=True)[0:4]
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
        '-last_visit')[0:4]

    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        # cart.clear()
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        if cart.__len__() == 0:
            for rs in shopcart:
                if rs.variant is None:
                    cart.add(product_id=rs.product.id,variant_id=None, user_id=current_user.id,
                         quantity=rs.quantity, update_quantity=True) 
                else:
                    cart.add(product_id=rs.product.id,variant_id=rs.variant.id, user_id=current_user.id,
                         quantity=rs.quantity, update_quantity=True)                 
        
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
            'var': var
        }
    )


def contact(request):
    if request.method == 'POST':
        print('hello')
        name = request.POST.get('full-name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        }
        message = '''
        New message: {}

        From: {}
        '''.format(data['message'], data['email'])
        send_mail(data['subject'], message, '', ['warehouse2fifty@gmail.com'])
        return HttpResponse('Thank you for your message, we will be in touch soon')

    return render(request, 'core/contact.html')


def about(request):
    return render(request, 'core/about.html')


def pricing(request):
    return render(request, 'core/pricing.html')


def frequently_asked_questions(request):
    return render(request, 'core/frequently_asked_questions.html')


def termsandconditions(request):
    return render(request, 'core/termsandconditions.html')


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def error_404_view(request, exception):
    return render(request, 'core/404.html')
