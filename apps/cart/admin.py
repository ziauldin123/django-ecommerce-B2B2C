from django.contrib import admin

# Register your models here.
from .models import District, Sector, Cell, Village

admin.site.register(District)
admin.site.register(Sector)
admin.site.register(Cell)
admin.site.register(Village)
