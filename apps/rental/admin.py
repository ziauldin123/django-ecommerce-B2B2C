from django.contrib import admin
from .models import *
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductImageInline(admin.TabularInline):
    model = ItemImage
    readonly_fields = ('id',)
    extra = 1

class ItemsAdmin(admin.ModelAdmin):
    list_display=['title','price','category','item_type','available','quantity','unit','visible']
    list_filter=['category']
    inlines=[ProductImageInline]

admin.site.register(Category)
admin.site.register(UnitTypes)
admin.site.register(Item,ItemsAdmin)
admin.site.register(Make)
admin.site.register(Room)
admin.site.register(Type)
admin.site.register(Application)
admin.site.register(Capacity)
admin.site.register(Amenity)
admin.site.register(Year)
admin.site.register(Engine)
admin.site.register(Item_Model)
admin.site.register(ItemImage)
