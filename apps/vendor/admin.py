from django.contrib import admin


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Transporter, Vendor, Customer, Profile, VendorDelivery,UserWishList


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton


def company_name(obj):
    return '%s' % (obj.company_name)


company_name.short_description = 'Name'


def company_code(obj):
    return '%s' % (obj.company_code)


company_code.short_description = 'Code'


def vendor_disable(modeladmin, request, queryset):
    for vendor in queryset:
        vendor.enabled = False
        vendor.save()
    return


vendor_disable.short_description = 'Disable'


def vendor_enabled(modeladmin, request, queryset):
    for vendor in queryset:
        vendor.enabled = True
        vendor.save()
    return


vendor_enabled.short_description = 'Enabled'


class VendorInline(admin.TabularInline):
    model = Vendor
    can_delete = False
    verbose_name_plural = 'vendor'


class TransporterInline(admin.StackedInline):
    model = Transporter
    can_delete = False
    verbose_name_plural = 'transporter'


class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = ''

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,VendorInline, CustomerInline,TransporterInline)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customername', company_code,
                    'email', 'address', 'phone', 'created_at']
    ordering = ['customername']
    search_fields = ['customername', 'email', 'address', 'phone']


class TransporterAdmin(admin.ModelAdmin):
    list_display = ['transporter_name', 'number_plate',
                    'email', 'phone', 'created_at']
    ordering = ['transporter_name']
    search_fields = ['transporter_name', 'email', 'address', 'phone']


class VendorAdmin(admin.ModelAdmin):
    list_display = [company_name, company_code, 'email',
                    'address', 'phone', 'created_at', 'enabled']
    ordering = ['company_name']
    search_fields = [company_name, company_code, 'email',
                     'district', 'sector', 'cell', 'village', 'address', 'phone']

    actions = [vendor_disable, vendor_enabled]


class VendorDeliveryAdmin(admin.ModelAdmin):
    pass


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


admin.site.register(Vendor, VendorAdmin)
admin.site.register(VendorDelivery, VendorDeliveryAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Transporter, TransporterAdmin)
admin.site.register(Profile)
admin.register(UserWishList)
