from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.query import RawQuerySet
from django.http import HttpResponse,HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render,redirect
from django.conf import settings
from apps.cart.cart import Cart
from django.utils.crypto import get_random_string
from apps.ordering.models import ShopCart,ShopCartForm,Order,OrderItem
from apps.newProduct.models import Category,Product,Variants
from apps.vendor.models import Customer, Profile
from apps.cart.models import District,Sector,Cell,Village
from decimal import Decimal
from django.views.decorators.cache import never_cache,cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
@never_cache
def index(request):
    return HttpResponse("Order Page")

@login_required(login_url='/login') #check login
@never_cache
@csrf_exempt
def addtoshopcart(request,id):
    cart = Cart(request)
    url=request.META.get('HTTP_REFERER')#get last url
    current_user=request.user #Access User Session infor
    product=Product.objects.get(pk=id)
    variantid = request.POST.get('variantid')
    customer=Customer.objects.filter(email=current_user)
    print("variant id", variantid)


    if product.is_variant:
        #get variant object
        #from variant add to cart
        checkinvariant = ShopCart.objects.filter(variant_id=variantid,user=current_user) #check product from cart
        if checkinvariant:
            control = 1 #product is in cart
        else:
            control = 0 #product is not in cart
    else:
        #No Variant
        variant=None

        checkinproduct = ShopCart.objects.filter(product_id=id, user_id=current_user)# check product in cart
        if checkinproduct:
            control = 1 #product is in cart
        else:
            control = 0 #product is not in cart


    if request.method == 'POST': #if there is a post
        print("control",control)
        p_quantity = int(request.POST.get('quantity'))


        if control == 1: #update shopcart
            if product.variant == 'None':
                data = ShopCart.objects.get(product_id=id, user_id=current_user)
            else:
                data=ShopCart.objects.get(variant_id=variantid, user_id=current_user.id)
            data.quantity += p_quantity
            data.save()#save data

            cart.add(product_id=product.id,user_id=current_user.id,quantity=p_quantity, update_quantity=True)
        else :# insert to shopcart
            data=ShopCart()
            if product.variant != 'None':
                variant=Variants.objects.get(id=variantid)
                data.variant=variant
                data.variant_id=variantid
            data.user=current_user
            data.product=product
            data.quantity = p_quantity
            data.save()
                # cart.set(int(product.id), int(form.cleaned_data['quantity']))
            cart.add(product_id=product.id,user_id=current_user.id, quantity=p_quantity, update_quantity=True)


        messages.success(request,"Product added to Shopcart")
        return HttpResponse("Success!")



    else:#if there is no post
        if control == 1:
            print("get 1")
            data=ShopCart.objects.get(product_id=id, user_id=current_user.id)
            data.quantity += 1
            data.save()
            cart.add(product_id=product.id,variant_id=None,quantity=1, update_quantity=True,user_id=current_user.id)
        else:#insert to shopcart
            print("get")
            data=ShopCart.objects.create(
                user_id=current_user.id,
                product_id = id,
                quantity = 1,
                variant_id = None,
            )
            cart.add(product_id=product.id,variant_id=None, quantity=1, update_quantity=True,user_id=current_user.id)
        messages.success(request,'Product added to Shopcart')
        return HttpResponse("Success!")

@never_cache
def shopcart(request):
    category = Category.objects.all()
    current_user = request.user
    cart = Cart(request)

    if request.method == 'POST':
        if request.user.is_authenticated:
            # messages.success(request, 'Thank you for your order')
            if "id_quantity" in request.POST:
                print("coupon code = ", request.POST["coupon_code"])
                print("coupon value = ", request.POST["coupon_discount"])
                coupon_code = request.POST["coupon_code"]
                coupon_discount = request.POST["coupon_discount"]
                if coupon_discount == "":
                    coupon_code = ""

                coupon = request.session.get(settings.COUPON_SESSION_ID)
                if not coupon:
                    coupon = request.session[settings.COUPON_SESSION_ID] = {}
                coupon["code"] = coupon_code
                coupon["discount"] = coupon_discount
                request.session[settings.COUPON_SESSION_ID] = coupon
                request.session.modified = True
                for elem in request.POST["id_quantity"].split(":"):
                    elem_id = elem.split("_")[0]
                    elem_quantity = elem.split("_")[1]
                    cart.set(elem_id, elem_quantity)

                return redirect('contact_info')
        else:
            messages.success(request, 'Please sign in')
            return redirect('login')

    if not request.user.is_anonymous:

        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total=cart.get_cart_cost()
        tax=cart.get_cart_tax()
        grandTotal=cart.get_cart_cost() + cart.get_cart_tax()

        context={'shopcart': shopcart,
                'category':category,
                'total': round(Decimal(total),2),
                'tax':tax,
                'grandTotal':grandTotal
                }
    else:
         context={'shopcart': None,
                'category':None,
                'total': None,
                'tax':None,
                'grandTotal':None
                }
    return render(request,'shopcart_products.html',context)

