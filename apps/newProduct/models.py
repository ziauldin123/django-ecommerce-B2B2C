import os
from itertools import product
from turtle import title
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.expressions import OrderBy
from django.contrib.auth.models import User
from django.db.models.fields import SlugField
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.utils.safestring import mark_safe
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.db.models import Max
from django.urls import reverse
from django.utils.text import slugify
from autoslug import AutoSlugField
from django.forms import ModelForm

from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image

from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
from apps.vendor.models import Vendor
from django.db.models import Avg, Count



class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=False, unique=True)
    ordering = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'Categories'

    def get_absolute_url(self):
        return '/%s/' % (self.slug)


class SubCategory(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=False, unique=True)
    ordering = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, related_name='subcategory', on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(SubCategory, self).save(*args, **kwargs)

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'SubCategories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/%s/' % (self.category, self.slug)


class SubSubCategory(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True,
                            related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    slug = models.SlugField(null=False, unique=True)
    sub_category = models.ForeignKey(
        SubCategory, related_name='subsubcategory', on_delete=CASCADE, null=True
    )
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Sub_subcategories'

    class MPTTMeta:
        order_insertion_by = ['title']

    def get_absolute_url(self):
        return reverse('susubcategory_detail', kwargs={'slug': self.slug})

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.apparent
        return ' / '.join(full_path[::-1])


class Size(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


class Weight(models.Model):
    weight = models.IntegerField(default=0)

    def __str__(self):
        return str(self.weight)


class Width(models.Model):
    width = models.IntegerField(default=0)

    def __str__(self):
        return str(self.width)


class Length(models.Model):
    length = models.IntegerField(default=0)

    def __str__(self):
        return str(self.length)


class Height(models.Model):
    height = models.IntegerField(default=0)

    def __str__(self):
        return str(self.height)


class Color(models.Model):
    name = models.CharField(max_length=28)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color </p>'.format(self.code))
        else:
            return ""


class UnitTypes(models.Model):
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=150)

    def __str__(self):
        return "{}".format(self.unit)     

    class Meta:
        verbose_name_plural = 'Unit_Types'
    
    

class Brand(models.Model):
    brand = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return str(self.brand)

    class Meta:
        ordering=('-brand',)

    def save(self,*args,**kwargs):
        self.brand=self.brand.lower()
        return super(Brand, self).save(*args,**kwargs)    

class Product(models.Model):

    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
        ('Color', 'Color'),
        ('Weight', 'Weight'),
        ('Height', 'Height'),
        ('Length', 'Length'),
        ('Width', 'Width'),
        ('Size-Color', 'Size-Color'),
        ('Wght-Color', 'Weight-Color')
    )
    # many to one relation with Category
    category = models.ForeignKey(
        SubSubCategory, related_name='product', on_delete=models.CASCADE)
    vendor = models.ForeignKey(
        Vendor, related_name='newProducts', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=150)
    brand = models.ForeignKey(
        Brand, on_delete=models.DO_NOTHING, null=True, blank=True)
    summary = models.TextField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    unit_type = models.ForeignKey(
        UnitTypes, on_delete=models.DO_NOTHING, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)
    variant = models.CharField(max_length=10, choices=VARIANTS, default='None')
    description = RichTextUploadingField()
    size = models.ForeignKey(
        Size, on_delete=models.CASCADE, blank=True, null=True)
    weight = models.ForeignKey(
        Weight, on_delete=models.CASCADE, blank=True, null=True)
    width = models.ForeignKey(
        Width, on_delete=models.CASCADE, blank=True, null=True)
    length = models.ForeignKey(
        Length, on_delete=models.CASCADE, blank=True, null=True)
    height = models.ForeignKey(
        Height, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(null=False, unique=True)
    slugV = AutoSlugField(populate_from='vendor', null=True)
    num_visits = models.IntegerField(default=0)
    last_visit = models.DateTimeField(blank=True, null=True)
    pickup_available = models.BooleanField(default=False)
    visible = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    discount = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name="Discount %")
    is_free_delivery = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_vat = models.BooleanField(default=True)
    is_variant = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.image and not self.image.url.endswith('.webp'):
            imm = Image.open(self.image).convert("RGB")
            original_width, original_height = imm.size
            aspect_ratio = round(original_width / original_height)
            if aspect_ratio < 1:
                aspect_ratio = 1
            desired_height = 500  # Edit to add your desired height in pixels
            desired_width = desired_height * aspect_ratio
            imm.thumbnail((desired_width, desired_height), Image.ANTIALIAS)
            new_image_io = BytesIO()
            imm.save(new_image_io, format="WEBP", quality=70)
            self.image.save(
                self.title[:40]+".webp",
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )
        super(Product, self).save(*args, **kwargs)

    @property
    def get_variant(self):
        if Variants.objects.filter(product=self, status=True, visible=True).exists():
            return Variants.objects.filter(product=self, status=True, visible=True).first()
        else:
            return []

    def __str__(self):
        return self.title

    def get_url(self):
        return f'/{self.id}/{self.vendor.slug}/{self.category.sub_category.category.slug}/{self.category.sub_category.slug}/{self.category.slug}/{self.slug}/'

    def get_product_image(self):
        return self.product_image

    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""

    def get_absolute_url(self):
        # return reverse('category_detail', kwargs={'slug': self.slug})
        return '/%s/%s' % (self.category.slug, self.slug)

    def avaregeview(self):
        reviews = Comment.objects.filter(
            product=self, status='True').aggregate(avarage=Avg('rate'))
        avg = 0
        if reviews["avarage"] is not None:
            avg = float(reviews["avarage"])
        return avg

    def countreview(self):
        reviews = Comment.objects.filter(
            product=self, status='True').aggregate(count=Count('id'))
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt
    
    def  maxrating(self):
        rate = Comment.objects.filter(
            product=self, status='True').aggregate(Max('rate'))

        return rate    


    def get_thumbnail(self):
        try:
            product_image = self.image
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

    def get_vat_price(self):
        if self.is_vat == True:
            if self.discount > 0:
                discounted_price = float(
                    self.price-((self.discount*self.price)/100)

                )
                return float(18*discounted_price/100)
            else:
                return float((18*self.price)/100)
        else:
            return 0

    def get_discounted_price(self):
        discounted_price = float(self.price-((self.discount*self.price)/100))
        return discounted_price

    def get_vat_exclusive_price(self):
        if self.is_vat == True:
            discounted_price = float(
                self.price-((self.discount*self.price)/100))
            return float(discounted_price-((18*discounted_price)/100))
        else:
            return float(self.price-((self.discount*self.price)/100))


