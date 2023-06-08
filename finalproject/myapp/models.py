from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from .utils.generate import generate_unique_image_name
from django.urls import reverse

# Create your models here.
class Image(models.Model):
    id = models.AutoField(primary_key=True)
    # multiple images
    image = models.ImageField(upload_to='static/images/uploads/', blank=False, null=False)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    width = models.IntegerField()
    height = models.IntegerField()
    size = models.IntegerField()
    channel = models.CharField(max_length=10)
    format = models.CharField(max_length=10)
    dpi = models.IntegerField()
    distance = models.IntegerField()
    color = models.CharField(max_length=32 ,blank=True, null=True)
    segmented = models.BooleanField(default=False)

    # override delete method
    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)

    # override update method
    def update(self, *args, **kwargs):
        # hash image name to make it unique
        unique_name = generate_unique_image_name(self.image.name)
        # width, height, size, channel, format, dpi, distance, color
        self.width = self.image.width
        self.height = self.image.height
        self.size = self.image.size
        self.channel = 3
        # shape to get channel
        self.format = self.image.name.split('.')[-1]
        # get dpi from image
        self.dpi = 300
        # set file format
        self.slug = slugify(unique_name + '.' + self.image.name.split('.')[-1])
        self.image.name = unique_name + '.' + self.image.name.split('.')[-1]
        super(Image, self).save(*args, **kwargs)

    # override save method
    def save(self, *args, **kwargs):
        # hash image name to make it unique
        unique_name = generate_unique_image_name(self.image.name)
        # width, height, size, channel, format, dpi, distance, color
        self.width = self.image.width
        self.height = self.image.height
        self.size = self.image.size
        self.channel = 3
        # shape to get channel
        self.format = self.image.name.split('.')[-1]
        # get dpi from image
        self.dpi = 300
        # set file format
        self.slug = slugify(unique_name + '.' + self.image.name.split('.')[-1])
        self.image.name = unique_name + '.' + self.image.name.split('.')[-1]
        super(Image, self).save(*args, **kwargs)

    def get_absolute_url(self, *args, **kwargs):
        return reverse('myapp:image_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return "{}. {}".format(self.id, self.image.name, self.uploader.username)

    
