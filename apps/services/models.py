from django.db import models
from django.dispatch import receiver
from django.forms import ModelForm
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import Max
from django.db.models import Avg, Count
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=255,null=False)
    slug = models.SlugField(null=False,unique=True)
    image = models.ImageField(upload_to='images/',null=False)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.title)
        if self.image and not self.image.url.endswith('.webp'):
            imm = Image.open(self.image).convert("RGB")
            original_width, original_height = imm.size
            aspect_ration = round(original_width / original_height)
            if aspect_ration <1 :
                aspect_ration = 1
            desired_height = 500
            desired_width = desired_height * aspect_ration
            imm.thumbnail((desired_width,desired_height),Image.ANTIALIAS)
            new_image_io = BytesIO()
            imm.save(new_image_io,format="WEBP",quality=70)
            self.image.save(
                self.title[:40]+".webp",
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )    
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
    rating = models.IntegerField(default=0)
    tin = models.CharField(max_length=255,default=0)
    privacy_checked = models.BooleanField(default=False)
    price=models.IntegerField(default=0)
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
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        review = Comment.objects.filter(
            service_provider=self, status='True').aggregate(avarage=Avg('rate'))
        
        if review["avarage"] is not None:
            self.rating=round(float(review["avarage"]))


    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        
        if self.image and not self.image.url.endswith('.webp'):
            imm=Image.open(self.image).convert("RGB")
            original_width, original_height = imm.size
            aspect_ratio=round(original_width / original_height)
            if aspect_ratio < 1:
                aspect_ratio = 1
            desired_height = 500
            desired_width = desired_height * aspect_ratio
            imm.thumbnail((desired_width,desired_height), Image.ANTIALIAS)
            new_image_io = BytesIO()
            imm.save(new_image_io,format="WEBP",quality=70)
            self.image.save(
                self.name[:40]+".webp",
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )     
        super(ServiceProvider,self).save(*args,**kwargs)

    def __str__(self):
        return self.name    
    
    def get_thumbnail(self):
        try:
            item_image = self.image
            if item_image.thumbnail:
                return item_image.thumbnail.url
            else:
                if item_image.image:
                    item_image.thumbnail = self.make_thumbnail(self.image)
                    item_image.save()

                    return item_image.thumbnail.url
                else:
                    return   'https://via.placeholder.com/240x180.jpg'
        except:
            return 'https://via.placeholder.com/240x180.jpg'                  

    def avarageview(self):
        reviews = Comment.objects.filter(
            service_provider=self, status='True').aggregate(avarage=Avg('rate'))
        avg = 0
        if reviews["avarage"] is not None:
            avg=round(float(reviews["avarage"]))
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

    def get_absolute_url(self):
        return '/%s/%s' % (self.service.slug, self.slug)

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