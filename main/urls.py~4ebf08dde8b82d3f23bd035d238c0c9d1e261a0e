"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django import urls
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static

from apps.cart.views import check_add_qty,contact_info, payment_check,success
from apps.newsletter.api import api_add_subscriber
from apps.coupon.api import api_can_use
from apps.home import views
from apps.ordering import views as orderview
from apps.product import views as new
from django.views.static import serve
from django.conf.urls import url


from django.contrib.sitemaps.views import sitemap

from .sitemaps import StaticViewSitemap,  PostSitemap, CategorySitemap, ProductSitemap, VendorSitemap


from apps.vendor import views as vendor_views

sitemaps = {'static': StaticViewSitemap, 'post': PostSitemap,
            'category': CategorySitemap, 'product': ProductSitemap, 'vendor': VendorSitemap,
            }


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    path('users/', include('apps.vendor.urls')),
    path('home/', include('apps.home.urls')),
    path('cart/', include('apps.cart.urls')),
    path('blog/', include('apps.blog.urls')),
    path('transporter/', include('apps.transporter.urls')),
    path('api/add_subscriber/', api_add_subscriber, name='api_add_subscriber'),
    path('api/can_use/', api_can_use, name='api_can_use'),
    path('api/check_add_qty/<int:product_id>/<int:num>/',
         check_add_qty, name='check_add_qty'),
    path('activate/<slug:uidb64>/<slug:token>/',
         vendor_views.activate, name='activate'),
    path('activate_password/<slug:uidb64>/<slug:token>/',
         vendor_views.activate_password, name='activate_password'),
    path('', include('apps.core.urls')),
    path('', include('apps.product.urls')),
    path('newProduct/', include('apps.newProduct.urls')),
    path('ajaxcolor/', views.ajaxcolor, name='ajaxcolor'),
    path('ajaxcolorWeight/',views.ajaxcolorWeigth, name='ajaxcolor-weight'),
    path('cart/',orderview.shopcart,name='shopcart'),
    path('checkout', contact_info, name='contact_info'),
    path('payment_check', payment_check, name='payment_check'),
    path('awaiting_payment', success, name='waiting'),
    path('order/addtoshopcart/<int:id>', orderview.addtoshopcart, name='addtoshopcart'),
    path('updateshopcart',orderview.update, name='update'),
    path('order/deletefromcart/<int:id>', orderview.deletefromcart, name='deletefromcart'),
    path('customer/order-detail/<int:id>/',
         vendor_views.order_detail, name='order_details'),
    path('vendor/order_details/<int:id>/',
         vendor_views.vendor_order_detail, name='vendor-order-detail'),
    path('<slug:category_slug>/', new.category, name='category'),
    path('<slug:category_slug>/<slug:subcategory_slug>/',
         new.subcategory, name='subcategory'),
    path(
        '<slug:category_slug>/<slug:subcategory_slug>/<slug:subsubcategory_slug>/',
        new.subsubcategory,
        name='subsubcategory'
    ),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.view.sitemap'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
urlpatterns += [url(r'media/(?P<path>.*)$', serve,
                    {'document_root': settings.MEDIA_ROOT, }), ]

# if settings.DEBUG:
urlpatterns += [url(r'static/(?P<path>.*)$', serve,
                    {'document_root': settings.STATIC_ROOT, }), ]
