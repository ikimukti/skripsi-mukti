from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

# models import
from myapp.models import Image
from django.contrib.auth.models import User
from django.db.models import Count

# forms import
from myapp.forms import ImageForm

from django.urls import reverse_lazy

# cv2 import
import cv2

# numpy import
import numpy as np


class ImageUpdateView(UpdateView):
    model = Image
    template_name = "myapp/image/image_update.html"
    form_class = ImageForm
    success_url = reverse_lazy("myapp:image_list")
    failure_url = "/image/update/"

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Update"
        context["contributor"] = "WeeAI Team"
        context["content"] = "Welcome to WeeAI! Update Image"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        return context

    # invalid form
    def form_invalid(self, form):
        print(form.cleaned_data)
        return super().form_invalid(form)

    # form save
    def form_valid(self, form):
        # rewrite save method in form
        # get image channel from form data image file
        # cv2 image channel get image channel from shape
        image_channel = cv2.imread(
            form.cleaned_data["image"].temporary_file_path()
        ).shape[2]
        # rewrite channel in form data
        form.instance.channel = image_channel
        # cv2 get dpi from image file
        image_dpi = cv2.imread(form.cleaned_data["image"].temporary_file_path()).shape[
            0
        ]
        # rewrite dpi in form data
        form.instance.dpi = image_dpi
        return super().form_valid(form)

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class ImageDeleteView(DeleteView):
    model = Image
    template_name = "myapp/image/image_delete.html"
    success_url = reverse_lazy("myapp:image_list")

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Delete"
        context["contributor"] = "WeeAI Team"
        context["content"] = "Welcome to WeeAI! Delete Image"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class ImageUploadView(CreateView):
    form_class = ImageForm
    template_name = "myapp/image/image_upload.html"
    failure_url = "/image/upload/"
    # success_url = reverse_lazy('image_list')  # Assuming you have a URL name for the image list view

    # invalid form
    def form_invalid(self, form):
        print(form.cleaned_data)
        return super().form_invalid(form)

    # form save
    def form_valid(self, form):
        # rewrite save method in form
        # rewrite channel in form data
        # form.instance.channel = image_channel
        image_data = form.cleaned_data["image"].read()
        image_array = np.frombuffer(image_data, np.uint8)
        image_channel = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[2]
        form.instance.channel = image_channel
        # rewrite dpi in form data
        image_dpi = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[0]
        form.instance.dpi = image_dpi
        return super().form_valid(form)

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Upload"
        context["contributor"] = "WeeAI Team"
        context["content"] = "Welcome to WeeAI! Create Image"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class ImageSummaryView(ListView):
    model = Image
    template_name = "myapp/image/image_summary.html"
    context_object_name = "images"
    ordering = ["-created_at"]
    paginate_by = 8

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Summary"
        context["contributor"] = "WeeAI Team"
        context["content"] = "Welcome to WeeAI! Image Summary"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        # categories uploader name with name of uploader in User model
        uploaders_name = (
            User.objects.filter(image__isnull=False).values("username").distinct()
        )
        context["uploaders_name"] = uploaders_name
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class ImageListView(ListView):
    model = Image
    template_name = "myapp/image/image_list.html"
    context_object_name = "images"
    ordering = ["-created_at"]
    paginate_by = 8

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image List"
        context["contributor"] = "WeeAI Team"
        context["content"] = "Welcome to WeeAI!"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        # categories uploader name with name of uploader in User model
        uploaders_name = (
            User.objects.filter(image__isnull=False)
            .distinct()
            .values_list("username", flat=True)
        )
        # count Image by uploader
        uploaders_count = (
            Image.objects.values("uploader")
            .distinct()
            .annotate(count=Count("uploader"))
            .values_list("count", flat=True)
        )
        # context['uploaders'] = {'name': uploaders_name, 'count': uploaders_count}
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({"name": name, "count": count})
        context["uploaders"] = uploaders
        # categories color name
        context["colors"] = self.model.objects.values_list(
            "color", flat=True
        ).distinct()
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class ImageUploaderView(ListView):
    model = Image
    template_name = "myapp/image/image_by_uploader.html"
    context_object_name = "images"
    ordering = ["-created_at"]
    paginate_by = 8

    # get queryset
    def get_queryset(self):
        uploader = self.kwargs["uploader"]
        return Image.objects.filter(uploader__username=uploader)

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Capitalize first letter of uploader
        context["title"] = "Image Uploader " + self.kwargs["uploader"].capitalize()
        context["kwargs_uploader"] = self.kwargs["uploader"]
        context["contributor"] = "WeeAI Team"
        context["content"] = "Welcome to WeeAI!"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        # categories uploader name with name of uploader in User model
        uploaders_name = (
            User.objects.filter(image__isnull=False)
            .distinct()
            .values_list("username", flat=True)
        )
        # count Image by uploader
        uploaders_count = (
            Image.objects.values("uploader")
            .distinct()
            .annotate(count=Count("uploader"))
            .values_list("count", flat=True)
            .order_by("-count")
        )
        # context['uploaders'] = {'name': uploaders_name, 'count': uploaders_count}
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({"name": name, "count": count})
        context["uploaders"] = uploaders
        # categories color name
        context["colors"] = self.model.objects.values_list(
            "color", flat=True
        ).distinct()
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class ImageDetailView(DetailView):
    model = Image
    template_name = "myapp/image/image_detail.html"
    context_object_name = "image"

    # update context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Detail"
        context["contributor"] = "WeeAI Team"
        context["content"] = "Welcome to WeeAI!"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        # categories uploader by uploader name in Image model uploader_id
        context["uploader"] = User.objects.get(id=self.object.uploader_id)
        # get 5 image by uploader lastest
        context["images"] = Image.objects.filter(
            uploader_id=self.object.uploader_id
        ).order_by("-created_at")[:5]

        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)
