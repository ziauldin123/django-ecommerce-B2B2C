from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from apps.blog.models import Post


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['frontpage', 'contact', 'about', 'pricing', 'vendors', 'termsandconditions', 'frequently_asked_questions']

    def location(self, item):
        return reverse(item)




class ProductSitemap(Sitemap):
    def lastmod(self, obj):
        return obj.date_added


class PostSitemap(Sitemap):
    def items(self):
        return Post.objects.all()
