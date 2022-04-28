from dataclasses import field
from pyexpat import model
from unicodedata import category
from django.forms import ModelForm
from .models import Amenity, Item,Make,Room,Application,Capacity,Year,Engine,Amenity,Item_Model
from django import forms

from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from django.views import generic
from django_addanother.contrib.select2 import Select2AddAnother
from django.urls import reverse_lazy


class CreateMake(CreatePopupMixin, generic.CreateView):
    model = Make
    fields = ['make']

class CreateRoom(CreatePopupMixin, generic.CreateView):
    model = Room
    fields = ['room']
class CreateApplication(CreatePopupMixin, generic.CreateView):
    model = Application
    fields = ['application']
class CreateCapacity(CreatePopupMixin, generic.CreateView):
    model = Capacity
    fields = ['capacity']
class CreateEngine(CreatePopupMixin, generic.CreateView):
    model = Engine
    fields = ['engine']
class CreateAmenity(CreatePopupMixin, generic.CreateView):
    model = Amenity
    fields = ['amenity']
class CreateYear(CreatePopupMixin, generic.CreateView):
    model = Year
    fields = ['year']
class CreateItemModel(CreatePopupMixin, generic.CreateView):
    model = Item_Model
    fields = ['model']

class ItemForm(ModelForm):
    
    class Meta:
        model = Item
        fields = (
            'title',
            'description',
            'price',
            'category',
            'makes',
            'rooms',
            'application',
            'capacity',
            'sale',
            'year',
            'engine',
            'amenity',
            'model',
            'item_type',
            'quantity',
            'available',
            'image',
            'unit',
            'price',
        )
        widgets = {
           'category':forms.Select(attrs={'id':'category'}),
            'makes':  Select2AddAnother(
                reverse_lazy('add_make'),  
            ),
            'rooms':  Select2AddAnother(
                reverse_lazy('add_rooms'),  
            ),
            'application':  Select2AddAnother(
                reverse_lazy('add_application'),  
            ),
            'capacity':  Select2AddAnother(
                reverse_lazy('add_capacity'),  
            ),
            'year':  Select2AddAnother(
                reverse_lazy('add_year'),  
            ),
            'engine':  Select2AddAnother(
                reverse_lazy('add_engine'),  
            ),
            'amenity':  Select2AddAnother(
                reverse_lazy('add_amenity'),  
            ),
            'model':  Select2AddAnother(
                reverse_lazy('add_model'),  
            )
        }

class SearchForm(forms.Form):
    def __init__(self,*args,**kwargs):
        items = kwargs.pop('items') if kwargs.get('items') is not None else Item.objects.all()
        super().__init__(*args,**kwargs)

    query = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class':'input'}),required=False)
    price_from = forms.BooleanField(initial=0,required=False,widget=forms.TextInput(attrs={'class':'input'}))
    price_to = forms.IntegerField(initial=5000000, required=False,widget=forms.TextInput(attrs={'class':'input'}))
    location = forms.CharField(widget=forms.Select(),required=False)
    make = forms.CharField(widget=forms.Select(),required=False)
    room = forms.CharField(widget=forms.Select(),required=False)
    application = forms.CharField(widget=forms.Select(),required=False)
    capacity = forms.CharField(widget=forms.Select(),required=False)
    amenity = forms.CharField(widget=forms.Select(),required=False)
    year = forms.CharField(widget=forms.Select(),required=False)
    model = forms.CharField(widget=forms.Select(),required=False)
    engine = forms.CharField(widget=forms.Select(),required=False)
    item_type = forms.CharField(widget=forms.Select(),required=False)
    sale = forms.CharField(widget=forms.Select(),required=False)

    def clean_price_to(self) -> int:
        price_to = self.cleaned_data['price_to']
        if price_to is None:
            return 500000
        return price_to

    def clean_price_from(self) -> int:
        price_from = self.cleaned_data['price_from']
        if price_from is None:
            return 0
        return price_from            