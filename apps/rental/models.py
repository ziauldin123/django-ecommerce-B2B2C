from ast import arg
from distutils.command.upload import upload
from email.mime import image
from operator import mod
from tkinter import CASCADE
from turtle import title
from unicodedata import category
from django.db import models
from django.utils.text import slugify
from autoslug import AutoSlugField
from apps.newProduct.models import UnitTypes
from apps.vendor.models import Vendor

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=False,unique=True)
    description = models.TextField(max_length=255)
    image = models.ImageField(upload_to='images/',null=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category,self).save(*args, **kwargs)

    def __str__(self):
        return self.title    

class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    price = models.IntegerField(max_length=12,default=0)
    category = models.ForeignKey(
        Category, related_name='items',on_delete=models.CASCADE
    ) 
    contact = models.TextField(max_length=255)
    slug = models.SlugField(null=False, unique=True)
    slugV = AutoSlugField(populate_from='vendor', null=True)
    quantity = models.DecimalField(max_digits=12,default=0,decimal_places=2)
    unit=models.ForeignKey(UnitTypes,related_name='item_unit',on_delete=models.CASCADE)
    available=models.BooleanField(default=False)
    image=models.ImageField(upload_to='images/',null=False)
    vendor=models.ForeignKey(Vendor,related_name='vendor',on_delete=models.CASCADE)
    
