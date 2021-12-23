# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from . import views

urlpatterns = [

    # The home page
    # path('', views.index, name='dashboard'),
    path('order/<int:order_id>', views.orderDetails, name='orderDetails'),
    path('api/changeOrderStatus/<int:id>/<str:val>', views.changeOrderStatus, name='changeOrderStatus'),
    path('api/changeVendorEnalbed/<int:id>/<str:val>', views.changeVendorEnalbed, name='changeVendorEnalbed'),
    path('api/changeProductVisible/<int:id>/<str:val>', views.changeProductVisible, name='changeProductVisible'),
    path('api/changeProductLimit/<int:id>/<str:val>', views.changeProductLimit, name='changeProductLimit'),
    path('<slug:category_slug>/<slug:subcategory_slug>/<slug:subsubcategory_slug>/<slug:product_slug>', views.product_admin, name='product_admin'),
    # path('api/changeOrderStatus/<int:id>/<str:val>', views.changeOrderStatus, name='changeOrderStatus'),
    # path('api/changeOrderStatus/<int:id>/<str:val>', views.changeOrderStatus, name='changeOrderStatus'),
    # path('api/changeOrderStatus/<int:id>/<str:val>', views.changeOrderStatus, name='changeOrderStatus'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
