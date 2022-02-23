from django.contrib.auth import views as auth_views
from django.urls import path, include


from . import views, forms

urlpatterns = [
    path("select2/", include("django_select2.urls")),
    path('customer/<int:pk>/wishlist/',
         views.WishListView.as_view(), name='wishlist'),
    path('delivery_cost/', views.delivery_cost, name='delivery_cost'),
    path('vendor_admin/', views.vendor_admin, name='vendor_admin'),

    path('create-length/', forms.CreateLength.as_view(), name='add_length',),
    path('create-width/', forms.CreateWidth.as_view(), name='add_width',),
    path('create-brand/', forms.CreateBrand.as_view(), name='add_brand',),
    path('create-color/', forms.CreateColor.as_view(), name='add_color',),
    path('create-weight/', forms.CreateWeight.as_view(), name='add_weight',),
    path('create-height/', forms.CreateHeight.as_view(), name='add_height',),
    path('create-size/', forms.CreateSize.as_view(), name='add_size',),


    path('become-vendor/', views.become_vendor, name='become_vendor'),
    path('products/', views.vendor_products, name='products'),
    path('order-history/', views.order_history, name='vendor_orders'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-variant/', views.add_variant, name='add_variant'),
    path('add-product-with-variant/', views.add_product_with_variant,
         name='add_product_without_variant'),
    path('edit-vendor/', views.edit_vendor, name='edit_vendor'),
    path('add-product-image/<int:pk>/',views.add_productimage, name='add_product_image'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    #     path('edit-productimage/<int:pk>/',
    #          views.edit_productimage, name='edit_productimage'),
    path('remove-opening/<int:pk>/', views.remove_opening, name='remove_opening'),
    path('del-productimage/<int:pk>/',
         views.del_productimage, name='del_productimage'),

    path('customer/myaccount/', views.MyAccount.as_view(), name='myaccount'),
    path('customer/order-history',
         views.OrderHistory.as_view(), name='orderhistory'),
    path('upload_logo/', views.upload_logo, name='upload_logo'),
    path('become-customer/', views.become_customer, name='become_customer'),
    path('become-transporter/', views.become_transporter,
         name='become_transporter'),
    path('request_restore_password/', views.request_restore_password,
         name='request_restore_password'),
    path('restore_password/', views.restore_password, name='restore_password'),


    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('login/', auth_views.LoginView.as_view(template_name='vendor/login.html'), name='login'),

    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('changing_password/', views.changing_password_view,
         name="changing_password"),
    # path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),

    path('vendors/', views.vendors, name='vendors'),
    path('vendor/<slug:slug>/', views.vendor, name='vendor'),
    path('working_hours/', views.working_hours, name='working_hours')

]
