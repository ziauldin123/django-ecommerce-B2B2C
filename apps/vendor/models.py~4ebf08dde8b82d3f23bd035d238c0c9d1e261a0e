from decimal import Decimal
from random import choices
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.cart.models import District, Sector, Cell, Village
from autoslug import AutoSlugField
import apps.ordering


class Vendor(models.Model):
    STATUS = (
        ('DIAMOND','DIAMOND'),
        ('SAPPHIRE','SAPPHIRE'),
        ('EMERALD','EMERALD'),
        ('RUBY','RUBY')
    )
    email = models.EmailField(max_length=150)
    company_name = models.CharField(max_length=255)
    company_code = models.CharField(max_length=255)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, null=True)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=10)
    slug = AutoSlugField(populate_from='company_name', unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=False)
    products_limit = models.IntegerField(default=1)
    user = models.OneToOneField(
        User, related_name='vendor', on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='uploads/', blank=True, null=True)
    company_registration = models.ImageField(
        upload_to='upload/registration/company-%Y-%m-%d/', blank=True, null=True)
    privacy_checked = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS, default='DIAMOND')

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return '/%s/' % (self)

    @property
    def getOrder(self):
        order = apps.ordering.models.Order.objects.filter(vendors=self)
        return order

    def get_variant(self):
        product = self.newProducts.all()
        return apps.newProduct.models.Variants.objects.filter(product=product).all()

    def get_avatar(self):
        if not self.logo:
            return "https://via.placeholder.com/240x180.jpg"

    def get_balance(self):
        items = self.items.filter(
            vendor_paid=False, order__vendors__in=[self.id])
        return sum((item.price * item.quantity) for item in items)

    def get_total_amount(self, total):
        items = self.items.filter(
            vendor=self
        )
        total = sum((item.get_total_price) for item in items)
        return total

    def get_paid_amount(self):
        items = self.items.filter(
            vendor_paid=True, order__vendors__in=[self.id])
        return sum((item.price * item.quantity) for item in items)

    @receiver(post_save, sender=User)
    def create_user_vendor(sender, instance, created, **kwargs):
        # if not instance.vendor:
        #     Vendor.objects.create(user=instance)

        try:
            instance.vendor.save()
            if instance.is_staff == True:
                Vendor.objects.last().delete()

        except Exception as e:
            pass


class VendorDelivery(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=8)
    vendor = models.ForeignKey(
        Vendor, related_name='vendor_delivery', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Vendor Deliveries'


class OpeningHours(models.Model):
    WEEKDAYS = [
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    ]
    vendor = models.ForeignKey(
        Vendor, related_name='Opening', on_delete=models.CASCADE)
    weekday = models.IntegerField(choices=WEEKDAYS)
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    class Meta:
        ordering = ('weekday', 'from_hour')

    def __str__(self):
        return '%s' % (self.get_weekday_display())


class Customer(models.Model):
    email = models.EmailField(max_length=150)
    customername = models.CharField(max_length=32)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    company_code = models.CharField(max_length=255, null=True, blank=True)
    privacy_checked = models.BooleanField(default=False)
    user = models.OneToOneField(
        User, related_name='customer', on_delete=models.CASCADE)

    def __str__(self):
        return self.customername

    @receiver(post_save, sender=User)
    def create_user_customer(sender, instance, created, **kwargs):
        # if created:
        #     Customer.objects.create(user=instance)

        try:
            instance.customer.save()
            if instance.is_staff == True:
                Customer.objects.last().delete()

        except Exception as e:
            pass


class Transporter(models.Model):
    email = models.EmailField(max_length=150)
    transporter_name = models.CharField(max_length=32)
    number_plate = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        User, related_name='transporter', on_delete=models.CASCADE)

    def __str__(self):
        return self.transporter_name

    @receiver(post_save, sender=User)
    def create_user_transporter(sender, instance, created, **kwargs):
        # if created:
        #     Transporter.objects.create(user=instance)

        try:
            instance.transporter.save()
            if instance.is_staff == True:
                Transporter.objects.last().delete()

        except Exception as e:
            pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=150)
    signup_confirmation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def update_profile_signal(sender, instance, created, **kwargs):
        # if created:
        #     Profile.objects.create(user=instance)
        # instance.profile.save()
        print("profile", kwargs)
        try:
            instance.Profile.save()
            if instance.is_staff == True:
                Profile.objects.last().delete()

        except Exception as e:
            pass


class UserWishList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        'newProduct.Product', on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey(
        'newProduct.Variants', on_delete=models.CASCADE, null=True, blank=True
    )
    is_variant = models.BooleanField()
    text = models.CharField(max_length=255, null=True)
