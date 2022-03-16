from pyexpat import model
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.db import models
from django.db.models.base import Model
import admin_thumbnails
from django.contrib import admin
from django.contrib.admin import TabularInline, register

from mptt.admin import DraggableMPTTAdmin
# Register your models here.

from .models import *

class CategoryAdmin(DraggableMPTTAdmin):
    mptt_intend_field="title"
    list_display=('tree_actions','indented_title','related_products_count','related_products_cumulative_count')
    list_display_links = ('indented_title',)
    populated_fields={'slug':('title',)}
    def get_queryset(self,request):
        qs=super().get_queryset(request)

        qs=SubSubCategory.objects.add_related_count(
            qs,
            Product,
            'category',
            'products_cumulative_count',
            cumulative=True
        )

        qs=SubSubCategory.objects.add_related_count(
            qs,
            Product,
            'category',
            'products_count',
            cumulative=False
        )
        return qs
    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description='Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description='Related products (in tree)'

# @admin_thumbnails.thumbnail('image')
# class ProductImageInline(admin.TabularInline):
#     model=Images
#     readonly_fields = ('id',)
#     extra = 1

class ProductInline(TabularInline):
    model = ProductCollection
    fk_name = 'collection'


@register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    inlines = [ProductInline]

@admin_thumbnails.thumbnail('image')
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    readonly_fields = ('id',)
    extra = 1

@admin_thumbnails.thumbnail('image')
class VariantImageInline(admin.TabularInline):
    model = ProductImage
    readonly_fields = ('id',)
    extra = 1

class ProductVariantsInline(admin.TabularInline):
    model=Variants
    readonly_fields=['image_tag']
    extra = 1
    show_change_link = True

class UnitTypesAdmin(admin.ModelAdmin):
    list_display=['name','unit']

class BrandAdmin(admin.ModelAdmin):
    list_display=['brand',]



@admin_thumbnails.thumbnail('image')
class ImagesAdmin(admin.ModelAdmin):
    list_display=['image','name','image_thumbnail']

class ProductAdmin(admin.ModelAdmin):
    list_display=['title','category','status','pickup_available','is_vat','discount','price','get_discounted_price','get_vat_price','get_vat_exclusive_price']
    list_filter=['category']
    # readonly_fields=['image_tag']
    inlines=[ProductVariantsInline,ProductImageInline]
    prepopulated_fields={'slug':('title',)}

class VariantAdmin(admin.ModelAdmin):
    list_display=['title','product','color','image_variant','size','discount','price','get_discounted_price','get_vat_price','get_vat_exclusive_price','quantity']
    inlines=[VariantImageInline]
    list_filter=['product']

class sizeAdmin(admin.ModelAdmin):
    list_display=['name','code']

class colorAdmin(admin.ModelAdmin):
    list_display=['name','code','color_tag']

class LengthAdmin(admin.ModelAdmin):
    list_display=['length']

class WidthAdmin(admin.ModelAdmin):
    list_display=['width']

class WeightAdmin(admin.ModelAdmin):
    list_display=['weight']

class HeightAdmin(admin.ModelAdmin):
    list_display=['height']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['subject','comment', 'status','create_at']
    list_filter = ['status']
    readonly_fields = ('subject','comment','ip','user','product','rate','id')

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['image','title','image_tag','variant','product']

admin.site.register(Size,sizeAdmin)
admin.site.register(Color,colorAdmin)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(SubSubCategory,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Variants,VariantAdmin)
admin.site.register(Images,ImagesAdmin)
admin.site.register(Length,LengthAdmin)
admin.site.register(Width,WidthAdmin)
admin.site.register(Weight,WeightAdmin)
admin.site.register(Height,HeightAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(UnitTypes,UnitTypesAdmin)
admin.site.register(Brand,BrandAdmin)
admin.site.register(ProductImage,ProductImageAdmin)