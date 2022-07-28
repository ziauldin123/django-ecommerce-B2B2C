from ast import Bytes, arg
from distutils.command.upload import upload
import email
from email.mime import image
from operator import mod
from pyexpat import model
from statistics import mode
from tkinter import CASCADE
from django.utils.safestring import mark_safe
from PIL import Image
from turtle import title
from unicodedata import category
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

from apps.vendor.models import Customer, Vendor
from apps.cart.models import District
from django.core.files.base import ContentFile
from io import BytesIO

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=False,unique=True)
    description = models.TextField(max_length=255)
    image = models.ImageField(upload_to='images/',null=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        
        if self.image and not self.image.url.endswith('.webp'):
            imm = Image.open(self.image).convert("RGB")
            original_width, original_height = imm.size
            aspect_ration = round(original_width / original_height)
            if aspect_ration < 1:
                aspect_ration = 1
            desired_height = 500
            desired_width = desired_height * aspect_ration
            imm.thumbnail((desired_width,desired_height), Image.ANTIALIAS)
            new_image_io = BytesIO()
            imm.save(new_image_io,format="WEBP",quality=70)
            self.image.save(
                self.title[:40]+".webp",
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )
        super(Category,self).save(*args, **kwargs)    

    def __str__(self):
        return self.title

    def get_thumbnail(self):
        try:
            category_image = self.image
            if category_image.thumbnail:
                return category_image.thumbnail.url
            else:
                if category_image.image:
                    category_image.thumbnail = self.make_thumbnail(self.image)
                    category_image.save()

                    return category_image.thumbnail.url
                else:
                    return 'https://via.placeholder.com/240x180.jpg'
        except:
            return 'https://via.placeholder.com/240x180.jpg'                           

class Type(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category,related_name = 'category',on_delete=models.CASCADE,null=True,blank=True)
    slug = models.SlugField(null=False,unique=True)

    def save(self,*args,**kwargs):
        self.slug = slugify(self.title)
        super(Type,self).save(*args,**kwargs)

    def __str__(self):
        return self.title    


class UnitTypes(models.Model):
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=150)

    def __str__(self):
        return "{}".format(self.unit)     

    class Meta:
        verbose_name_plural = 'Unit_Types'

class Make(models.Model):
    make = models.CharField(max_length=255)

    def __str__(self):
        return str(self.make)

class Item_Model(models.Model):
    model=models.CharField(max_length=255)

    def __str__(self):
        return self.model

class Room(models.Model):
    room=models.IntegerField(default=0)

    def __str__(self):
        return str(self.room)

class Application(models.Model):
    application=models.CharField(max_length=255)

    def __str__(self):
        return self.application

class Capacity(models.Model):
    capacity=models.IntegerField(default=0)

    def __str__(self):
        return str(self.capacity)

class Year(models.Model):
    year=models.IntegerField(default=0)

    def __str__(self):
        return str(self.year)

class Engine(models.Model):
    engine=models.CharField(max_length=255)

    def __str__(self):
        return self.engine

class Amenity(models.Model):
    amenity=models.CharField(max_length=255)

    def __str__(self):
        return self.amenity

class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    category = models.ForeignKey(
        Category, related_name='items',on_delete=models.CASCADE
    )
    item_type = models.ForeignKey(Type,on_delete=models.CASCADE,related_name='item_type',null=True,blank=True) 
    phone = models.CharField(max_length=255,null=True)
    user = models.ForeignKey(
        User, related_name='rental_items',on_delete=models.CASCADE
    )
    email = models.EmailField(max_length=255,null=True)
    slug = models.SlugField(null=True, unique=True)
    quantity = models.DecimalField(max_digits=12,default=0,decimal_places=2)
    available=models.BooleanField(default=False)
    visible=models.BooleanField(default=False)
    district=models.ForeignKey(District,on_delete=models.CASCADE,null=True)
    makes=models.ForeignKey(Make,on_delete=models.CASCADE,related_name='makes',null=True,blank=True)
    rooms=models.ForeignKey(Room,on_delete=models.CASCADE,related_name='rooms',null=True,blank=True)
    application = models.ForeignKey(Application,on_delete=models.CASCADE,related_name='application_item',null=True,blank=True)
    capacity=models.ForeignKey(Capacity,on_delete=models.CASCADE,related_name='capacity_item',null=True,blank=True)
    sale=models.BooleanField(default=False)
    year=models.ForeignKey(Year,on_delete=models.CASCADE,related_name='year_item',null=True,blank=True)
    engine=models.ForeignKey(Engine,on_delete=models.CASCADE,related_name='engine_item',null=True,blank=True)
    amenity=models.ForeignKey(Amenity,on_delete=models.CASCADE,related_name='amenity_item',null=True,blank=True)
    model=models.ForeignKey(Item_Model,on_delete=models.CASCADE,related_name='vehicle_model',null=True,blank=True)
    image=models.ImageField(upload_to='images/',null=False)
    unit=models.ForeignKey(UnitTypes,related_name='unit_item',on_delete=models.CASCADE)
    review=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if self.image and not self.image.url.endswith('.webp'):
            imm=Image.open(self.image).convert("RGB")
            original_width, original_height = imm.size
            aspect_ration=round(original_width / original_height)
            if aspect_ration < 1:
                aspect_ration =1
            desired_height = 500
            desired_width = desired_height * aspect_ration
            imm.thumbnail((desired_width,desired_height), Image.ANTIALIAS)
            new_image_io = BytesIO()
            imm.save(new_image_io,format="WEBP",quality=70)
            self.image.save(
                self.title[:40]+".webp",
                content=ContentFile(new_image_io.getvalue()),
                save=False
            ) 
        super(Item,self).save(*args,**kwargs)

    def __str__(self):
        return self.title 

    def get_thumbnail(self):
        try:
            item_image = self.image
            if item_image.thumbnail:
                return item_image.thumbnail.url
            else:
                if item_image.image:
                    item_image.thumbnail=self.make_thumbnail(self.image)
                    item_image.save()

                    return item_image.thumbnail.url
                else:
                    return   'https://via.placeholder.com/240x180.jpg'
        except:
            return 'https://via.placeholder.com/240x180.jpg'                                
      
    def get_absolute_url(self):
        return '/%s/%s' % (self.category.slug, self.slug)
    
class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name='items_images',on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=50,blank=True)
    image = models.ImageField(blank=True,upload_to='images/')

    def save(self,*args,**kwargs):
        if self.image and not self.image.url.endswith('.webp'):
            imm = Image.open(self.image).convert("RGB")
            original_width,original_height = imm.size
            aspect_ration = round(original_width / original_height)
            if aspect_ration < 1:
                aspect_ration = 1
            desired_height = 500
            desired_width = desired_height * aspect_ration
            imm.thumbnail((desired_width, desired_height), Image.ANTIALIAS)
            new_image_io = BytesIO()
            imm.save(new_image_io, format="WEBP", quality=70)
            self.image.save(
                self.title[:40]+".webp", 
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )  
        super(ItemImage,self).save(*args,**kwargs) 
    
    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))         
    
