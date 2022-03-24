from django.contrib import admin
from .models import *

class ItemsAdmin(admin.ModelAdmin):
    list_display=['title','price','category','available','quantity','unit']
    list_filter=['category']

admin.site.register(Category)
admin.site.register(Item,ItemsAdmin)
