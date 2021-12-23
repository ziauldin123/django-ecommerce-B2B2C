import datetime
from django.contrib import admin


# Register your models here.
from apps.ordering.models import ShopCart, Order, OrderItem,TransporterOrder
# from .models import *

# Register your models here.
def admin_order_shipped(modeladmin, request, queryset):
    for order in queryset:
        order.shipped_date = datetime.datetime.now()
        order.status = Order.SHIPPED
        order.save()
    return


admin_order_shipped.short_description = 'Set shipped'


def admin_order_arrived(modeladmin, request, queryset):
    for order in queryset:
        order.arrived_date = datetime.datetime.now()
        order.status = Order.ARRIVED
        order.save()
    return


admin_order_arrived.short_description = 'Set arrived'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']



def product(obj):
    if obj.product:
        return '%s' % (obj.product.title)
    else:
        return '%s' % ("-")
def vendor_name(obj):
    if obj.product:
        return '%s' % (obj.product.vendor.company_name)
    else:
        return '%s' % ("-")
def vendor_address(obj):
    if obj.product:
        return '%s' % (obj.product.vendor.address)
    else:
        return '%s' % ("-")
def customer_name(obj):
    if obj.order:
        return '%s %s' % (obj.order.first_name, obj.order.last_name)
    else:
        return '%s' % ("-")
def customer_address(obj):
    if obj.order:
        return '%s, %s, %s, %s, %s' % (obj.order.address,obj.order.district,obj.order.sector,obj.order.village,obj.order.cell)
    else:
        return '%s' % ("-")
def customer_phone(obj):
    if obj.order:
        return '%s' % (obj.order.phone)
    else:
        return '%s' % ("-")

class TransporterOrderAdmin(admin.ModelAdmin):
    list_display = ['id', product, 'status','transporter','quantity',vendor_name,vendor_address,customer_name,customer_address,customer_phone]
    list_filter = ['status',]
    # search_fields = ['first_name', 'address']
    # inlines = [OrderItemInline]
    # actions = [admin_order_shipped, admin_order_arrived]

admin.site.register(TransporterOrder, TransporterOrderAdmin)