from django import template

from apps import vendor
from ...ordering.models import *
from ..models import *

register = template.Library()


@register.simple_tag
def get_total_order_cost(order, user):
    v=Vendor.objects.get(email=user)
    vendor=v
    total_cost=0
    vendor_item_price=0
    vendor_items_total_price=0
    total_quantity=0
    delivery_cost=0

    orderItems=order.items.filter(vendor_id=v.id).all()
    for items in orderItems:
        vendor_items_total_price += items.get_total()
        total_quantity = items.quantity
        if not items.product.is_free_delivery:
            if order.delivery_type == "Vendor_Delivery":
                delivery_cost=VendorDelivery.objects.get(vendor=vendor).price
                is_delivery=True
                if delivery_cost == None:
                    delivery_cost=False
            else:
                delivery_cost=0
                is_delivery=False
    total_cost=float(vendor_items_total_price-(order.coupon_discount*vendor_items_total_price/100))
    total_cost+=float(delivery_cost)

    return round(Decimal(total_cost),2)


@register.simple_tag
def get_total_paid_balance(user):
    v=Vendor.objects.get(email=user)
    vendor=v
    total_cost=0
    vendor_item_price=0
    vendor_items_total_price=0
    total_quantity=0
    delivery_cost=0

    orders=Order.objects.filter(vendors__id=v.id).all()
    for i in orders:
        orderItems=i.items.filter(vendor_id=v.id).all()
        for items in orderItems:
            if items.vendor_paid:
                vendor_item_price=items.get_total()
                vendor_items_total_price = vendor_item_price
                total_quantity = items.quantity
                if not items.product.is_free_delivery:
                    if i.delivery_type == "Vendor_Delivery":
                        delivery_cost=VendorDelivery.objects.get(vendor=vendor).price
                        is_delivery=True
                        if delivery_cost == None:
                            delivery_cost=False
                    else:
                        delivery_cost=0
                        is_delivery=False
                total_cost+=float(vendor_items_total_price-((i.coupon_discount*vendor_items_total_price)/100))
                total_cost+=float(delivery_cost)

    return round(Decimal(total_cost),2)

@register.simple_tag
def get_total_balance(user):
    v=Vendor.objects.get(email=user)
    vendor=v
    total_cost=0
    vendor_item_price=0
    vendor_items_total_price=0
    total_quantity=0
    delivery_cost=0

    orders=Order.objects.filter(vendors__id=v.id).all()
    for i in orders:
        orderItems=i.items.filter(vendor_id=v.id).all()
        for items in orderItems:
            if not items.vendor_paid:
                vendor_item_price=items.get_total()
                vendor_items_total_price = vendor_item_price
                total_quantity = items.quantity
                if not items.product.is_free_delivery:
                    if i.delivery_type == "Vendor_Delivery":
                        delivery_cost=VendorDelivery.objects.get(vendor=vendor).price
                        is_delivery=True
                        if delivery_cost == None:
                            delivery_cost=False
                    else:
                        delivery_cost=0
                        is_delivery=False
                total_cost+=float(vendor_items_total_price-((i.coupon_discount*vendor_items_total_price)/100))
                total_cost+=float(delivery_cost)

    return round(Decimal(total_cost),2)


@register.simple_tag
def get_total_with_coupon(order,price, user):
    v=Vendor.objects.get(email=user)
    vendor=v
    total_cost=0
    total_cost=float(price-(order.coupon_discount*price/100))

    return round(Decimal(total_cost),2)

@register.simple_tag()
def get_order_delivery_cost(order,user):
    v=Vendor.objects.get(email=user)
    vendor=v
    if order.delivery_type == "Vendor_Delivery":
        delivery_cost=VendorDelivery.objects.get(vendor=vendor).price
    else:
        delivery_cost=0
    return round(Decimal(delivery_cost),2)


