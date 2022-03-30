from django.contrib import admin
from .models import *

class ItemsAdmin(admin.ModelAdmin):
    list_display=['title','price','get_discounted_price','category','available','quantity','unit','visible']
    list_filter=['category']

admin.site.register(Category)
admin.site.register(UnitTypes)
admin.site.register(Item,ItemsAdmin)