@login_required(login_url='/login')
@never_cache
def deletefromcart(request,id):
    cart=Cart(request)

    shopcart=ShopCart.objects.get(id=id)

    cart.delete_product(shopcart.id)


    ShopCart.objects.filter(id=id).delete()


    messages.success(request, "Your item deleted form Shopcart.")
    return HttpResponseRedirect("/shopcart")

@csrf_exempt
@never_cache
def update(request):
    cart_data = Cart(request)
    if request.method == "POST":
        prod_id=int(request.POST.get('product_id'))
        if(ShopCart.objects.filter(user=request.user,id=prod_id)):
            prod_qty=int(request.POST.get('product_qty'))
            cart=ShopCart.objects.get(id=prod_id,user=request.user)
            cart.quantity=prod_qty
            cart.save()
            if cart.product.is_variant:
                cart_data.add(product_id=cart.product.id,variant_id=cart.variant.id,user_id=request.user.id, quantity=prod_qty, update_quantity=True)
            else:
                cart_data.add(product_id=cart.product.id,variant_id=None,user_id=request.user.id, quantity=prod_qty, update_quantity=True)    

            
            return JsonResponse({'status':"Updated"})

    return redirect('/')

def orderproduct(request):
    category = Category.objects.all()
    current_user = request.user
    district=District.objects.all()
    sector=Sector.objects.all()
    cell=Cell.objects.all()
    village=Village.objects.all()

    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for rs in shopcart:
        if rs.product.variant == 'None':
            total += rs.product.price * rs.quantity
        else:
            total += rs.variant.price * rs.quantity

    if request.method == 'POST':  # if there is a post
        form = OrderForm(request.POST)
        #return HttpResponse(request.POST.items())
        if form.is_valid():
            # Send Credit card to bank,  If the bank responds ok, continue, if not, show the error
            # ..............

            data = Order()
            data.first_name = form.cleaned_data['first_name'] #get product quantity from form
            data.last_name = form.cleaned_data['last_name']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.phone = form.cleaned_data['phone']
            data.user_id = current_user.id
            data.total = total
            data.ip = request.META.get('REMOTE_ADDR')
            ordercode= get_random_string(5).upper() # random cod
            data.code =  ordercode
            data.save() #


            for rs in shopcart:
                detail = OrderProduct()
                detail.order_id     = data.id # Order Id
                detail.product_id   = rs.product_id
                detail.user_id      = current_user.id
                detail.quantity     = rs.quantity
                if rs.product.variant == 'None':
                    detail.price    = rs.product.price
                else:
                    detail.price = rs.variant.price
                detail.variant_id   = rs.variant_id
                detail.amount        = rs.amount
                detail.save()
                # ***Reduce quantity of sold product from Amount of Product
                if  rs.product.variant=='None':
                    product = Product.objects.get(id=rs.product_id)
                    product.amount -= rs.quantity
                    product.save()
                else:
                    variant = Variants.objects.get(id=rs.product_id)
                    variant.quantity -= rs.quantity
                    variant.save()
                #************ <> *****************

            ShopCart.objects.filter(user_id=current_user.id).delete() # Clear & Delete shopcart
            request.session['cart_items']=0
            messages.success(request, "Your Order has been completed. Thank you ")
            return render(request, 'Order_Completed.html',{'ordercode':ordercode,'category': category})
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect("/order/orderproduct")

    form= OrderForm()
    profile = Profile.objects.get(user_id=current_user.id)
    context = {'shopcart': shopcart,
               'category': category,
               'total': total,
               'form': form,
               'profile': profile,
               'district':district,
               'sector':sector,
               'cell':cell,
               'village':village
               }
    return render(request, 'Order_Form.html', context)




