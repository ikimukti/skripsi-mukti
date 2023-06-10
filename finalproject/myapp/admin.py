from django.contrib import admin

# Register your models here.
from .models import Image, UserProfile


class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ("slug", "created_at", "updated_at")


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "user")


admin.site.register(UserProfile)

admin.site.register(Image)
