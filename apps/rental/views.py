from unicodedata import category
from urllib import request
from django.shortcuts import render
from .models import Category,Item

# Create your views here.
def index(request):
    category=Category.objects.all()
    return render(request,'rental/index.html',{'category':category})

def category(request,id):
    category=Category.objects.get(id=id)
    items=Item.objects.filter(category=category)
    return render(request,'rental/category.html',{'items':items,'category':category})

def item_Detail(request,id,category_slug,slug):
    item=Item.objects.get(id=id)
    return render(request,'rental/details.html',{'item':item})