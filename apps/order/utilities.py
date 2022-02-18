from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from decimal import Decimal

from apps.cart.cart import Cart
from apps.newProduct.models import Product, Variants

# from .models import Order, OrderItem
from apps.ordering.models import Order, OrderItem
from apps.coupon.models import Coupon
from ..vendor.models import Transporter, Vendor, VendorDelivery
from apps.vendor.services.account_service import account_service


def checkout(
    request,
    cart,
    first_name,
    last_name,
    email,
    address,
    phone,
    company_code,
    momo,
    district,
    sector,
    cell,
    village,
    delivery_address,
    delivery_cost,
    delivery_type,
    cart_cost,
    coupon_code,
    is_paid_now,
    vat_cost,
    subtotal
):
    print(" === coupon code = ", coupon_code)
    coupon_discount = 0
    if coupon_code != "":
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.can_use():
                coupon.use()
                coupon_discount = coupon.discount
        except:
            pass

    try:

        print("before calc: ", type(delivery_cost),
              type(cart_cost), type(coupon_discount))
        paid_amount = Decimal(delivery_cost) + \
            Decimal(cart_cost) * (100 - coupon_discount) / 100
        paid_amount = cart.get_cart_cost_with_coupen()
        print("paid amount = ", paid_amount)
        
        vat_cost = 0
        subtotal = 0

        for item in Cart(request):
            vat_cost += Decimal(item['tax'])
            vat = round(Decimal(vat_cost), 2)
            subtotal += Decimal(item['product']
                                       ['total_price'] * item['quantity'])
            subtotal = round(Decimal(subtotal), 2)

        print(vat_cost)
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            phone=phone,
            company_code=company_code,
            momo=momo,
            district=district,
            sector=sector,
            cell=cell,
            village=village,
            delivery_address=delivery_address,
            delivery_cost=delivery_cost,
            delivery_type=delivery_type,
            paid_amount=paid_amount,
            vat=vat_cost,
            subtotal=subtotal,
            used_coupon=coupon_code,
            coupon_discount=coupon_discount,
            is_paid=is_paid_now
        )

        total_quantity = 0
        subtotal_amount = 0
        price_no_vat = 0
        vat = 0
        print("checkout")

        for item in Cart(request):

            total_quantity += item['quantity']
            price_no_vat += Decimal(item['total_vat_excl'])
            price_no_vat = round(Decimal(price_no_vat), 2)
            vat += Decimal(item['tax'])
            vat = round(Decimal(vat), 2)
            print("quantity in cart")
            print(total_quantity)
            subtotal_amount += Decimal(item['product']
                                       ['total_price'] * item['quantity'])
            subtotal_amount = round(Decimal(subtotal_amount), 2)
            if item['product']['is_variant']:
                var_id = int(item['product']['variant_id']['id'])
                pro_id = int(item['product']['id'])
                print(pro_id)
            else:
                pro_id = int(item['product']['id'])
                var_id = ''

            OrderItem.objects.create(
                order=order,
                product_id=pro_id,
                variant_id=var_id,
                vendor_id=item['product']['vendor_id']['id'],
                price=item['product']['total_price'],
                quantity=item['quantity'],
                is_variant=item['product']['is_variant']
            )
            vendor = Vendor.objects.get(pk=item['product']['vendor_id']['id'])
            order.vendors.add(vendor)

        order.total_quantity = total_quantity
        order.price_no_vat = price_no_vat
        order.vat = vat
        order.subtotal_amount = subtotal_amount
        if order.is_paid:
            notify_vendor(order)
            notify_customer(order, request)
        
    except Exception as e:
        raise e

    return order



