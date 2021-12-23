from io import BytesIO
from os import name
from PIL import Image
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.expressions import Col
from django.db.models.fields import CharField
from autoslug import AutoSlugField
from django.utils.safestring import mark_safe

from django.core.files import File
from django.db import models
from django.db.models import CASCADE

from apps.vendor.models import Vendor
from django.core.validators import MinValueValidator, MaxValueValidator



class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/' % (self.slug)


class SubCategory(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category, related_name='subcategory', on_delete=models.CASCADE)

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'SubCategories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/%s/' % (self.category, self.slug)


class SubSubCategory(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    sub_category = models.ForeignKey(
        SubCategory, related_name='subsubcategory', on_delete=models.CASCADE)

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'SubSubCategories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/%s/%s/' % (self.sub_category.category, self.sub_category, self.slug)

class Color(models.Model):
    name=models.CharField(max_length=28)
    code=models.CharField(max_length=10,blank=True,null=True)

    def __str__(self) :
        return self.name

    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color </p>'.format(self.code))
        else:
            return ""



class Product(models.Model):
    VARIANTS=(
        ('None','None'),
        ('size','size'),
        ('color','color'),
        ('color-Size','color-Size')
          )
    category = models.ForeignKey(
        SubSubCategory, related_name='products', on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', related_name='variants', on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(
        Vendor, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    slugV=AutoSlugField(populate_from='vendor')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=0)
    date_added = models.DateTimeField(auto_now_add=True)
    # image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    # thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    num_available = models.IntegerField(default=1)
    num_visits = models.IntegerField(default=0)
    last_visit = models.DateTimeField(blank=True, null=True)
    pickup_available = models.BooleanField(default=False)
    visible = models.BooleanField(default=False)
    discount = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(99)])
    is_free_delivery = models.BooleanField(default=False)

    rating = models.FloatField(default=0.0)

    weight = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    material = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)

    # property

    payment=models.CharField(max_length=100,null=True, blank=True)
    delivery_Time=models.DecimalField(max_digits=6, decimal_places=0,null=True, blank=True)
    returns=models.DecimalField(max_digits=6, decimal_places=0,null=True, blank=True)
    dimensions=models.CharField(max_length=200,null=True, blank=True)
    available=models.DecimalField(max_digits=6, decimal_places=0,null=True, blank=True)
    variant=models.CharField(max_length=10,choices=VARIANTS,default='None')
    # name=models.ForeignKey(Color,on_delete=models.CASCADE)


    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.title

    def get_thumbnail(self):
        try:
            product_image = ProductImage.objects.filter(
                product=self.id).first()
            if product_image.thumbnail:
                return product_image.thumbnail.url

            else:
                if product_image.image:
                    product_image.thumbnail = self.make_thumbnail(self.image)
                    product_image.save()

                    return product_image.thumbnail.url
                else:
                    return 'https://via.placeholder.com/240x180.jpg'
        except:
            return 'https://via.placeholder.com/240x180.jpg'

    def get_absolute_url(self):
        return '/%s/%s' % (self.category.slug, self.slug)

    def get_url(self):
        return f'/{self.category.sub_category.category.slug}/{self.category.sub_category.slug}/{self.category.slug}/{self.slug}/'

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=100)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail

    def get_discounted_price(self):
        return self.price * (100 - self.discount) / 100


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE)

    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)

        super().save(*args, **kwargs)



    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=100)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


# class Review(models.Model):
#     product = models.ForeignKey(Product, on_delete=CASCADE)
#     user = models.ForeignKey(User, on_delete=CASCADE)
#     text = models.CharField(max_length=255)
#     rating = models.PositiveIntegerField(default=1)


# class ProductCollection(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     collection = models.ForeignKey(
#         'product.Collection', on_delete=models.CASCADE)


# class Collection(models.Model):
#     products = models.ManyToManyField(
#         to=Product,
#         through=ProductCollection,
#         related_name='product_collection'
#     )
#     title = models.CharField(max_length=255)

#     def __str__(self):
#         return self.title



class Size(models.Model):
    name=models.CharField(max_length=20)
    code=models.CharField(max_length=10,blank=True,null=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    title=models.CharField(max_length=100,blank=True,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    color=models.ForeignKey(Color,on_delete=CASCADE,blank=True,null=True)
    size=models.ForeignKey(Size,on_delete=CASCADE,blank=True,null=True)
    imageId=models.IntegerField(blank=True,null=True,default=0)
    quantity=models.IntegerField(default=1)
    price=models.FloatField(default=0)

    def __str__(self):
        return self.title

    def image(self):
        img=ProductImage.objects.get(id=self.imageId)
        if img.id is not None:
            varimage=img.image.url
        else:
            varimage=""
        return varimage

    def image_tag(self):
        img=ProductImage.objects.get(id=self.imageId)
        if img.id is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(img.image.url))
        else:
            return ""


