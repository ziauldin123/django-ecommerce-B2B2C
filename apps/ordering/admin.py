import datetime
from django.contrib import admin


# Register your models here.
from apps.ordering.models import ShopCart, Order, OrderItem, Quotation

class ShopCartAdmin(admin.ModelAdmin):
    list_display=['product','user','quantity','price','var_dicount_amount','prodct_dicount_amount']
    list_filter=['user']

def order_name(obj):
    return '%s %s' % (obj.first_name, obj.last_name)


order_name.short_description = 'Name'

class QuatationAdmin(admin.ModelAdmin):
    list_display=['reference_number','product','user','vendor','quantity','created_at']

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


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', order_name, 'status', 'created_at']
    list_filter = ['created_at', 'status']
    search_fields = ['first_name', 'address']
    inlines = [OrderItemInline]
    actions = [admin_order_shipped, admin_order_arrived]

admin.site.register(ShopCart,ShopCartAdmin)
admin.site.register(Quotation,QuatationAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)