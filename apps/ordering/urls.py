from django.urls import path

from apps.ordering import views 

urlpatterns=[
    path('',views.index,name='index')
]