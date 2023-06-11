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
from myapp.models import Image, ImagePreprocessing
from django.contrib.auth.models import User
from django.db.models import Count
from django.db import transaction

# forms import
from myapp.forms import ImageForm

from django.urls import reverse_lazy

# cv2 import
import cv2

# numpy import
import numpy as np
from PIL import Image as PILImage

# PILImageEnhance
from PIL import ImageEnhance as PILImageEnhance
from django.core.files.base import ContentFile
import io
import uuid
import scipy.ndimage.filters as filters

# datetime import
from datetime import datetime


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

    # override post method
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


def process_and_save_image_preprocessing(image_obj, image_array, parameters):
    original_image = PILImage.fromarray(cv2.imdecode(image_array, cv2.COLOR_BGR2RGB))
    otw_gray = np.array(original_image)
    original_image_gray = cv2.cvtColor(otw_gray, cv2.COLOR_BGR2GRAY)

    for param in parameters:
        scale = param["scale"]
        brightness = param["brightness"]
        contrast = param["contrast"]
        spatial_filter = param["spatial_filter"]

        preprocessing_instance = ImagePreprocessing()
        preprocessing_instance.image = image_obj

        # Resize
        resized_image = original_image.resize(
            (int(original_image.width * scale), int(original_image.height * scale))
        )
        resized_image_stream = io.BytesIO()
        resized_image.save(resized_image_stream, format="JPEG")
        resized_image_stream.seek(0)

        preprocessing_instance.resize = True
        preprocessing_instance.resize_width = resized_image.width
        preprocessing_instance.resize_height = resized_image.height
        preprocessing_instance.resize_percent = scale * 100

        # Adjust brightness
        enhanced_image = PILImageEnhance.Brightness(resized_image).enhance(brightness)

        preprocessing_instance.brightness = True
        preprocessing_instance.brightness_percent = brightness * 100

        # Adjust contrast
        enhanced_image = PILImageEnhance.Contrast(enhanced_image).enhance(contrast)

        preprocessing_instance.contrast = True
        preprocessing_instance.contrast_percent = contrast * 100

        # Apply spatial filter
        filtered_image = None
        filter_type, filter_size = spatial_filter

        if filter_type == "mean_filter":
            filtered_image = filters.uniform_filter(
                original_image_gray, size=filter_size
            )

            preprocessing_instance.mean_filter = True
            preprocessing_instance.mean_filter_size = filter_size
            preprocessing_instance.median_filter = False
            preprocessing_instance.gaussian_filter = False

        elif filter_type == "median_filter":
            filtered_image = filters.median_filter(
                original_image_gray, size=filter_size
            )

            preprocessing_instance.median_filter = True
            preprocessing_instance.median_filter_size = filter_size
            preprocessing_instance.mean_filter = False
            preprocessing_instance.gaussian_filter = False

        elif filter_type == "gaussian_filter":
            sigma = filter_size / 6
            filtered_image = filters.gaussian_filter(original_image_gray, sigma=sigma)

            preprocessing_instance.gaussian_filter = True
            preprocessing_instance.gaussian_filter_size = filter_size
            preprocessing_instance.mean_filter = False
            preprocessing_instance.median_filter = False

        filtered_image = PILImage.fromarray(filtered_image)

        # Save the processed image
        processed_image_stream = io.BytesIO()
        filtered_image.save(processed_image_stream, format="JPEG")
        processed_image_stream.seek(0)

        preprocessing_instance.image_preprocessing.save(
            uuid.uuid4().hex + ".jpg",
            ContentFile(processed_image_stream.read()),
            save=False,
        )

        # created_at and updated_at
        preprocessing_instance.created_at = datetime.now()
        preprocessing_instance.updated_at = datetime.now()

        # ground truth image
        # Create a blank ground truth image
        filtered_image_to_array = np.array(filtered_image)
        ground_truth = np.zeros_like(filtered_image)

        # set black areas as foreground (255) and white areas as background (0) with the threshold adaptative
        thresholded_image = cv2.adaptiveThreshold(
            filtered_image_to_array,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2,
        )

        ground_truth[thresholded_image > ground_truth] = 255

        # set black area is the background, inverse of the image and background is the biggest area
        ground_truth = cv2.bitwise_not(ground_truth)

        # Remove small black areas
        contours, _ = cv2.findContours(
            ground_truth.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        min_area_threshold = 100
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area_threshold:
                cv2.drawContours(
                    ground_truth, [contour], -1, (0, 0, 0), thickness=cv2.FILLED
                )

        # Menggunakan thresholding untuk mendapatkan gambar biner
        _, binary = cv2.threshold(ground_truth, 0, 255, cv2.THRESH_BINARY)

        # Mendeteksi kontur pada gambar biner
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Menggabungkan kontur terdekat dengan jarak tertentu
        min_distance_threshold = 10
        merged_contours = []
        for contour in contours:
            if cv2.contourArea(contour) < min_area_threshold:
                continue
            merged_contours.append(
                cv2.approxPolyDP(contour, min_distance_threshold, True)
            )

        # Membuat gambar kosong sebagai latar belakang
        ground_truth = np.zeros_like(ground_truth)

        # Menggambar kontur yang digabungkan pada gambar output
        cv2.drawContours(ground_truth, merged_contours, -1, 255, thickness=cv2.FILLED)

        # set black area is the background, inverse of the image and background is the biggest area
        ground_truth = cv2.bitwise_not(ground_truth)

        # Save the processed image
        ground_truth = PILImage.fromarray(ground_truth)
        ground_truth_image_stream = io.BytesIO()
        ground_truth.save(ground_truth_image_stream, format="JPEG")
        ground_truth_image_stream.seek(0)

        preprocessing_instance.image_ground_truth.save(
            uuid.uuid4().hex + ".jpg",
            ContentFile(ground_truth_image_stream.read()),
            save=False,
        )

        preprocessing_instance.save()


class ImageUploadView(CreateView):
    form_class = ImageForm
    template_name = "myapp/image/image_upload.html"
    failure_url = "/image/upload/"
    # success_url = reverse_lazy('image_list')  # Assuming you have a URL name for the image list view

    # invalid form
    def form_invalid(self, form):
        print(form.cleaned_data)
        return super().form_invalid(form)

    def form_valid(self, form):
        image_data = form.cleaned_data["image"].read()
        image_array = np.frombuffer(image_data, np.uint8)
        image_channel = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[2]
        image_dpi = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[0]
        form.instance.dpi = image_dpi
        form.instance.channel = image_channel
        image_obj = form.save()

        parameters = [
            {
                "scale": scale,
                "brightness": brightness,
                "contrast": contrast,
                "spatial_filter": spatial_filter,
            }
            for scale in [0.5, 0.75, 1.0, 1.25, 1.5]
            for brightness in [0.5, 0.75, 1.0, 1.25, 1.5]
            for contrast in [0.5, 0.75, 1.0, 1.25, 1.5]
            for spatial_filter in [
                ("mean_filter", 3),
                ("mean_filter", 5),
                ("mean_filter", 7),
                ("median_filter", 3),
                ("median_filter", 5),
                ("median_filter", 7),
                ("gaussian_filter", 3),
                ("gaussian_filter", 5),
                ("gaussian_filter", 7),
            ]
        ]

        process_and_save_image_preprocessing(image_obj, image_array, parameters)

        return redirect("myapp:image_list")

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
