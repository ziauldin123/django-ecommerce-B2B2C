import email
import re
from django import apps
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

from django.forms import ModelForm
from apps.newProduct.models import Product, Variants


from apps.vendor.models import Customer, Transporter, Vendor, VendorDelivery
# from apps.transporter.models import TransporterOrder
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from apps.ordering.utils import create_new_ref_number



def notify_transporter(order_items,transporter):
    connection = get_connection() # uses SMTP server specified in settings.py
    connection.open()

    from_email = settings.DEFAULT_EMAIL_FROM
    to_email = transporter.email
    subject = 'Order confirmation'
    text_content = 'Thank you for the order!'
    html_content = render_to_string(
        'order/email_notify_transporter.html', {'order_items': order_items})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email], connection=connection)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    connection.close()

def notify_vendor(order):
    connection = get_connection()  # uses SMTP server specified in settings.py
    connection.open()
    print("vendor order")
    print(order)
    print("vender")
    print(order.vendors.all())

    from_email = settings.DEFAULT_EMAIL_FROM
    try:

        for vendor in order.vendors.all():
            print(vendor.email)
            to_email = vendor.email
            vendor_item_price = 0
            vendor_items_total_price = 0
            total_quantity = 0
            is_delivery = False
            order_items = OrderItem.objects.filter(order=order)
            delivery_cost = 0
            for items in order_items:
                if vendor == items.vendor:
                    vendor_item_price = items.get_product_total_price()
                    vendor_items_total_price += vendor_item_price*items.quantity
                    total_quantity += items.quantity
                    if not items.product.is_free_delivery:
                        if order.delivery_type == "Vendor_Delivery":
                            delivery_cost = VendorDelivery.objects.get(
                                vendor=vendor).price
                            is_delivery = True
                            if delivery_cost == None:
                                delivery_cost = 0
                                is_delivery = False
                        else:
                            delivery_cost = 0
                            is_delivery = False

            total_cost = float(
                vendor_items_total_price-(order.coupon_discount*vendor_items_total_price/100))
            total_cost += float(delivery_cost)

            vendor_items_total_price = round(
                Decimal(vendor_items_total_price), 2)
            total_cost = round(Decimal(total_cost), 2)

            subject = 'New order - Sokopark'
            text_content = 'You have a new order!'
            html_content = render_to_string(
                'order/email_notify_vendor.html', {'order': order,
                                                   'vendor': vendor,
                                                   'subtotal_cost': vendor_items_total_price,
                                                   'delivery_cost': delivery_cost,
                                                   'is_delivery': is_delivery,
                                                   'grand_total': total_cost,
                                                   'total_quantity': total_quantity})

            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [to_email], connection=connection)
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
    except Exception as e:
        print(e)

    connection.close()
    


def notify_customer(order):
    connection = get_connection()  # uses SMTP server specified in settings.py
    connection.open()
    grand_cost = order.paid_amount + Decimal(order.delivery_cost)
    from_email = settings.DEFAULT_EMAIL_FROM
    to_email = order.email
    subject = 'Order confirmation - Sokopark'
    text_content = 'Thank you for the order!'
    html_content = render_to_string(
        'order/email_notify_customer.html', {'order': order, 'grand_cost': grand_cost})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [
                                 to_email], connection=connection)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    connection.close()


class ShopCart(models.Model):
    user=models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    product=models.ForeignKey(Product, on_delete=models.SET_NULL,null=True)
    variant=models.ForeignKey(Variants, on_delete=models.SET_NULL,null=True,blank=True) #relation with variant
    quantity=models.IntegerField()

    def __str__(self):
        if self.product == None:
            return "No Product Selected"
        else:
            return self.product.title

    @property
    def price(self):
        if self.product == None:
            return 0
        else:
            return round(Decimal(self.product.price),2)


    @property
    def amount(self):
        if self.product == None:
            return 0
        else:
            return round(Decimal(self.quantity * self.product.price),2)

    @property
    def varamount(self):

        if self.variant == None:
            return 0
        else:
            return round(Decimal(self.quantity * self.variant.price),2)

    @property
    def var_dicount_amount(self):
        if self.variant.discount  == 0:
            return 00
        else:
            return round(Decimal(self.quantity * self.variant.get_discounted_price_var()),2)

    @property
    def prodct_dicount_amount(self):
            return round(Decimal(self.quantity * self.product.get_discounted_price()),2)


