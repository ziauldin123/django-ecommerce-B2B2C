import imp
from unicodedata import category
from urllib import request
import django
from django.shortcuts import render
from .models import Category,Item
from django.core.paginator import (Paginator,PageNotAnInteger,EmptyPage)

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
    items_list=Item.objects.filter(category=category)

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
    item=Item.objects.get(id=id)
    return render(request,'rental/details.html',{'item':item})