from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from .utils.generate import generate_unique_image_name
from django.urls import reverse


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # additional fields
    profile_pic = models.ImageField(
        upload_to="static/images/profile_pics/", blank=True, null=True
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}. {}".format(self.id, self.user.username)


# Create your models here.
class Image(models.Model):
    id = models.AutoField(primary_key=True)
    # multiple images
    image = models.ImageField(
        upload_to="static/images/uploads/", blank=False, null=False
    )
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
    COLOR_CHOICES = [
        ("red", "Red"),
        ("green", "Green"),
        ("blue", "Blue"),
        ("yellow", "Yellow"),
        ("orange", "Orange"),
        ("purple", "Purple"),
        ("pink", "Pink"),
        ("brown", "Brown"),
        ("black", "Black"),
        ("white", "White"),
        ("gray", "Gray"),
        ("cyan", "Cyan"),
        ("magenta", "Magenta"),
        ("lime", "Lime"),
        ("olive", "Olive"),
        ("maroon", "Maroon"),
        ("navy", "Navy"),
        ("teal", "Teal"),
        ("aqua", "Aqua"),
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("bronze", "Bronze"),
        ("beige", "Beige"),
        ("azure", "Azure"),
        ("ivory", "Ivory"),
        ("lavender", "Lavender"),
        ("coral", "Coral"),
        ("salmon", "Salmon"),
        ("tan", "Tan"),
        ("turquoise", "Turquoise"),
        ("violet", "Violet"),
        ("indigo", "Indigo"),
        ("crimson", "Crimson"),
        ("fuchsia", "Fuchsia"),
        ("orchid", "Orchid"),
        ("plum", "Plum"),
        ("khaki", "Khaki"),
        ("chocolate", "Chocolate"),
        ("tomato", "Tomato"),
        ("wheat", "Wheat"),
        ("snow", "Snow"),
        ("seashell", "Seashell"),
        ("salmon", "Salmon"),
    ]
    color = models.CharField(
        max_length=20, choices=COLOR_CHOICES, default="white", blank=False, null=False
    )
    segmented = models.BooleanField(default=False)

    # override delete method
    def delete(self, *args, **kwargs):
        # delete image
        self.image.delete(False)  # False means don't save model
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
        self.format = self.image.name.split(".")[-1]
        # get dpi from image
        self.dpi = 300
        # set file format
        self.slug = slugify(unique_name + "." + self.image.name.split(".")[-1])
        self.image.name = unique_name + "." + self.image.name.split(".")[-1]
        super(Image, self).save(*args, **kwargs)

    # override save method
    def save(self, *args, **kwargs):
        # hash image name to make it unique
        unique_name = generate_unique_image_name(self.image.name)
        # width, height, size, channel, format, dpi, distance, color
        self.width = self.image.width
        self.height = self.image.height
        self.size = self.image.size
        # shape to get channel
        self.format = self.image.name.split(".")[-1]
        # get dpi from image
        # set file format
        self.slug = slugify(unique_name + "." + self.image.name.split(".")[-1])
        self.image.name = unique_name + "." + self.image.name.split(".")[-1]
        super(Image, self).save(*args, **kwargs)

    def get_absolute_url(self, *args, **kwargs):
        return reverse("myapp:image_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return "{}. {}".format(self.id, self.image.name, self.uploader.username)


class ImagePreprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    image_preprocessing = models.ImageField(
        upload_to="static/images/preprocessing/", blank=False, null=False
    )
    image_ground_truth = models.ImageField(
        upload_to="static/images/ground_truth/", blank=False, null=False
    )
    # column to store image preprocessing parameters
    # preprocessing
    # 1. resize
    resize = models.BooleanField(default=False)
    resize_width = models.IntegerField(blank=True, null=True)
    resize_height = models.IntegerField(blank=True, null=True)
    # 2. grayscale
    grayscale = models.BooleanField(default=False)
    # 3. blur
    blur = models.BooleanField(default=False)
    blur_radius = models.IntegerField(blank=True, null=True)
    # 4. sharpen
    sharpen = models.BooleanField(default=False)
    sharpen_radius = models.IntegerField(blank=True, null=True)
    sharpen_percent = models.IntegerField(blank=True, null=True)
    # 5. brightness
    brightness = models.BooleanField(default=False)
    brightness_percent = models.IntegerField(blank=True, null=True)
    # 6. contrast
    contrast = models.BooleanField(default=False)
    contrast_percent = models.IntegerField(blank=True, null=True)
    # 7. smooth
    smooth = models.BooleanField(default=False)
    smooth_radius = models.IntegerField(blank=True, null=True)
    # 8. edge enhance
    edge_enhance = models.BooleanField(default=False)
    edge_enhance_radius = models.IntegerField(blank=True, null=True)
    # 9. find edges
    find_edges = models.BooleanField(default=False)
    find_edges_radius = models.IntegerField(blank=True, null=True)
    # 10. contour
    contour = models.BooleanField(default=False)
    contour_radius = models.IntegerField(blank=True, null=True)
    # 11. enhance
    enhance = models.BooleanField(default=False)
    enhance_percent = models.IntegerField(blank=True, null=True)
    # 12. colorize
    colorize = models.BooleanField(default=False)
    colorize_color = models.CharField(max_length=20, blank=True, null=True)
    # 13. posterize
    posterize = models.BooleanField(default=False)
    posterize_bits = models.IntegerField(blank=True, null=True)
    # 14. solarize
    solarize = models.BooleanField(default=False)
    solarize_threshold = models.IntegerField(blank=True, null=True)
    # 15. invert
    invert = models.BooleanField(default=False)
