from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='services'),
    path('<int:id>/',views.get_category,name='category-service'),
    path('<int:id>/<slug:service_slug>/<slug:slug>/',views.get_service_provider,name='service_provider'),
    path('become-service-provider/',views.become_service_provider,name='become-service-provider'),
    path('my-account-service/',views.myServiceAccount,name='mySerrviceAccount'),
    path('update-profile/',views.upload_profile,name='update_profile'),
    path('update-profile/<int:id>/',views.update_profile,name='edit_profile')
]