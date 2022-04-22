from base64 import urlsafe_b64decode
from email import message
import imp
from unicodedata import category
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
import re

from apps.services.forms import SearchForm
from .models import Category, Daily_rate, Experience,ServiceProvider,CommentForm,Comment
from django.core.paginator import (Paginator,PageNotAnInteger,EmptyPage)
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .forms import ServiceProviderForm
from apps.vendor.models import Profile
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
import email
from django.contrib.auth.decorators import login_required
from apps.vendor import tokens,views,models
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Max
from apps.cart.cart import Cart
from apps.ordering.models import ShopCart
from .filters.filter import providers_filters

# Create your views here.
def index(request):
    category_list=Category.objects.all()
    paginator = Paginator(category_list,6)
    page = request.GET.get('page')

    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories =   paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)

    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = models.UserWishList.objects.filter(user=current_user)
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


    return render(request,'index.html',
    {  'categories':categories,
       'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
    })          

def get_category(request,id,service_slug):
    service = Category.objects.get(id=id)
    providers_list = ServiceProvider.objects.filter(service=service,review=True)
    

    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = models.UserWishList.objects.filter(user=current_user)
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
    
    ratings = [1,2,3,4,5]
    experiences = Experience.objects.all()
    daily_rates = Daily_rate.objects.all()
    search_form = SearchForm(request.GET)

    query=request.GET.get('query')
    query_rating=request.GET.get('rating')
    query_experience=request.GET.get('experience')
    query_daily_rate=request.GET.get('daily_rate')
    price_to=request.GET.get('price_to')
    price_from=request.GET.get('price_from')

    if not query:
        query = ''
    if price_from == None:
        price_from = 0
    if price_to == None:
        price_to = "10000"
    max_amount = "500000"            

    sorting = request.GET.get('sorting','created_at')

    providers_ids = []
    providers_ids.extend(
        service.service_category.all().values_list('id',flat=True)
    )
    providers_list = ServiceProvider.objects.filter(id__in=providers_ids,review=True)
    if search_form.is_valid():
        providers_list,price_from,price_to,experiences,daily_rates= providers_filters.filter_provider(providers_list,sorting=sorting,**search_form.cleaned_data)
    else:
        print(search_form.errors) 

    search_form = SearchForm(request.GET,providers=providers_list)
    paginator = Paginator(providers_list,6)
    page = request.GET.get('page')

    try:
        providers = paginator.page(page)
    except PageNotAnInteger:
        providers = paginator.page(1)
    except EmptyPage:
        providers = paginator.page(paginator.num_pages)

    return render(
    request,
    'service.html',
    {
    'service':service,
    'providers':providers, 
    'shopcart': shopcart,
    'subtotal': total,
    'tax': tax,
    'total': grandTotal,
    'wishlist': wishlist,
    'total_compare': total_compare,
    'query_experience':query_experience,
    'experiences':experiences,
    'query':query,
    'form':search_form,
    'sorting':sorting,
    'ratings':ratings,
    'daily_rates':daily_rates,
    'query_daily_rate':query_daily_rate,
    'price_to':re.sub('[\$,]','',str(price_to)),
    'price_from':re.sub('[\$,]','',str(price_from)),
    })

def get_service_provider(request,id,service_slug,slug):
    service_provider = ServiceProvider.objects.get(id=id)
    username = request.user
    customer = models.Customer.objects.filter(email=username)
    # max = service_provider.service_provider.all().aggregate(Max('rate'))
    max=round(service_provider.avarageview(),0)
    comment_list = Comment.objects.filter(service_provider=id,status='True')
    paginator = Paginator(comment_list,2)
    page = request.GET.get('page')

    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)  


    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = models.UserWishList.objects.filter(user=current_user)
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

    return render (request,'provider.html',
    {
        'provider':service_provider,
        'max':max,
        'customer':customer,
        'comments':comments,
        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
        })

def become_service_provider(request):
    if request.user.is_authenticated:
        logout(request)
    
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data.get('email')).exists():
                user = User.objects.get(
                    username=form.cleaned_data.get('email')
                )
            else:
                user = form.save(commit=False)
                user.username = form.cleaned_data.get('email')
                user.is_active = False
                user.save()
            if not Profile.objects.filter(email=form.cleaned_data.get('email')).exists():
                profile = Profile(
                    user=user, email=form.cleaned_data.get('email')
                )  
                profile.save()

            privacy_checked = request.POST.get('is_privacy')
            
            service_id=form.cleaned_data['service']
            service=Category.objects.get(id=service_id)

            service_provider = ServiceProvider(
                service=service,
                slug=slugify(form.cleaned_data.get('name')),
                phone=form.cleaned_data.get('phone'),
                email=form.cleaned_data.get('email'),
                name=form.cleaned_data.get('name'),
                account=form.cleaned_data.get('account'),
                available=True,
                review=False,
                privacy_checked=privacy_checked,
                user=user
            )
            service_provider.save()

            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            message = render_to_string('activation_request.html',
            {
                'user':user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':tokens.account_activation_token.make_token(user),
            }) 

            views.email_user(user,subject,message)

            return redirect('activation_sent')     
        else:
            messages.add_message(
                request, messages.ERROR, "Input field not Valid"
            )    
            return redirect('become-service-provider')
    else:
        form = ServiceProviderForm()

    return render(request,'become_provider.html',{'form':form})        

@login_required    
def myServiceAccount(request):
    try:
        service_provider = request.user.service_provider
    except Exception as e:
        return redirect('frontpage')        
    return render(
        request,
        'myServiceAccount.html',
        {'serviceProvider':service_provider}
    )

@login_required
def upload_profile(request):
    service_provider = request.user.service_provider
    if request.method == 'POST':
        if "image" in request.FILES and len(request.FILES["image"]) > 0:
            service_provider.image = request.FILES["image"]
            service_provider.save()
            request.session['logo'] = ServiceProvider.objects.get(
                email=service_provider.email
            ).image.url
            messages.info(request,f"Profile Picture Updated Successfully")
    return redirect('mySerrviceAccount')        

@login_required
def update_profile(request,id):
    url=request.META.get('HTTP_REFERER')
    service_provider=ServiceProvider.objects.filter(id=id).first()
    if request.method == 'POST':
        description=request.POST.get('description')
        if service_provider.account == 'INDIVIDUAL':
            tin=0
        else :
            tin=request.POST.get('tin')  
        service_provider.tin=tin
        service_provider.description=description
        service_provider.save()

        messages.info(request,'User Profile Updated') 
        return redirect('mySerrviceAccount')      
    else:
        form = ServiceProviderForm(instance=service_provider)

    return render(request,'edit-profile.html',{'form':form,'service_provider':service_provider})

def addComment(request,id):
    url=request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()
            data.subject = form.cleaned_data['subject']
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            data.ip = request.META.get('REMOTE_ADDR')
            data.service_provider_id = id
            data.customer_id=request.user.id
            data.save()
            messages.success(
                request,"Your review has been submitted."
            )
            return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)        
