from django.db import models
from django.db.models.base import Model
import admin_thumbnails
from django.contrib import admin
from django.contrib.admin import TabularInline, register

from .models import Category,  Color, Product,ProductImage,   Size, SubCategory, SubSubCategory, ProductVariant


class ProductChildsInline(TabularInline):
    model = Product



@register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ ProductChildsInline]

# class ProductVariantsInline(admin.TabularInline):
#     model = ProductVariant
#     readonly_fields = ('image_tag',)
#     extra = 1
#     show_change_link = True

# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['title','category', 'status','image_tag']
#     list_filter = ['category']
#     readonly_fields = ('image_tag',)
#     inlines = [ProductVariantsInline]
#     prepopulated_fields = {'slug': ('title',)}



# class ProductInline(TabularInline):
#     model = ProductCollection
#     fk_name = 'collection'




# @register(Collection)
# class CollectionAdmin(admin.ModelAdmin):
#     inlines = [ProductInline]


class colorAdmin(admin.ModelAdmin):
    model=Color
    list_display=['name','code','color_tag']

class sizeAdmin(admin.ModelAdmin):
    list_display=['name','code']

class variantAdmin(admin.ModelAdmin):
    list_display=['title','product','color','size','price','quantity','image_tag']

class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image','title','image_thumbnail']

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(ProductImage)
# admin.site.register(Product)
admin.site.register(SubSubCategory)
admin.site.register(Color,colorAdmin)
admin.site.register(Size,sizeAdmin)
# admin.site.register(ProductImage,ImagesAdmin)
# admin.site.unregister(Vendor)
# admin.site.register(Vendor,VendorAdmin)
admin.site.register(ProductVariant,variantAdmin)