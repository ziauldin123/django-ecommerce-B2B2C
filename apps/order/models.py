# from django.db import models

# from apps.product.models import Product
# from apps.vendor.models import Vendor


# class Order(models.Model):
#     ORDERED = 'ordered'
#     SHIPPED = 'shipped'
#     ARRIVED = 'arrived'

#     STATUS_CHOICES = (
#         (ORDERED, 'Ordered'),
#         (SHIPPED, 'Shipped'),
#         (ARRIVED, 'Arrived')
#     )

#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.CharField(max_length=100)
#     address = models.CharField(max_length=100)
#     phone = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)

#     district = models.CharField(max_length=100, null=True)
#     sector = models.CharField(max_length=100, null=True)
#     village = models.CharField(max_length=100, null=True)
#     cell = models.CharField(max_length=100, null=True)
#     delivery_address = models.CharField(max_length=170, null=True)

#     delivery_cost = models.IntegerField(default=0)

#     paid_amount = models.DecimalField(max_digits=8, decimal_places=0)
#     is_paid = models.BooleanField(default=False)
#     vendors = models.ManyToManyField(Vendor, related_name='orders')

#     shipped_date = models.DateTimeField(blank=True, null=True)
#     arrived_date = models.DateTimeField(blank=True, null=True)
#     status = models.CharField(
#         max_length=20, choices=STATUS_CHOICES, default=ORDERED)
#     used_coupon = models.CharField(max_length=50, blank=True, null=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return self.first_name


# class OrderItem(models.Model):
#     order = models.ForeignKey(
#         Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(
#         Product, related_name='items', on_delete=models.CASCADE)
#     vendor = models.ForeignKey(
#         Vendor, related_name='items', on_delete=models.CASCADE)
#     vendor_paid = models.BooleanField(default=False)
#     price = models.DecimalField(max_digits=8, decimal_places=0)
#     quantity = models.IntegerField(default=1)

#     def __str__(self):
#         return '%s' % self.id

#     def get_total_price(self):
#         return self.price * self.quantity
