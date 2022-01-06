from decimal import Decimal
from django.core.validators import ProhibitNullCharactersValidator

import stripe
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render

from apps.vendor.models import Customer, Vendor
from .cart import Cart
from apps.ordering.models import Order,ShopCart
from .forms import CheckoutForm, PaymentForm
from .models import Cell, District, Sector, Village
from .services.payment_service import payment_service
from ..core.utils import get_attr_or_none
# from ..product.models import Product
from apps.newProduct.models import Product


def cart_detail(request):
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

    remove_from_cart = request.GET.get('remove_from_cart', '')
    change_quantity = request.GET.get('change_quantity', '')
    quantity = request.GET.get('quantity', 0)

    if remove_from_cart:
        cart.remove(remove_from_cart)
        return redirect('cart')

    if change_quantity:
        cart.add(change_quantity, quantity, True)
        return redirect('cart')

    return render(request, 'cart/cart.html')


def contact_info(request):
    delivery_type=''
    district=''
    sector=''
    cell=''
    village=''
    cart = Cart(request)

    districts = District.objects.all()

    cart_vendor = Vendor.objects.filter(email=request.user.email).first()
    cart_customer = Customer.objects.filter(email=request.user.email).first()
    current_user=request.user



    coupon_discount=cart.get_coupon_discount()
    print(coupon_discount,"%")

    

    use_vendor_delivery,pickup_avaliable=cart.get_is_vendor_delivery()
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    # products = [i['product'] for i in cart]
    sub_total=cart.get_cart_cost()
    total=total=cart.get_cart_cost_with_coupen()
    tax=Cart(request).get_cart_tax()
    grandTotal=cart.get_cart_cost() + cart.get_cart_tax()
    

    if cart_customer:
        print("cart_customer")
        if request.method == 'POST':
            print("POST")
            form = CheckoutForm(use_vendor_delivery, request.POST)

            if form.is_valid():
                district_id = form.cleaned_data['district']
                sector_id = form.cleaned_data['sector']
                cell_id = form.cleaned_data['cell']
                village_id = form.cleaned_data['village']
                address = form.cleaned_data['delivery_address']

                option = form.cleaned_data['delivery_option']
                products = [i['product'] for i in cart]
                print(cart)
                is_free_delivery = all([p['is_free_delivery'] for p in products])
                print('is free delivery')
                print(is_free_delivery)


                if option == "Store":
                    print(option)
                    # print(shopcart)
                    for i in shopcart:
                        print(i.product.vendor)
                        vendor = i.product.vendor
                        # vendor = Vendor.objects.get(pk=vendor_id)
                        district = get_attr_or_none(vendor.district, 'district')
                        sector = get_attr_or_none(vendor.sector, 'sector')
                        cell = get_attr_or_none(vendor.cell, 'cell')
                        village = get_attr_or_none(vendor.village, 'village')
                        address = get_attr_or_none(vendor, 'address')
                        # TODO sometime cost is free
                        delivery_cost = '0'
                        delivery_type = 'store'
                elif option == "Vendor":
                    delivery_type = 'Vendor_Delivery'
                    district = District.objects.get(id=district_id).district
                    sector = Sector.objects.get(id=sector_id).sector
                    cell = Cell.objects.get(id=cell_id).cell
                    village = Village.objects.get(id=village_id).village
                    product_ids = cart.get_product_ids()
                    vendors = set([p.vendor for p in Product.objects.filter(id__in=product_ids)])
                    vendor_delivery_prices = []
                    for v in vendors:
                        vendor_delivery_prices.extend(v.vendor_delivery.all().values_list('price', flat=True))

                    if vendor_delivery_prices:
                        delivery_cost = float(sum(vendor_delivery_prices))
                else:
                    district = District.objects.get(id=district_id).district
                    sector = Sector.objects.get(id=sector_id).sector
                    cell = Cell.objects.get(id=cell_id).cell
                    village = Village.objects.get(id=village_id).village

                    if option == "Express_Delivery":
                        delivery_cost = 10000
                        delivery_type = 'Express_Delivery'
                    else:
                        delivery_cost = 5000
                        delivery_type = 'Basic_Delivery'

                if is_free_delivery:
                    delivery_cost = 0
                print('check this:')
                print(delivery_type != 'store')
                print(not is_free_delivery)

                # if not is_free_delivery and delivery_type != 'store':

                    # product_ids = cart.get_product_ids()
                    # vendors = set([p.vendor for p in Product.objects.filter(id__in=product_ids)])
                    # vendor_delivery_prices = []
                    # for v in vendors:
                    #     vendor_delivery_prices.extend(v.vendor_delivery.all().values_list('price', flat=True))
                    #
                    # if vendor_delivery_prices:
                    #     delivery_cost = float(sum(vendor_delivery_prices))
                # delivery_cost = payment_service.update_payment_cost(delivery_cost, is_free_delivery, delivery_type, cart)
                cart.add_deliver(district, sector, cell, village, address, delivery_cost, delivery_type)
                return redirect('payment_check')
            else:
                print('go to same page')
                print(form.errors)
                print('---')
        else:
            print('get')

    else:
        return redirect('cart')

    form = CheckoutForm(use_vendor_delivery)

    return render(
        request,
        'cart/contact.html',
        {
            'shopcart': shopcart,
            'sub_total':sub_total,
            'total': total,
            'tax':round(tax,2),
            'grandTotal':round(grandTotal,2),
            'form': form,
            'cart_user': cart_customer,
            'districts': districts,
            'pickup_available': pickup_avaliable,
            'coupon': request.session.get(settings.COUPON_SESSION_ID),
            'use_vendor_delivery': use_vendor_delivery
        }
    )


