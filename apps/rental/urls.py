from unicodedata import name
from django.urls import  path

from . import views

urlpatterns=[
    path('',views.index,name='rental'),
    path('<int:id>/<slug:category_slug>/',views.category,name='category'),
    path('<int:id>/<slug:category_slug>/<slug:slug>/',views.item_Detail,name='item-detail'),
    path('items/',views.get_user_items,name='items'),
    path('add-item/',views.add_item,name='add_item'),
    path('edit-item/<int:pk>/',views.edit_item,name='edit_item'),
    path('delete_item/<int:pk>/',views.delete_item,name='delete_item')
]