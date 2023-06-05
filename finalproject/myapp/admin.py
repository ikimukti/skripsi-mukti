from django.contrib import admin

# Register your models here.
from .models import Image

class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', 'created_at', 'updated_at')

admin.site.register(Image)

