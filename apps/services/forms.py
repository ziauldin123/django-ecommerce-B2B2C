from dataclasses import fields
from email.mime import image
from pyexpat import model
import re
from unicodedata import name

from apps import services
from .models import ServiceProvider,Category
from django import forms
from django.contrib.auth.forms import UserCreationForm,User

class ServiceProviderForm(UserCreationForm):
    service = forms.ChoiceField(choices=[
                                 (-1, '')] + [(entry.id, entry.title) for entry in Category.objects.all()])
    phone = forms.CharField(max_length=35,required=True)
    tin = forms.CharField(max_length=25,required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}),required=False)
    image = forms.ImageField(required=False)
    name = forms.CharField(max_length=25,required=True)
    account = forms.ChoiceField(choices=ServiceProvider.ACCOUNT_CHOICES)
    class Meta:
        model = User
        fields = [
           'username',
           'password1',
           'password2',
           'email',
           'service',
           'phone',
           'name',
           'account',
           'tin',
           'description'
        ]

class SearchForm(forms.Form):
    def __init__(self,*args,**kwargs):
        providers = kwargs.pop('providers') if kwargs.get('providers') is not None else ServiceProvider.objects.all()
        super().__init__(*args,**kwargs)

    query = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class':'input'}),required=False)
    experience = forms.CharField(widget=forms.Select(),required=False)    