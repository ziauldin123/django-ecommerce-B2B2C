from unicodedata import name
from django.urls import  path

from . import views

urlpatterns=[
    path('',views.index,name='rental'),
    path('<int:id>',views.category,name='category'),
    path('<int:id>/<slug:category_slug>/<slug:slug>/',views.item_Detail,name='item-detail')
]