from unicodedata import name
from django.urls import  path,include

from apps.rental.forms import CreateMake,CreateRoom,CreateEngine,CreateApplication,CreateCapacity,CreateYear,CreateAmenity,CreateYear,CreateItemModel

from . import views

urlpatterns=[

    path("select2/", include("django_select2.urls")),
    path('create-make/', CreateMake.as_view(), name='add_make',),
    path('create-room/', CreateRoom.as_view(), name='add_rooms',),
    path('create-application/', CreateApplication.as_view(), name='add_application',),
    path('create-capacity/', CreateCapacity.as_view(), name='add_capacity',),
    path('create-year/', CreateYear.as_view(), name='add_year',),
    path('create-engine/', CreateEngine.as_view(), name='add_engine',),
    path('create-amenity/', CreateAmenity.as_view(), name='add_amenity',),
    path('create-model/', CreateItemModel.as_view(), name='add_model',),

    path('', views.index, name='rental'),
    path('<int:id>/<slug:category_slug>/', views.category, name='category'),
    path('<int:id>/<slug:category_slug>/<slug:slug>/', views.item_Detail, name='item-detail'),
    path('items/', views.get_user_items, name='items'),
    path('add-item/', views.add_item, name='add_item'),
    path('edit-item/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete_item/<int:pk>/', views.delete_item, name='delete_item'),

    
]