class ShopCartForm(ModelForm):
    class Meta:
        model=ShopCart
        fields=['quantity']


class Order(models.Model):
    PENDING = 'pending'
    PAID = 'paid'
    CANCELLED = 'cancelled'
    SHIPPED = 'shipped'
    ARRIVED = 'arrived'

    STATUS_CHOICES = (
        (PENDING , 'pending'),
        (PAID , 'paid'),
        (CANCELLED,'cancelled'),
        (SHIPPED, 'Shipped'),
        (ARRIVED, 'Arrived'),
    )
    reference_number = models.CharField(
        max_length=100, default=create_new_ref_number)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    service_provider=models.CharField(max_length=100,default=0)
    momo=models.CharField(max_length=100,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    district=models.CharField(max_length=100,null=True)
    sector=models.CharField(max_length=100,null=True)
    village=models.CharField(max_length=100,null=True)
    cell=models.CharField(max_length=100,null=True)
    delivery_address=models.CharField(max_length=170,null=True)
    delivery_cost=models.DecimalField(max_digits=13,decimal_places=2,default=0)
    subtotal=models.DecimalField(max_digits=13,decimal_places=2,default=0)
    vat=models.DecimalField(max_digits=100,decimal_places=2,default=0)
    delivery_type=models.CharField(max_length=100,null=True)
    company_code = models.CharField(max_length=100, default=000)
    coupon_discount=models.DecimalField(max_digits=13,decimal_places=2,default=0)
    paid_amount=models.DecimalField(max_digits=13,decimal_places=2,default=0)
    is_paid=models.BooleanField(default=False)
    vendors=models.ManyToManyField(Vendor,related_name='orders')
    shipped_date=models.DateTimeField(blank=True,null=True)
    arrived_date=models.DateTimeField(blank=True,null=True)
    status=models.CharField(
        max_length=20,choices=STATUS_CHOICES,default=PENDING
    )
    used_coupon=models.CharField(max_length=50,blank=True,null=True)
    transporter=models.ForeignKey(Transporter, on_delete=models.SET_NULL,blank=True,null=True)
    
    __original_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.__original_status=self.is_paid


    @property
    def getItem(self):
        return OrderItem.objects.filter(order=self)

    class Meta:
        ordering=['-created_at']

    def __str__(self):
        return self.first_name
    
    def getCustomer(self):
        return Customer.objects.filter(email=self.email)

    def grand_paid_amount(self):
        return self.paid_amount + self.delivery_cost

    def get_delivery_cost(self):
        return round(Decimal(self.delivery_cost),2)
    
    def paid(self):
        if self.is_paid:
            return bool(self.items.all().vendor_paid)

    def save(self, *args, **kwargs):
        created = TransporterOrder.objects.filter(order=self).first()
        super(Order, self).save(*args, **kwargs)
        if self.is_paid != self.__original_status:
            if self.is_paid:
                items = OrderItem.objects.filter(order=self.pk)
                for item in items:
                    item.vendor_paid=True
                    item.save()
                notify_customer(self)
                notify_vendor(self)
        if created and self.transporter:
            TransporterOrder.objects.filter(order=self).update(transporter=self.transporter)
        elif self.transporter:
            try:
                order_items = OrderItem.objects.filter(
                    order=self.pk,
                    )
                print("order_items",order_items)
                for pr in order_items:
                    tr_order= TransporterOrder(product= pr.product,quantity=pr.quantity,order=self, transporter=self.transporter)
                    tr_order.save()

                notify_transporter(order_items,self.transporter)
            except Exception as e:
                print(e)
        else:
            TransporterOrder.objects.filter(order=self).delete()
    #

# Create your models here.
class TransporterOrder(models.Model):
    ORDERED = 'ordered'
    PICKEDUP = 'picked'
    DELIVERED = 'delieverd'

    STATUS_CHOICES = (
        (ORDERED, 'Ordered'),
        (PICKEDUP, 'Picked Up'),
        (DELIVERED, 'Delieverd'),
    )

    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    quantity=models.IntegerField(default=1)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,null=True)
    status=models.CharField(
        max_length=20,choices=STATUS_CHOICES,default=ORDERED
    )
    transporter=models.ForeignKey(Transporter, on_delete=models.SET_NULL,null=True)


    def __str__(self):
        if self. product:
            return '%s' % (self.product.title)
        else:
            return '%s' % ("-")

