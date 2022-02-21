from django.urls import path

from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart'),
    path('contact_info', views.contact_info, name='contact_info'),
    path('payment_check', views.payment_check, name='payment_check'),
    path('waiting', views.success, name='waiting'),

    path('district_sector', views.district_sector, name='district_sector'),
    path('district_sector_cell', views.district_sector_cell, name='district_sector_cell'),
    path('district_sector_cell_village', views.district_sector_cell_village, name='district_sector_cell_village')    
]
