#
#

from django.urls import path

#
#

from . import views

#
#

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('sitemap/',views.sitemap,name='sitemap'),
    path('pricing/', views.pricing,name='pricing'),
    path('frequently_asked_questions/', views.frequently_asked_questions,
         name='frequently_asked_questions'),
    path('termsandconditions/', views.termsandconditions,
         name='termsandconditions'),
    path('privacy_policy/', views.privacy_policy,
         name='privacy_policy'),
    path('vendor_guidelines/', views.vendor_guidelines,
         name='vendor_guidelines'),

]

handler404 = 'apps.core.views.error_404_view'
