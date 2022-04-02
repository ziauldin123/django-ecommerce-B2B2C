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
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    image = forms.ImageField(required=False)
    name = forms.CharField(max_length=25,required=True)
    account = forms.ChoiceField(choices=[
        (-1, '')] + [(entry.id, entry.account) for entry in ServiceProvider.objects.all()])
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
