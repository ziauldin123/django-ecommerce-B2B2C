from email.mime import image
from pyexpat import model
from tkinter import Widget
from tkinter.tix import Select
from turtle import color, title
from unicodedata import category
from urllib import request
from django.db.models import fields
from django.forms import FileInput, ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import widgets
from jmespath import search
from apps.newProduct.models import *
from .models import  Vendor, Customer, OpeningHours
from apps.cart.models import Village, Cell, Sector, District
from django.urls import reverse_lazy
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from django.views import generic
from django_addanother.contrib.select2 import Select2AddAnother
from django_select2 import forms as s2forms

class CreateLength(CreatePopupMixin, generic.CreateView):
    model = Length
    fields = ['length']

class CreateUnitType(CreatePopupMixin,generic.CreateView):
    model = UnitTypes
    fields = ['name','unit']    

class CreateHeight(CreatePopupMixin, generic.CreateView):
    model = Height
    fields = ['height']

class CreateSize(CreatePopupMixin, generic.CreateView):
    model = Size
    fields = ['name','code']

class CreateBrand(CreatePopupMixin, generic.CreateView):
    model = Brand
    fields = ['brand']

class CreateWeight(CreatePopupMixin, generic.CreateView):
    model = Weight
    fields = ['weight']

class CreateWidth(CreatePopupMixin, generic.CreateView):
    model = Width
    fields = ['width']

class CreateColor(CreatePopupMixin, generic.CreateView):
    model = Color
    fields = ['name','code']
    

class CategoryWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "title__icontains",
    ]

class ProductWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "title__icontains"
    ]


class ProductForm(ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    class Meta:
        model = Product
        fields = (
            'category',
            'title',
            'summary',
            'price',
            'is_vat',
            'quantity',
            'description',
            'discount',
            'color',
            'length',
            'width',
            'weight',
            'size',
            'height',
            'pickup_available',
            'is_free_delivery',
            'image',
            'brand',
            'unit_type',
            'is_vat',
        )
        widgets = {
            'category': CategoryWidget,
            'length':  Select2AddAnother(
                reverse_lazy('add_length'),  
            ),
            'brand':  Select2AddAnother(
                reverse_lazy('add_brand'),
            ),
            'width':  Select2AddAnother(
                reverse_lazy('add_width'),
            ),
            'weight':  Select2AddAnother(
                reverse_lazy('add_weight'),
            ),
            'height':  Select2AddAnother(
                reverse_lazy('add_height'),
            ),
            'size':  Select2AddAnother(
                reverse_lazy('add_size'),
            ),
            'color': Select2AddAnother(
                 reverse_lazy('add_color')
            ),
            'unit_type':Select2AddAnother(
                reverse_lazy('add_unit_type')
            )
        } 
        
    

class ProductWithVariantForm(ModelForm):
    description=forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    class Meta:
        model=Product
        fields=[
            'category',
            'title',
            'summary',
            'description',
            'pickup_available',
            'is_free_delivery',
            'brand',
            'variant',
            'is_vat'
        ]
        widgets = {
        'category': CategoryWidget,
        'brand':  Select2AddAnother(
            reverse_lazy('add_brand'),
        )
    }


class VariantForm(ModelForm):

    class Meta:
        model = Variants
        fields = (
            'title',
            'product',
            'price',
            'discount',
            'quantity',
            'unit_type',
            'image_variant',
            'color',
            'length',
            'width',
            'height',
            'weight',
            'size',
        )
        

        widgets = {
            # 'product': ProductWidget,

            'length':  Select2AddAnother(
                reverse_lazy('add_length'),  
            ),
            'brand':  Select2AddAnother(
                reverse_lazy('add_brand'),
            ),
            'width':  Select2AddAnother(
                reverse_lazy('add_width'),
            ),
            'weight':  Select2AddAnother(
                reverse_lazy('add_weight'),
            ),
            'height':  Select2AddAnother(
                reverse_lazy('add_height'),
            ),
            'size':  Select2AddAnother(
                reverse_lazy('add_size'),
            ),
            'color': Select2AddAnother(
                 reverse_lazy('add_color')
            ),
            'unit_type':Select2AddAnother(
                reverse_lazy('add_unit_type')
            )
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user','')
        super(VariantForm, self).__init__(*args, **kwargs)
        self.fields['product']=forms.ModelChoiceField(queryset=Product.objects.filter(vendor=user,is_variant=True))    


class OpeningHoursForm(ModelForm):
    class Meta:
        model = OpeningHours
        from_hour = forms.TimeField(widget=widgets.AdminTimeWidget)
        to_hour = forms.TimeField(widget=widgets.AdminTimeWidget)
        fields = ['weekday', 'from_hour', 'to_hour']


class ProductImageForm(ModelForm):
    class Meta:
        model = ProductImage
        fields = [
            'image',
            ]


# Vendor Sign Up Form
class VendorSignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=64, required=True)
    company_code = forms.CharField(max_length=64, required=True)
    district = forms.ChoiceField(choices=[
                                 (-1, '')] + [(entry.id, entry.district) for entry in District.objects.all()])
    print("district", district)

    sector = forms.ChoiceField(
        choices=[(-1, '')] + [(entry.id, entry.sector) for entry in Sector.objects.all()])
    print("sector", sector)

    cell = forms.ChoiceField(
        choices=[(-1, '')] + [(entry.id, entry.cell) for entry in Cell.objects.all()])
    print("cell", cell)

    village = forms.ChoiceField(
        choices=[(-1, '')] + [(entry.id, entry.village) for entry in Village.objects.all()])
    print("village", village)
    address = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 2, 'cols': 85}), max_length=170)
    phone = forms.CharField(max_length=32, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'company_name',
            'company_code',
            'address',
            'phone',
        ]

# Customer Sign Up Form


class RestorePasswordForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


class RequestRestorePasswordForm(forms.Form):
    email = forms.EmailField()


class CustomerSignUpForm(UserCreationForm):
    customername = forms.CharField(max_length=32)
    address = forms.CharField(max_length=64, required=True)
    phone = forms.CharField(max_length=32, required=True)
    company_code = forms.CharField(max_length=32,required=False)
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'customername',
            'address',
            'phone',
            'company_code'
        ]


class TransporterSignUpForm(UserCreationForm):
    transporter_name=forms.CharField(max_length=32)
    phone=forms.CharField(max_length=10,required=True)
    number_plate=forms.CharField(max_length=155)
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'transporter_name',
            'phone',
            'number_plate',
        ]