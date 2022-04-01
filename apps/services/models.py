from datetime import datetime
from distutils.command.upload import upload
from email.mime import image
from operator import mod
from telnetlib import STATUS
from turtle import title
from unicodedata import category
import django
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=255,null=False)
    slug = models.SlugField(null=False,unique=True)
    image = models.ImageField(upload_to='images/',null=False)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.title)
        super(Category,self).save(*args,**kwargs)

    def __str__(self):
        return self.title   

class ServiceProvider(models.Model):
    

    ACCOUNT_CHOICES = (
        ('COMPANY','company'),
        ('INDIVIDUAL','individual')
    )

    service = models.ForeignKey(Category,on_delete=models.CASCADE)
    slug = models.SlugField(null=False,unique=True)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=150)
    image = models.ImageField(upload_to='images/',null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255,null=True)
    available = models.BooleanField(default=True)
    review = models.BooleanField(default=False)
    tin = models.CharField(max_length=255,default=0)
    privacy_checked = models.BooleanField(default=False)
    account = models.CharField(max_length=20,choices=ACCOUNT_CHOICES,default='individual')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        User, related_name='service_provider',on_delete=models.CASCADE
    )

    @receiver(post_save,sender=User)
    def create_service_provider(sender, instance, created, **kwargs):
        try:
            instance.service_provider.save()
            if instance.is_staff == True:
                ServiceProvider.objects.last().delte()
        except Exception as e:
            pass         

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super(ServiceProvider,self).save(*args,**kwargs)

    def __str__(self):
        return self.name    