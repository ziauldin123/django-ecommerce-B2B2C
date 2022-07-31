from django.urls import path

from . import views

urlpatterns = [
    # path('', views.cart_detail, name='cart'),
    path('district_sector', views.district_sector, name='district_sector'),
    path('district_sector_cell', views.district_sector_cell, name='district_sector_cell'),
    path('district_sector_cell_village', views.district_sector_cell_village, name='district_sector_cell_village'),
    path('request_quatation/<int:id>', views.request_quatation, name='request_quatation')    
]
