from io import BytesIO
from PIL import Image

from django.core.files import File

from django.db import models
from django.db.models.fields import SlugField
from django.utils.text import slugify
from autoslug import AutoSlugField


class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    author_detail = models.TextField(blank=True, null=True)
    slug = AutoSlugField(populate_from='title')
    intro = models.TextField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/' % (self)

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return self.thumbnail.url
            else:
                return 'https://via.placeholder.com/240x180.jpg'

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=100)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail
