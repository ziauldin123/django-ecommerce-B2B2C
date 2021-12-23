# import datetime

# from django.urls import reverse
# from django.contrib import admin

# from .models import Order, OrderItem
# from django.db.models import Subquery, Sum, OuterRef


# def order_name(obj):
#     return '%s %s' % (obj.first_name, obj.last_name)


# order_name.short_description = 'Name'


# def admin_order_shipped(modeladmin, request, queryset):
#     for order in queryset:
#         order.shipped_date = datetime.datetime.now()
#         order.status = Order.SHIPPED
#         order.save()
#     return


# admin_order_shipped.short_description = 'Set shipped'


# def admin_order_arrived(modeladmin, request, queryset):
#     for order in queryset:
#         order.arrived_date = datetime.datetime.now()
#         order.status = Order.ARRIVED
#         order.save()
#     return


# admin_order_arrived.short_description = 'Set arrived'


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     raw_id_fields = ['product']


# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', order_name, 'status', 'created_at']
#     list_filter = ['created_at', 'status']
#     search_fields = ['first_name', 'address']
#     inlines = [OrderItemInline]
#     actions = [admin_order_shipped, admin_order_arrived]

#     # def get_queryset(self, request):
#     #     qs = super(OrderAdmin, self).get_queryset(request)
#     #     qs = qs.annotate(
#     #         id = "",
#     #         order_name = "total",
#     #         # status = Subquery(FinishedGoodsItem.objects.filter(goods_item=OuterRef('pk'))\
#     #         #     .values('goods_item_id').annotate(sum=Sum('weight')).values('sum')[:1]),
#     #         status = "",
#     #         created_at = "",
#     #     )
#     #     return qs


# admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem)
