from base64 import urlsafe_b64decode
from email import message
from unicodedata import category
from django.shortcuts import redirect, render
from .models import Category,ServiceProvider
from django.core.paginator import (Paginator,PageNotAnInteger,EmptyPage)
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .forms import ServiceProviderForm
from apps.vendor.models import Profile
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
import email
from apps.vendor import tokens,views
from django.utils.encoding import force_bytes
from django.contrib import messages
from django.utils.text import slugify

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


    return render(request,'index.html',{'categories':categories})          

def get_category(request,id):
    service = Category.objects.get(id=id)
    providers_list = ServiceProvider.objects.filter(service=service,review=True)
    paginator = Paginator(providers_list,6)
    page = request.GET.get('page')

    try:
        providers = paginator.page(page)
    except PageNotAnInteger:
        providers = paginator.page(1)
    except EmptyPage:
        providers = paginator.page(paginator.num_pages)
          
    
    return render(request,'service.html',{'service':service,'providers':providers})

def get_service_provider(request,id,service_slug,slug):
    service_provider = ServiceProvider.objects.get(id=id)

    return render (request,'provider.html',{'provider':service_provider})

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
            service_provider = ServiceProvider(
                name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email'),
                service=service_id,
                phone=form.cleaned_data.get('phone'),
                slug=slugify(form.cleaned_data.get('name')),
                available=True,
                review=False,
                privacy_checked=privacy_checked,
                user=user
            )
            service_provider.save()

            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            message = render_to_string('vendor/activation_request.html',
            {
                'user':user,
                'domain':current_site.domain,
                'uid':urlsafe_b64decode(force_bytes(user.pk)),
                'token':tokens.account_activation_token.make_token(user),
            }) 

            views.email_user(user,subject,message)

            return redirect('activation_sent')     
        else:
            print(form.cleaned_data.get('service'))
            messages.add_message(
                request, messages.ERROR, "Input field not Valid"
            )    
            return redirect('become-service-provider')
    else:
        form = ServiceProviderForm()

    return render(request,'become_provider.html',{'form':form})        
    