class Comment(models.Model):
    STATUS = (
        ('New', 'New'),
        ('True', 'True'),
        ('False', 'False'),
    )
    product = models.ForeignKey(
        Product, related_name='product', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='True')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['subject', 'comment', 'rate']


class Images(models.Model):
    product = models.ForeignKey('newProduct.product', on_delete=models.CASCADE,
                                null=True, blank=True, related_name='product_image')
    
    name = models.CharField(max_length=50, blank=True)
    image = models.ImageField(blank=True, upload_to='images/')

    def save(self, *args, **kwargs):
        if self.image and not self.image.url.endswith('.webp'):
            imm = Image.open(self.image).convert("RGB")
            original_width, original_height = imm.size
            aspect_ratio = round(original_width / original_height)
            if aspect_ratio < 1:
                aspect_ratio = 1
            desired_height = 500  # Edit to add your desired height in pixels
            desired_width = desired_height * aspect_ratio
            imm.thumbnail((desired_width, desired_height), Image.ANTIALIAS)
            new_image_io = BytesIO()
            imm.save(new_image_io, format="WEBP", quality=70)
            self.image.save(
                self.name[:40]+".webp",
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )
        super(Images, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Gallery"
        verbose_name = "Images"

    def imagename(self):
        return os.path.basename(self.image.name)

    def img(self):
        if self.image:
            return mark_safe('<img src="%s" width="80px" height="80px"/>' % (self.image.url))
    img.short_description = 'Images'


class Variants(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_variant')
    vendor = models.ForeignKey(
        Vendor, related_name='variants_vendor', on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, blank=True, null=True)
    size = models.ForeignKey(
        Size, on_delete=models.CASCADE, blank=True, null=True)
    weight = models.ForeignKey(
        Weight, on_delete=models.CASCADE, blank=True, null=True)
    width = models.ForeignKey(
        Width, on_delete=models.CASCADE, blank=True, null=True)
    length = models.ForeignKey(
        Length, on_delete=models.CASCADE, blank=True, null=True)
    height = models.ForeignKey(
        Height, on_delete=models.CASCADE, blank=True, null=True)
    image_id = models.IntegerField(blank=True, null=True, default=0)
    image_variant = models.ImageField(upload_to='images/', null=False)
    quantity = models.IntegerField(default=1)
    is_vat = models.BooleanField(default=True)
    unit_type = models.ForeignKey(
        UnitTypes, on_delete=models.DO_NOTHING, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.BooleanField(default=False)
    visible = models.BooleanField(default=False)
    discount = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name="Discount %")

    def save(self, *args, **kwargs):
        if self.image_variant and not self.image_variant.url.endswith('.webp'):
            imm = Image.open(self.image_variant).convert("RGB")
            original_width, original_height = imm.size
            aspect_ratio = round(original_width / original_height)
            if aspect_ratio < 1:
                aspect_ratio = 1
            desired_height = 500  # Edit to add your desired height in pixels
            desired_width = desired_height * aspect_ratio
            imm.thumbnail((desired_width, desired_height), Image.ANTIALIAS)
            new_image_io = BytesIO()
            imm.save(new_image_io, format="WEBP", quality=70)
            self.image_variant.save(
                self.title[:40]+".webp",
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )
        super(Variants, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Variants'

    def get_url(self):
        return f'/{self.product.id}/{self.product.vendor.slug}/{self.product.category.sub_category.category.slug}/{self.product.category.sub_category.slug}/{self.product.category.slug}/{self.product.slug}/'

   
    def image(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            varimage = img.image.url
        else:
            varimage = ""
        return varimage

    def get_vat_price(self):
        if self.is_vat == True:
            if self.discount > 0:
                discounted_price = float(
                    self.price-((self.discount*self.price)/100)
                )
                return float(18*discounted_price/100)
            else:
                return float((18*self.price)/100)
        else:
            return 0

    def get_vat_exclusive_price(self):
        if self.is_vat == True:
            discounted_price = float(
                self.price-((self.discount*self.price)/100))
            return float(discounted_price-((18*discounted_price)/100))
        else:
            return float(self.price-((self.discount*self.price)/100))

    def image_tag(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(img.image.url))
        else:
            return ""

    def get_discounted_price_var(self):
        discounted_price = float(self.price-((self.discount*self.price)/100))
        return discounted_price

    def get_vat_exclusive_price(self):
        if self.is_vat == True:
            discounted_price = float(
                self.price-((self.discount*self.price)/100))
            return float(discounted_price-((18*discounted_price)/100))
        else:
            return float(self.price-((self.discount*self.price)/100))

    def get_discounted_price(self):
        discounted_price = float(self.price-((self.discount*self.price)/100))
        return discounted_price


class ProductCollection(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    collection = models.ForeignKey(
        'newProduct.Collection', on_delete=models.CASCADE)


class Collection(models.Model):
    products = models.ManyToManyField(
        to=Product,
        through=ProductCollection,
        related_name='product_collection'
    )
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='product_images', on_delete=models.CASCADE, blank=True, null=True)
    variant = models.ForeignKey(
        Variants, related_name='variants_images', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True)
    image = models.ImageField(blank=True, upload_to='images/')
    

    def save(self, *args, **kwargs):
        if self.image and not self.image.url.endswith('.webp'):
            imm = Image.open(self.image).convert("RGB")
            original_width, original_height = imm.size
            aspect_ratio = round(original_width / original_height)
            if aspect_ratio < 1:
                aspect_ratio = 1
            desired_height = 500  # Edit to add your desired height in pixels
            desired_width = desired_height * aspect_ratio
            imm.thumbnail((desired_width, desired_height), Image.ANTIALIAS)
            new_image_io = BytesIO()
            imm.save(new_image_io, format="WEBP", quality=70)
            self.image.save(
                self.title[:40]+".webp",
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )
        super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def image_tag(self):

        return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
