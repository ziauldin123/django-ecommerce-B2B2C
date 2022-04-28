import email
import imp
from pyexpat.errors import messages
import re
from unicodedata import category
from urllib import request
import django
from django.shortcuts import redirect, render
from django.utils.text import slugify
from apps.product.views import search
from apps.rental.forms import ItemForm,SearchForm
from apps.vendor.models import Customer, Vendor, UserWishList
from .models import Amenity, Application, Capacity, Category,Item, Item_Model,Make, Room,Year, Engine, Type
from django.contrib import messages
from django.core.paginator import (Paginator,PageNotAnInteger,EmptyPage)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from apps.cart.cart import Cart
from apps.cart.models import District
from apps.ordering.models import ShopCart
from .services.filter import items_filters

# Create your views here.
def index(request):
    category_list=Category.objects.all()
    paginator = Paginator(category_list,6)
    page = request.GET.get('page')
   
    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = UserWishList.objects.filter(user=current_user)
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

    try:
        category = paginator.page(page)
    except PageNotAnInteger:
        category = paginator.page(1)
    except EmptyPage:
        category = paginator.page(paginator.num_pages)        

    return render(request,'rental/index.html',
    {
        'category':category,
        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare
        })

def category(request,id,category_slug):
    category=Category.objects.get(id=id)
    # items_list=Item.objects.filter(category=category,visible=True)
    
    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = UserWishList.objects.filter(user=current_user)
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

    items_list = Item.objects.filter(category=category,review=True,visible=True)
        
    
    locations = District.objects.all()
    makes = Make.objects.all()
    rooms = Room.objects.all()
    application = Application.objects.all()
    capacity = Capacity.objects.all()
    amenity = Amenity.objects.all()
    year = Year.objects.all()
    model= Item_Model.objects.all()
    engine = Engine.objects.all()
    item_type= Type.objects.all()

    search_form = SearchForm(request.GET) 

    query=request.GET.get('query')
    price_to=request.GET.get('price_to')
    price_from=request.GET.get('price_from')
    query_sale=request.GET.get('sale')
    query_loc=request.GET.get('location')
    query_makes=request.GET.get('make')
    query_rooms=request.GET.get('room')
    query_application=request.GET.get('application')
    query_capacity=request.GET.get('capacity')
    query_amenity=request.GET.get('amenity')
    query_year=request.GET.get('year')
    query_model=request.GET.get('model')
    query_engine=request.GET.get('engine')
    query_item_type=request.GET.get('item_type')

    if not query:
        query = ''
    if price_from == None:
        price_from = 0
    if price_to == None:
        price_to = "10000"  
    max_amount = "500000" 
    
    sorting = request.GET.get('sorting','created_at')
    
    items_ids = []
    items_ids.extend(
        category.items.all().values_list('id',flat=True)
    )
        
    items_list = Item.objects.filter(id__in=items_ids,review=True)    
    if search_form.is_valid():
        items_list,price_from,price_to,sale,locations,makes,rooms,application,capacity,amenity,year,model,engine,item_type = items_filters.filter_items(query_loc,items_list,sorting=sorting,**search_form.cleaned_data)
        print('loc:',locations)
    else:
        print(search_form.errors)
    search_form = SearchForm(request.GET,items=items_list)
    paginator = Paginator(items_list,6)
    page  = request.GET.get('page')

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.numb_pages)
    
    
    return render(request,'rental/category.html',
    {
        'items':items,
        'category_title':category,
        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare,
        'query':query,
        'form':search_form,
        'sorting':sorting,
        'price_to':re.sub('[\$,]','',str(price_to)),
        'price_from':re.sub('[\$,]','',str(price_from)),
        'query_loc':query_loc,
        'query_makes':query_makes,
        'query_rooms':query_rooms,
        'max_amaount':max_amount,
        'location':locations,
        'makes':makes,
        'rooms':rooms,
        'applicaton':application,
        'query_application':query_application,
        'capacity':capacity,
        'query_capacity':query_capacity,
        'amenity':amenity,
        'query_amenity':query_amenity,
        'year':year,
        'query_year':query_year,
        'model':model,
        'query_model':query_model,
        'model':model,
        'query_model':query_model,
        'engine':engine,
        'query_engine':query_engine,
        'item_type':item_type,
        'query_item_type':query_item_type,
        # 'sale':sale,
        # 'query_sale':query_sale
    })

def item_Detail(request,id,category_slug,slug):
    url=request.META.get('HTTP_REFERER')
    item=Item.objects.get(id=id)
    
    if Customer.objects.filter(user=item.user).exists():
        user=Customer.objects.get(user=item.user)
    else:
        user=Vendor.objects.get(user=item.user)

    if not request.user.is_anonymous:
        cart = Cart(request)
        current_user = request.user
        wishlist = UserWishList.objects.filter(user=current_user)
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

    if not item.visible:
        messages.success(request, 'Item not available') 
        return redirect(url)

    return render(request,'rental/details.html',
    {   'item':item,
        'shopcart': shopcart,
        'subtotal': total,
        'tax': tax,
        'total': grandTotal,
        'wishlist': wishlist,
        'total_compare': total_compare,
        'user':user
        })

def get_user_items(request):
    current_user=request.user
    items=Item.objects.filter(email=current_user,visible=True)
    vendor=[]
    try:
        if current_user.vendor:
            vendor=Vendor.objects.get(email=current_user)  
    except:
        print('customer')
    print(vendor)    
    return render(request,'rental/allItems.html',{'items':items,'vendor':vendor})

@login_required
def add_item(request):
    equipment_id=Category.objects.get(title='Equipment').id
    space_id=Category.objects.get(title='Spaces').id
    vehicles_id=Category.objects.get(title='Vehicles').id
    current_user =  request.user
    username=User.objects.get(email=current_user)
    if Customer.objects.filter(user=current_user).exists():
        district=Customer.objects.get(user=current_user).district
    else:
        district=Vendor.objects.get(user=current_user).district    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.email = username    
            item.slug = slugify(item.title)
            item.user = current_user
            item.district = district
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

    return render(request,'add_item.html',{'form':form,'equipment_id':equipment_id,'space_id':space_id,'vehicles_id':vehicles_id})        


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