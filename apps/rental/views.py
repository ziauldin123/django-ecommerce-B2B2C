from unicodedata import category
from urllib import request
from django.shortcuts import render
from .models import Category,Item

# Create your views here.
def index(request):
    category=Category.objects.all()
    return render(request,'rental/index.html',{'category':category})

def item_Detail(request,id,vendor_slug,category_slug,slug,):
    item=Item.objects.get(pk=id)
    return render(request,'rental/details.html',{'item':item})