from gettext import Catalog
from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from apps.blog.models import Post
from apps.newProduct.models import Product, Category
from apps.vendor.models import Vendor


class StaticViewSitemap(Sitemap):
    template_name = 'core/sitemaps.html'

    def items(self):
        return ['frontpage', 'contact', 'about', 'pricing', 'termsandconditions', 'privacy_policy', 'frequently_asked_questions', 'vendor_guidelines', ]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    template_name = 'core/sitemaps.html'

    def get(self):
        return Catalog.objects.all()

    def items(self):
        return Category.objects.all()


class ProductSitemap(Sitemap):
    template_name = 'core/sitemaps.html'

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.created_at


class PostSitemap(Sitemap):
    template_name = 'core/sitemaps.html'

    def items(self):
        return Post.objects.all()


class VendorSitemap(Sitemap):
    template_name = 'core/sitemaps.html'

    def items(self):
        return Vendor.objects.all()
