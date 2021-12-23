from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addcomment/<int:id>', views.addcomment, name='addcomment'),
]
# path('<slug:category_slug>/', views.category, name='category'),
# path('<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory, name='subcategory'),
# path(
#         '<slug:category_slug>/<slug:subcategory_slug>/<slug:subsubcategory_slug>/',
#         views.subsubcategory,
#         name='subsubcategory'
#     )