from django.urls import path

from . import views
from apps.home.views import product_detail
from apps.product import views

urlpatterns = [
    path('collections/<int:pk>/', views.CollectionView.as_view(), name='collections'),
    path('search/', views.search, name='search'),
    path('product/<int:pk>/wishlist-add/',
         views.WishListAddView.as_view(), name='wishlist-add'),
    path('product/<int:pk>/compare/',
         views.CompareView.as_view(), name='product-compare'),
    path('product/comparing/', views.ComparingView.as_view(),
         name='product-comparing'),
    path(
        '<int:id>/<slug:vendor_slug>/<slug:category_slug>/<slug:subcategory_slug>/<slug:subsubcategory_slug>/<slug:slug>/',
        product_detail,
        name='product'
    ),
    path('variant/compare/', views.variantCompare, name='compare-variant'),
    path('variant/wishlist/', views.WishlistAddVariant.as_view(),
         name='addwishlistvariant'),
    path('compare/delete/<int:id>/', views.deleteCompare, name='delete_compare'),
    path('compare/deletevariant/<int:id>',
         views.deleteVariantCompare, name='deleteVariantCompare'),
    path('wishlist/delete/<int:id>/', views.wishlistDelete, name='wishlistdelete'),
    path('brands', views.brands, name='brands')
]
