from apps.newProduct.models import Category, SubCategory, SubSubCategory
from apps.rental import models


def menu_categories(request):
    categories = Category.objects.all()
    for category in categories:
        subcategories = SubCategory.objects.filter(category=category)
        for subcategory in subcategories:
            subsubcategories = SubSubCategory.objects.filter(sub_category = subcategory)
            if len(subsubcategories) > 0:
                subcategory.children = subsubcategories
                subcategory.has_children = True
            else:
                subcategory.has_children = False
        if len(subcategories) > 0:
            category.children = subcategories
            category.has_children = True
        else:
            category.has_children = False
    return {'menu_categories': categories}

def rental_categories(request):
    categories = models.Category.objects.all()

    return {'rental_categories':categories}