def district_sector(request):
    district_id = request.GET.get('districtId')
    sectors = Sector.objects.filter(district_id=district_id)

    return JsonResponse(list(sectors.values('id', 'sector')), safe=False)


def district_sector_cell(request):
    district_id = request.GET.get('districtId')
    sector_id = request.GET.get('sectorId')
    cells = Cell.objects.filter(district_id=district_id, sector_id=sector_id)

    return JsonResponse(list(cells.values('id', 'cell')), safe=False)


def district_sector_cell_village(request):
    district_id = request.GET.get('districtId')
    sector_id = request.GET.get('sectorId')
    cell_id = request.GET.get('cellId')
    villages = Village.objects.filter(
        district_id=district_id, sector_id=sector_id, cell_id=cell_id)

    return JsonResponse(list(villages.values('id', 'village')), safe=False)


def payment_check(request, *args, **kwargs):
    cart = Cart(request)
    current_user=request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total=cart.get_cart_cost()
    tax=cart.get_cart_tax()
    grandTotal=cart.get_cart_tax() + cart.get_total_cost()
    if request.method == 'POST':
        form = PaymentForm(request.POST)  # PaymentForm
        if cart.get_delivery_type() == 'store':
            payment_service.make_checkout(request,cart,shopcart)
            return redirect('success')
        elif form.is_valid():
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                amount = cart.get_cart_cost_with_coupen()
                amount += cart.get_delivery_cost()
                try:
                    token = stripe.Token.create(
                        card={
                            "number": form.cleaned_data['card_num'],
                            "exp_month": int(form.cleaned_data['exp_month']),
                            "exp_year": int(form.cleaned_data['exp_year']),
                            "cvc": form.cleaned_data['cvc']
                        },
                    )
                    stripe.Charge.create(
                        amount=int(amount * 100),
                        currency='USD',
                        description='Charge from Warehouse250',
                        source=token
                    )
                except Exception as e:
                    print(e)
                    pass
                payment_service.make_checkout(request, cart,shopcart)
                return redirect('success')
            except Exception as e:
                print(e)
                messages.error(
                    request, 'There was something wrong with the payment')
        else:
            print("invalid")
            print('there invalid')
            print(form.errors)
    else:
        form = PaymentForm()

    return render(
        request,
        'cart/payment.html',
        {
            'form': form,
            'stripe_pub_key': settings.STRIPE_PUB_KEY,
            'coupon': request.session.get(settings.COUPON_SESSION_ID),
            'shopcart': shopcart,
            'total':round(total,2),
            'tax':round(tax,2),
            'grandTotal':round(grandTotal,2),
            'cart':cart
        }
    )


def success(request):
    return render(request, 'cart/success.html')


def check_add_qty(request, product_id, num, *args, **kwargs):
    product = Product.objects.get(id=product_id)
    json_response = {'approved': product.num_available + 1 > num}
    return JsonResponse(json_response)
