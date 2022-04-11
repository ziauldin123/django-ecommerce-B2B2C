from dataclasses import field
from pyexpat import model
from django.forms import ModelForm
from .models import Item
from django import forms

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = (
            'title',
            'description',
            'price',
            'category',
            'quantity',
            'available',
            'image',
            'unit',
        )

class SearchForm(forms.Form):
    def __init__(self,*args,**kwargs):
        items = kwargs.pop('items') if kwargs.get('items') is not None else Item.objects.all()
        super().__init__(*args,**kwargs)

    query = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class':'input'}),required=False)
    price_from = forms.BooleanField(initial=0,required=False,widget=forms.TextInput(attrs={'class':'input'}))
    price_to = forms.IntegerField(initial=5000000, required=False,widget=forms.TextInput(attrs={'class':'input'}))
    location = forms.CharField(widget=forms.Select(),required=False)

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