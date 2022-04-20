from dataclasses import fields
from pyexpat import model
from django.db import models
from django.dispatch import receiver
from django.forms import ModelForm
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import Max
from django.urls import reverse
from django.db.models import Avg, Count

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

class Experience(models.Model):
    experince = models.IntegerField(default=0)

    def __str__(self):
        return str(self.experince)

class ServiceProvider(models.Model):
    
    ACCOUNT_CHOICES = (
        ('COMPANY','company'),
        ('INDIVIDUAL','individual')
    )

    service = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='service_category')
    slug = models.SlugField(null=False,unique=True)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=150)
    image = models.ImageField(upload_to='images/',null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255,null=True)
    experience = models.ForeignKey(Experience,on_delete=models.CASCADE,null=True,blank=True)
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
    
    def avarageview(self):
        reviews = Comment.objects.filter(
            service_provider=self, status='True').aggregate(avarage=Avg('rate'))
        avg = 0
        if reviews["avarage"] is not None:
            avg = float(reviews["avarage"])
        return avg 

    def countreview(self):
        reviews = Comment.objects.filter(
           service_provider = self, status='True').aggregate(count=Count('id')) 
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt 

    def maxrating(self):
        rate = Comment.objects.filter(
            service_provider=self, status='True'
        ).aggregate(Max('rate'))     
        return rate  

               

class Comment(models.Model):
    STATUS = (
        ('New','New'),
        ('True','True'),
        ('False','False')
    )
    service_provider = models.ForeignKey(
        ServiceProvider,related_name='service_provider',on_delete=models.CASCADE
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50,blank=True)
    comment = models.CharField(max_length=250,blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20,blank=True)
    status = models.CharField(max_length=10,choices=STATUS,default='True')
    create_at = models.DateField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields =  ['subject','comment','rate']