from typing import List

from django.conf import settings

# from apps.product.models import Product
from apps.newProduct.models import Product
from apps.ordering.models import ShopCart
from decimal import Decimal
import json
from django.forms.models import model_to_dict
from django.core import serializers
from django.db.models.query import QuerySet

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        # print("Cart data")
        print(cart)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {'cart':{}}

        self.cart = cart
        null_id=[]
        for p in self.cart['cart'].keys():
            shopcart = ShopCart.objects.filter(pk=int(p)).first()
            if shopcart:
                self.cart['cart'][str(p)]['product'] = {'id': shopcart.product.id}
                self.cart['cart'][str(p)]['product']['category_slug'] = shopcart.product.category.slug
                self.cart['cart'][str(p)]['product']['subcategory_slug'] = shopcart.product.category.sub_category.slug
                self.cart['cart'][str(p)]['product']['subsubcategory_slug'] = shopcart.product.category.sub_category.category.slug
                self.cart['cart'][str(p)]['product']['slug'] = shopcart.product.slug
                self.cart['cart'][str(p)]['product']['vendor_id'] = shopcart.product.vendor.id
                self.cart['cart'][str(p)]['product']['slugV']=shopcart.product.slugV
                self.cart['cart'][str(p)]['product']['pickup_available'] = shopcart.product.pickup_available
                if shopcart.variant == None :
                    self.cart['cart'][str(p)]['product']['total_price'] = float(shopcart.product.get_discounted_price())
                    self.cart['cart'][str(p)]['product']['is_variant'] = False
                else:
                    self.cart['cart'][str(p)]['product']['total_price'] = float(shopcart.variant.get_discounted_price())
                    self.cart['cart'][str(p)]['product']['is_variant'] = True
                    self.cart['cart'][str(p)]['product']['variant_id'] = shopcart.variant.id

                self.cart['cart'][str(p)]['product']['is_free_delivery'] = shopcart.product.is_free_delivery
                self.cart['cart'][str(p)]['product']['get_thumbnail'] = shopcart.product.get_thumbnail()
                self.cart['cart'][str(p)]['product']['title'] = shopcart.product.title
            else:
                null_id.append(p)

        for item in null_id:
            del self.cart['cart'][item]


        for item in self.cart['cart'].values():
            if 'product' in item:
                item['total_price'] = float(item['product']['total_price'] * item['quantity'])


    def __iter__(self):
        null_id=[]
        for p in self.cart['cart'].keys():
            shopcart = ShopCart.objects.filter(pk=int(p)).first()
            if shopcart:
                self.cart['cart'][str(p)]['product'] = {'id': shopcart.product.id}
                self.cart['cart'][str(p)]['product']['category_slug'] = shopcart.product.category.slug
                self.cart['cart'][str(p)]['product']['subcategory_slug'] = shopcart.product.category.sub_category.slug
                self.cart['cart'][str(p)]['product']['subsubcategory_slug'] = shopcart.product.category.sub_category.category.slug
                self.cart['cart'][str(p)]['product']['slug'] = shopcart.product.slug
                self.cart['cart'][str(p)]['product']['vendor_id'] = shopcart.product.vendor.id
                self.cart['cart'][str(p)]['product']['slugV']=shopcart.product.slugV
                self.cart['cart'][str(p)]['product']['pickup_available'] = shopcart.product.pickup_available
                if shopcart.variant == None :
                    self.cart['cart'][str(p)]['product']['total_price'] = float(shopcart.product.get_discounted_price())
                    self.cart['cart'][str(p)]['product']['is_variant'] = False
                else:
                    self.cart['cart'][str(p)]['product']['total_price'] = float(shopcart.variant.get_discounted_price())
                    self.cart['cart'][str(p)]['product']['is_variant'] = True
                    self.cart['cart'][str(p)]['product']['variant_id'] = shopcart.variant.id

                self.cart['cart'][str(p)]['product']['is_free_delivery'] = shopcart.product.is_free_delivery
                self.cart['cart'][str(p)]['product']['get_thumbnail'] = shopcart.product.get_thumbnail()
                self.cart['cart'][str(p)]['product']['title'] = shopcart.product.title
            else:
                null_id.append(p)
        for item in null_id:
            del self.cart['cart'][item]


        for item in self.cart['cart'].values():
            if 'product' in item:
                item['total_price'] = float(item['product']['total_price'] * item['quantity'])

                yield item

    def __len__(self):
        sum_quantity = 0
        for item in self.cart['cart'].values():
            if 'quantity' in item:
                sum_quantity += item['quantity']
        return sum_quantity

    def add(self, product_id,user_id, quantity, update_quantity=False):
        cart_data=ShopCart.objects.filter(product_id=product_id, user_id=user_id).first()
        if cart_data:
            cart_id=str(cart_data.id)

        if cart_id not in self.cart['cart']:
            self.cart['cart'][cart_id] ={'quantity': cart_data.quantity,'id':str(cart_data.id)}

        if cart_id in self.cart['cart']:
            self.cart['cart'][cart_id] ={'quantity': cart_data.quantity}



        self.save()

    def add_coupon(self, coupon_code,coupon_discount):

        self.cart['coupon_code'] = coupon_code
        self.cart['coupon_discount'] = coupon_discount

        self.save()

    def get_coupon_discount(self):
        return self.cart.get('coupon_discount')

    def set(self, product_id, quantity=1):
        product_id = str(product_id)
        self.cart['products']={product_id:{'quantity' : int(quantity)}}

        if self.cart['products'][product_id]['quantity'] == 0:
            self.remove(product_id)

        self.save()
    def delete_product(self,shopcart_id):

        self.remove(shopcart_id)

    def add_deliver(self, district, sector, cell, village, address, cost, delivery_type) -> None:
        self.cart['delivery'] = {
            'district': district,
            'sector': sector,
            'cell': cell,
            'village': village,
            'address': address,
            'cost': cost,
            'delivery_type': delivery_type
        }
        self.save()

    def get_delivery_address(self) -> str:
        delivery = self.cart['delivery']

        delivery_list = []
        if delivery.get('district'):
            delivery_list.append(delivery.get('district'))
        if delivery.get('sector'):
            delivery_list.append(delivery.get('sector'))
        if delivery.get('cell'):
            delivery_list.append(delivery.get('cell'))
        if delivery.get('village'):
            delivery_list.append(delivery.get('village'))
        if delivery.get('address'):
            delivery_list.append(delivery.get('address'))

        address = ' - '.join(delivery_list)
        return address

    def get_delivery_type(self):
        delivery = self.cart.get('delivery')
        if delivery:
            return delivery.get('delivery_type')
        return

    def has_product(self, product_id):
        if str(product_id) in self.cart['products']:
            return True
        else:
            return False

    def remove(self,shopcart_id):

        shopcart_id=str(shopcart_id)


        if shopcart_id in self.cart['cart']:
            del self.cart['cart'][shopcart_id]

        for p in list(self.cart):
            print(p)
            if p == 'coupon_code':
                del self.cart['coupon_code']
                del self.cart['coupon_discount']
        for p in list(self.cart):
            print(p)
            if p == 'delivery':
                del self.cart['delivery']

        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_is_vendor_delivery(self):
        is_vendor_delivery=[]
        is_pickup_avaliable=[]
        for item in self.cart['cart']:
            p_id=self.cart['cart'][str(item)]['product']['id']
            product = Product.objects.get(pk=p_id)
            is_vendor_delivery.append(product.vendor.vendor_delivery.all().count() == 1)
            is_pickup_avaliable.append(self.cart['cart'][str(item)]['product']['pickup_available'])
            # if product.vendor.vendor_delivery.all().count() == 0:
            #     use_vendor_delivery = False
            # pickup_avaliable = self.cart['cart'][str(item)]['product']['pickup_available']

        print(is_vendor_delivery)
        print(is_pickup_avaliable)
        if all(is_vendor_delivery):
            use_vendor_delivery=True
        else:
            use_vendor_delivery=False

        if all(is_pickup_avaliable):
            pickup_avaliable=True
        else:
            pickup_avaliable=False
        print("option",use_vendor_delivery,pickup_avaliable)
        return use_vendor_delivery,pickup_avaliable

    def get_delivery_cost(self):
        if "delivery" in self.cart:
            print(" delivery - 1")
            if self.cart['delivery']['cost']:
                print(" delivery - 2 *", self.cart['delivery']['cost'], "#")
        if "delivery" in self.cart and self.cart['delivery']['cost']:
            return round(Decimal(self.cart['delivery']['cost']),2)
        return 0

    def get_product_ids(self) -> List[str]:
        product_ids=[]
        for p in self.cart['cart'].keys():
            shopcart = ShopCart.objects.filter(pk=int(p)).first()
            if shopcart:
                 product_ids.append(shopcart.product.id)
        return product_ids
        # return [int(p) for p in self.cart['cart'].keys()]

    def get_cart_cost(self):
        for p in self.cart['cart'].keys():

            # product = Product.objects.get(pk=p)
            shopcart = ShopCart.objects.filter(pk=int(p)).first()
            if shopcart:
                self.cart['cart'][str(p)]['product']['id'] = shopcart.product.id
                self.cart['cart'][str(p)]['product']['total_cost'] = self.cart['cart'][str(p)]['product']['total_price']

        total_cost = 0
        for item in self.cart['cart'].values():
            if 'product' in item:
                total_cost += float(item['product']['total_cost'] * item['quantity'])

        total_cost=Decimal(total_cost)

        return round(total_cost,2)

    def get_cart_cost_with_coupen(self):
        for p in self.cart['cart'].keys():

            shopcart = ShopCart.objects.filter(pk=int(p)).first()
            if shopcart:
                self.cart['cart'][str(p)]['product']['id'] = shopcart.product.id
                self.cart['cart'][str(p)]['product']['total_cost'] = self.cart['cart'][str(p)]['product']['total_price']

        total_cost = 0
        for item in self.cart['cart'].values():
            if 'product' in item:
                total_cost += float(item['product']['total_cost'] * item['quantity'])



        if 'coupon_discount' in list(self.cart):
            coupon_discount=self.cart.get('coupon_discount')
            total_cost= float(total_cost-(coupon_discount*total_cost/100))
            total_cost=Decimal(total_cost)
        total_cost=Decimal(total_cost)
        return round(total_cost,2)


    def get_total_cost(self):
        for p in self.cart['cart'].keys():
            if p != 'delivery':
                shopcart = ShopCart.objects.filter(pk=int(p)).first()
                if shopcart:
                    self.cart['cart'][str(p)]['product']['id'] = shopcart.product.id
                    self.cart['cart'][str(p)]['product']['total_cost'] = self.cart['cart'][str(p)]['product']['total_price']
                    # self.cart[str(p)]['product']['delivery_cost'] = float(sum(product.vendor.vendor_delivery.all().values_list('price', flat=True)))
                    self.cart['cart'][str(p)]['product']['delivery_cost'] = self.cart['delivery']['cost']

        total_cost = 0
        for item in self.cart['cart'].values():
            if 'product' in item:
                total_cost += float(item['product']['total_cost'] * item['quantity'])
                # total_cost += float(item['product']['delivery_cost'])

        coupon_discount=self.cart.get('coupon_discount')
        if coupon_discount:
            total_cost= float(total_cost-(coupon_discount*total_cost/100))

        if "delivery" in self.cart and self.cart['delivery']['cost']:
            total_cost += float(self.cart['delivery']['cost'])
            total_cost=Decimal(total_cost)
        total_cost=Decimal(total_cost)
        return round(total_cost,2)


