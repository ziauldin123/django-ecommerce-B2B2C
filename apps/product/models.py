from io import BytesIO
from os import name
from PIL import Image
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.expressions import Col
from django.db.models.fields import CharField
from autoslug import AutoSlugField
from django.utils.safestring import mark_safe

from django.core.files import File
from django.db import models
from django.db.models import CASCADE

from apps.vendor.models import Vendor
from django.core.validators import MinValueValidator, MaxValueValidator



class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/' % (self.slug)


