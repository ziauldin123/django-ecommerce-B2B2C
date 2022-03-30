from dataclasses import field
from pyexpat import model
from django.forms import ModelForm
from .models import Item

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = (
            'title',
            'description',
            'price',
            'discount',
            'category',
            'quantity',
            'available',
            'image',
            'unit',
        )