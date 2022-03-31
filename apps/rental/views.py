import email
import imp
from pyexpat.errors import messages
import re
from unicodedata import category
from urllib import request
import django
from django.shortcuts import redirect, render
from django.utils.text import slugify
from apps.rental.forms import ItemForm
from apps.vendor.models import Customer, Vendor
from .models import Category,Item
from django.contrib import messages
from django.core.paginator import (Paginator,PageNotAnInteger,EmptyPage)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    category_list=Category.objects.all()
    paginator = Paginator(category_list,6)
    page = request.GET.get('page')

    try:
        category = paginator.page(page)
    except PageNotAnInteger:
        category = paginator.page(1)
    except EmptyPage:
        category = paginator.page(paginator.num_pages)        

    return render(request,'rental/index.html',{'category':category})

def category(request,id):
    category=Category.objects.get(id=id)
    items_list=Item.objects.filter(category=category,visible=True)

    paginator = Paginator(items_list,6)
    page  = request.GET.get('page')
    
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)   
    except EmptyPage:
        items = paginator.page(paginator.numb_pages)     

    for item in items:
        print(item.category.slug)
    return render(request,'rental/category.html',{'items':items,'category_title':category})

def item_Detail(request,id,category_slug,slug):
    url=request.META.get('HTTP_REFERER')
    item=Item.objects.get(id=id)
    if not item.visible:
        messages.success(request, 'Item not available') 
        return redirect(url)

    return render(request,'rental/details.html',{'item':item})

def get_user_items(request):
    current_user=request.user
    items=Item.objects.filter(email=current_user,visible=True)

    return render(request,'rental/allItems.html',{'items':items})

@login_required
def add_item(request):
    current_user =  request.user
    username=User.objects.get(email=current_user)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.email = username    
            item.slug = slugify(item.title)
            item.user = request.session.get('username')
            item.visible = True
            item.review=False
            item.phone = request.session.get('phone')
            item.save()
            messages.add_message(
                request, messages.SUCCESS, "New Rental Item Added and is under-review"
            )
            return redirect('items')
        else:
            messages.add_message(
                request, messages.ERROR, "Input field not Valid"
            )    
            return redirect('add_item')
    else:
        form = ItemForm()

    return render(request,'add_item.html',{'form':form})        


@login_required
def edit_item(request,pk):
    item = Item.objects.filter(id=pk).first()
    if request.method == 'POST':
        form = ItemForm(request.POST,request.FILES,instance=item)
        if form.is_valid():
            form.save()
            messages.info(request,"Product Updated")
            return redirect('items')
        else:
            messages.add_message(
                request,messages.ERROR, "Input fiels not valid"
            )  
            return redirect('edit_item')  
    else:
        form = ItemForm(instance=item)

    return render(request,'edit_item.html',{'form':form,'item':item})        

@login_required
def delete_item(request,pk):
    Item.objects.filter(id=pk).update(visible=False)
    messages.info(request,"Item Deleted")
    return redirect('items')