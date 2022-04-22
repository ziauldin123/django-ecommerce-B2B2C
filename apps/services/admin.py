from doctest import Example
from django.contrib import admin
from .models import Category, Daily_rate,ServiceProvider,Comment,Experience

# Register your models here.

class ServicesAdmin(admin.ModelAdmin):
    list_display = ['service','name','available','review','account']
    list_filter = ['service']

admin.site.register(Category)
admin.site.register(ServiceProvider,ServicesAdmin)
admin.site.register(Comment)
admin.site.register(Experience)
admin.site.register(Daily_rate)