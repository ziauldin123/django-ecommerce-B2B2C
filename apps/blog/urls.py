from django.urls import path

from . import views

urlpatterns = [

    path('', views.index, name='blog'),
    path('<int:id>/', views.detail, name='detail'),
    path('<slug:slug>/',views.tagged,name='tag')
]