class OrderItem(models.Model):
    order=models.ForeignKey(
        Order,related_name='items',on_delete=models.CASCADE
    )
    product=models.ForeignKey(Product, on_delete=models.SET_NULL,null=True,blank=True,related_name='items')
    variant=models.ForeignKey(Variants, on_delete=models.SET_NULL,null=True,blank=True,related_name='items')
    vendor=models.ForeignKey(
        Vendor,related_name='items',on_delete=models.CASCADE
    )
    vendor_paid=models.BooleanField(default=False)
    price=models.DecimalField(max_digits=8,decimal_places=2)
    price_no_vat=models.DecimalField(max_digits=8,decimal_places=2,default=0)
    quantity=models.IntegerField(default=1)
    is_variant=models.BooleanField(default=False)
    vat=models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True)
    total=models.DecimalField(max_digits=8,decimal_places=2,default=0)
    
    

    def __str__(self):
        return '%s' % self.id
    
    def payed(self, *args, **kwargs):
        if self.order.is_paid:
            return self.vendor_paid == True

    def get_vat_price(self):
        if not self.is_variant:
            vat=self.product.get_vat_price()
        else:
            vat=self.variant.get_vat_price()
        vat=round(Decimal(vat),2)
        return round(Decimal(vat),2)    
    
    def get_total(self):
        total=self.price*self.quantity
        return round(Decimal(total),2)


    def get_discounted_price(self):
        if not self.is_variant:
            price=self.product.get_discounted_price()
        else:
            price =self.variant.get_discounted_price()
        price=round(Decimal(price),2)
        return round(Decimal(price),2)

    def vendor_name(self):
        if self.product:
            return '%s' % (self.product.vendor.company_name)
        else:
            return '%s' % ("-")
    def vendor_address(self):
        if self.product:
            return '%s' % (self.product.vendor.address)
        else:
            return '%s' % ("-")

    def customer_name(self):
        if self.order:
            return '%s %s' % (self.order.first_name, self.order.last_name)
        else:
            return '%s' % ("-")
    def customer_address(self):
        if self.order:
            return '%s, %s, %s, %s, %s' % (self.order.address,self.order.district,self.order.sector,self.order.village,self.order.cell)
        else:
            return '%s' % ("-")
    def customer_phone(self):
        if self.order:
            return '%s' % (self.order.phone)
        else:
            return '%s' % ("-")

    def get_product_name(self):
        if not self.is_variant:
            title=self.product.title
        else:
            title =self.variant.title
        return title

    
    def get_product_total_price(self):
        if not self.is_variant:
            price=self.product.get_discounted_price()
        else:
            price =self.variant.get_discounted_price()
        return round(Decimal(price),2)

    def get_product_no_vat(self):
        if not self.is_variant:
            price_no_vat=self.product.get_vat_exclusive_price()
        else:
            price_no_vat=self.variant.get_vat_exclusive_price() 
        return round(Decimal(price_no_vat),2)       
    
    def get_subtotal_vat_exlusive(self):
        if not self.is_variant:
            return round(Decimal(round(Decimal(self.product.get_vat_exclusive_price() * self.quantity),2)),2)
        else:
            return round(Decimal(round(Decimal(self.variant.get_vat_exclusive_price() * self.quantity),2)),2)
                

    def get_total_price(self):
        return round(Decimal(self.price * self.quantity),2)

    def get_total_with_coupon(self):
        return round(Decimal((self.price * self.quantity)* self.order.coupon_discount / 100),2)

    
    def subtotal(self):
        return self.quantity * self.get_discounted_price()
