from django.conf import settings

from apps.cart.cart import Cart
from apps.order.utilities import checkout
from apps.newProduct.models import Product, Variants
from apps.ordering.models import Order,OrderItem,ShopCart,notify_customer,notify_vendor


class PaymentService:
    def make_checkout(self, request, cart: Cart, shop_cart,service_provider,momo):
        first_name = request.user.customer.customername.split(' ')[0]
        if len(request.user.customer.customername.split(' ')) > 1:
            last_name = request.user.customer.customername.split(' ')[
                1]
        else:
            last_name = ""

        s_coupon = request.session.get(settings.COUPON_SESSION_ID)
        if not s_coupon:
            s_coupon = request.session[settings.COUPON_SESSION_ID] = {}
            s_coupon["code"] = ""
            s_coupon["discount"] = ""




        email = request.user.customer.email
        phone = request.user.customer.phone
        address = request.user.customer.address
        company_code = request.user.customer.company_code
        service_provider=service_provider
        momo=momo
        district = cart.cart['delivery']['district']
        sector = cart.cart['delivery']['sector']
        cell = cart.cart['delivery']['cell']
        village = cart.cart['delivery']['village']
        delivery_address = cart.cart['delivery']['address']
        delivery_cost = cart.cart['delivery']['cost']
        delivery_type=cart.cart['delivery']['delivery_type']
        is_paid_now = True if request.POST.get('pay_now') else False
        order = checkout(request,cart, first_name, last_name, email,address, phone,company_code,service_provider,momo,district,
                         sector, cell, village, delivery_address, delivery_cost,delivery_type,cart.get_cart_cost(),
                         request.session.get(settings.COUPON_SESSION_ID)["code"], is_paid_now,cart.get_cart_tax(),cart.get_cart_cost())

        if s_coupon:
            s_coupon = request.session[settings.COUPON_SESSION_ID] = {}
            s_coupon["code"] = ""
            s_coupon["discount"] = ""

        product_ids = [k for k in cart.cart['cart'].keys() if k != 'delivery']
        for p_id in product_ids:
            qty = cart.cart['cart'][p_id]['quantity']
            is_variant=cart.cart['cart'][p_id]['product']['is_variant']
            if is_variant:
                variant_id=cart.cart['cart'][p_id]['product']['variant_id']['id']
                variant = Variants.objects.get(id=variant_id)
                variant.quantity = variant.quantity - qty
                variant.save()
            else:
                product_id=cart.cart['cart'][p_id]['product']['id']
                product = Product.objects.get(id=product_id)
                product.quantity = product.quantity - qty
                product.save()

        print('reduce num available done')
        cart.clear()
        shop_cart.all().delete()

        return order

    def update_payment_cost(self, delivery_cost, is_free_delivery, delivery_type, cart: Cart):
        if is_free_delivery:
            return delivery_cost
        if delivery_type == 'store':
            return delivery_cost
        elif delivery_type == "Vendor":
            return delivery_cost



        product_ids = cart.get_product_ids()
        vendors = set([p.vendor for p in Product.objects.filter(id__in=product_ids)])

        empty_custom_delivery_added = False
        vendor_delivery_prices = []
        for v in vendors:
            custom_delivery_price = v.vendor_delivery.all().values_list('price', flat=True)
            if not custom_delivery_price and not empty_custom_delivery_added:
                empty_custom_delivery_added = True
                vendor_delivery_prices.append(delivery_cost)

            vendor_delivery_prices.extend(custom_delivery_price)

        if vendor_delivery_prices:
            delivery_cost = float(sum(vendor_delivery_prices))

        return delivery_cost


payment_service = PaymentService()
