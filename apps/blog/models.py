from io import BytesIO
from PIL import Image

from django.core.files import File

from django.db import models
from django.db.models.fields import SlugField
from django.utils.text import slugify
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from django.core.files.base import ContentFile


class Tag(models.Model):
    tag = models.CharField(max_length=255)
    slug = models.SlugField(null=True,blank=True)

    def __str__(self):
        return self.tag

    def save(self, *args, **kwargs):
        self.slug = slugify(self.tag)
        super(Tag, self).save(*args, **kwargs)    

class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    author_detail = models.TextField(blank=True, null=True)
    tag = models.ForeignKey(Tag,on_delete=models.CASCADE,null=True,blank=True)
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

        if self.image and not self.image.url.endswith('.webp'):
            imm = Image.open(self.image).convert("RGB")
            original_width, original_height = imm.size
            aspect_ration = round(original_width / original_height)
            if aspect_ration < 1:
                aspect_ration = 1
            desired_height = 500
            desired_width = desired_height * aspect_ration
            imm.thumbnail((desired_width,desired_height), Image.ANTIALIAS) 
            new_image_io = BytesIO()
            imm.save(new_image_io,format="WEBP", quality=70) 
            self.image.save(
                self.title[:40]+".webp",
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )  

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
