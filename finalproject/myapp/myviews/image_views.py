import json
import random
from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)

from django.core.paginator import Paginator

# models import
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
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


def apply_spatial_filter(image, filter_type, filter_size):
    image_array = np.array(image)

    if filter_type == "mean_filter":
        filtered_image = filters.uniform_filter(
            image_array, size=filter_size, mode="constant"
        )
    elif filter_type == "median_filter":
        filtered_image = filters.median_filter(
            image_array, size=filter_size, mode="constant"
        )
    elif filter_type == "gaussian_filter":
        sigma = filter_size / 6
        filtered_image = filters.gaussian_filter(
            image_array, sigma=sigma, mode="constant"
        )
    else:
        raise ValueError("Invalid filter type")

    filtered_image = PILImage.fromarray(filtered_image)
    return filtered_image


def process_and_save_image_preprocessing(image_obj, image_array, parameters):
    original_image = PILImage.fromarray(cv2.imdecode(image_array, cv2.COLOR_BGR2RGB))
    counter = 0
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
        # print shape

        preprocessing_instance.resize = True
        preprocessing_instance.resize_width = resized_image.width
        preprocessing_instance.resize_height = resized_image.height
        preprocessing_instance.resize_percent = scale * 100

        # Adjust brightness
        enhanced_image = PILImageEnhance.Brightness(resized_image).enhance(brightness)
        print("enhanced_image.shape brightness", enhanced_image.size, counter)

        preprocessing_instance.brightness = True
        preprocessing_instance.brightness_percent = brightness * 100

        # Adjust contrast
        enhanced_image = PILImageEnhance.Contrast(enhanced_image).enhance(contrast)
        print("enhanced_image.shape contrast", enhanced_image.size, counter)

        preprocessing_instance.contrast = True
        preprocessing_instance.contrast_percent = contrast * 100

        # Convert to grayscale
        enhanced_image_gray = np.array(enhanced_image.convert("L"))
        enhanced_image_color = np.array(enhanced_image)

        # Apply spatial filter
        filtered_image_gray = None
        filtered_image_color = None
        filter_type, filter_size = spatial_filter

        if filter_type == "mean_filter":
            filtered_image_gray = filters.uniform_filter(
                enhanced_image_gray, size=filter_size, mode="constant"
            )
            filtered_image_color = filters.uniform_filter(
                enhanced_image_color, size=filter_size, mode="constant"
            )
            print(
                "filtered_image_gray.shape mean_filter",
                filtered_image_gray.shape,
                counter,
            )
            print(
                "filtered_image_color.shape mean_filter",
                filtered_image_color.shape,
                counter,
            )
            preprocessing_instance.mean_filter = True
            preprocessing_instance.mean_filter_size = filter_size
            preprocessing_instance.median_filter = False
            preprocessing_instance.gaussian_filter = False

        elif filter_type == "median_filter":
            filtered_image_gray = filters.median_filter(
                enhanced_image_gray, size=filter_size, mode="constant"
            )
            filtered_image_color = filters.median_filter(
                enhanced_image_color, size=filter_size, mode="constant"
            )
            print(
                "filtered_image_gray.shape median_filter",
                filtered_image_gray.shape,
                counter,
            )
            print(
                "filtered_image_color.shape median_filter",
                filtered_image_color.shape,
                counter,
            )
            preprocessing_instance.median_filter = True
            preprocessing_instance.median_filter_size = filter_size
            preprocessing_instance.mean_filter = False
            preprocessing_instance.gaussian_filter = False

        elif filter_type == "gaussian_filter":
            sigma = filter_size / 6
            filtered_image_gray = filters.gaussian_filter(
                enhanced_image_gray, sigma=sigma, mode="constant"
            )
            filtered_image_color = filters.gaussian_filter(
                enhanced_image_color, sigma=sigma, mode="constant"
            )
            print(
                "filtered_image_gray.shape gaussian_filter",
                filtered_image_gray.shape,
                counter,
            )
            print(
                "filtered_image_color.shape gaussian_filter",
                filtered_image_color.shape,
                counter,
            )
            preprocessing_instance.gaussian_filter = True
            preprocessing_instance.gaussian_filter_size = filter_size
            preprocessing_instance.mean_filter = False
            preprocessing_instance.median_filter = False

        filtered_image_gray = PILImage.fromarray(filtered_image_gray)
        filtered_image_color = PILImage.fromarray(filtered_image_color)

        # if filtered_image_color is to bright or to dark, skip it and use the resized image
        if filtered_image_color.getextrema()[0] == filtered_image_color.getextrema()[1]:
            filtered_image_color = resized_image

        print("filtered_image_gray.shape", filtered_image_gray.size, counter)
        print("filtered_image_color.shape", filtered_image_color.size, counter)

        # Save the processed image
        processed_image_gray_stream = io.BytesIO()
        filtered_image_gray.save(processed_image_gray_stream, format="JPEG")
        processed_image_gray_stream.seek(0)

        processed_image_color_stream = io.BytesIO()
        filtered_image_color.save(processed_image_color_stream, format="JPEG")
        processed_image_color_stream.seek(0)

        preprocessing_instance.image_preprocessing_color.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(processed_image_color_stream.getvalue()),
            save=False,
        )

        preprocessing_instance.image_preprocessing_gray.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(processed_image_gray_stream.getvalue()),
            save=False,
        )

        # created_at and updated_at
        preprocessing_instance.created_at = datetime.now()
        preprocessing_instance.updated_at = datetime.now()

        # ground truth image
        # Create a blank ground truth image
        filtered_image_to_array = np.array(filtered_image_gray)
        ground_truth = np.zeros_like(filtered_image_to_array)

        # set black areas as foreground (255) and white areas as background (0) with the threshold adaptative
        _, thresholded_image = cv2.threshold(
            filtered_image_to_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        ground_truth[thresholded_image > ground_truth] = 255

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

        # set black area is the background, inverse of the image and background is the biggest area
        if np.sum(ground_truth) < np.sum(255 - ground_truth):
            ground_truth = 255 - ground_truth

        # Save the processed image
        ground_truth = PILImage.fromarray(ground_truth)
        print("ground_truth.shape", ground_truth.size, counter)
        ground_truth_image_stream = io.BytesIO()
        ground_truth.save(ground_truth_image_stream, format="JPEG")
        ground_truth_image_stream.seek(0)

        preprocessing_instance.image_ground_truth.save(
            uuid.uuid4().hex + ".jpg",
            ContentFile(ground_truth_image_stream.read()),
            save=False,
        )

        counter += 1
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
                ("median_filter", 3),
                ("gaussian_filter", 3),
            ]
        ]

        total_combinations = len(parameters)
        target_count = 50
        step = total_combinations // target_count

        selected_parameters = []

        for i in range(0, total_combinations, step):
            selected_parameters.append(parameters[i])

        random.shuffle(selected_parameters)

        print("selected_parameters", selected_parameters)

        process_and_save_image_preprocessing(
            image_obj, image_array, selected_parameters
        )
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
    paginate_by = 10

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


def get_user_image_count():
    user_image_count = []
    users = User.objects.all()
    for user in users:
        image_count = Image.objects.filter(uploader=user).count()
        user_image_count.append((user.username, image_count))
    return user_image_count


class ImageListView(ListView):
    model = Image
    template_name = "myapp/image/image_list.html"
    context_object_name = "images"
    ordering = ["-created_at"]
    paginate_by = 10

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

        # Prepare uploaders data as a list of dictionaries
        uploaders = []
        user_image_count = get_user_image_count()
        for name, count in user_image_count:
            if count > 0:
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
    paginate_by = 10

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
    paginate_by = 10  # Menampilkan 10 gambar per halaman

    def get_segmentation_data(self, segmentation_type):
        image_preprocessing = ImagePreprocessing.objects.filter(image=self.object)
        if segmentation_type == "all":
            segmentation = Segmentation.objects.filter(
                image_preprocessing__in=image_preprocessing,
            )
        else:
            segmentation = Segmentation.objects.filter(
                image_preprocessing__in=image_preprocessing,
                segmentation_type=segmentation_type,
            )

        segmentation = segmentation.order_by(
            "-f1_score",
            "-rand_score",
            "-jaccard_score",
            "-mse",
            "-psnr",
            "-mae",
            "-rmse",
        )
        # Urutkan dari terendah ke tertinggi
        segmentation = sorted(
            segmentation,
            key=lambda x: (
                x.f1_score,
                x.rand_score,
                x.jaccard_score,
                x.mse,
                x.psnr,
                x.mae,
                x.rmse,
            ),
        )

        labels = [seg.segmentation_type for seg in segmentation]
        f1_score = [seg.f1_score for seg in segmentation]
        rand_score = [seg.rand_score for seg in segmentation]
        jaccard_score = [seg.jaccard_score for seg in segmentation]
        mse = [seg.mse for seg in segmentation]
        psnr = [seg.psnr for seg in segmentation]
        mae = [seg.mae for seg in segmentation]
        rmse = [seg.rmse for seg in segmentation]

        # get 1st segmentation data as best
        data_length = len(labels)
        best = segmentation[data_length - 1]

        return {
            "labels": json.dumps(list(labels)),
            "data_f1_score": json.dumps(list(f1_score)),
            "data_rand_score": json.dumps(list(rand_score)),
            "data_jaccard_score": json.dumps(list(jaccard_score)),
            "data_mse": json.dumps(list(mse)),
            "data_psnr": json.dumps(list(psnr)),
            "data_mae": json.dumps(list(mae)),
            "data_rmse": json.dumps(list(rmse)),
            "best": best,
        }

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

        # Get all images by image id
        image_list = ImagePreprocessing.objects.filter(image=self.object)
        # get segmentation by imagepreprocessing id and add related imagepreprocessing to image_list
        seg_type = self.request.GET.get("segmentation")
        print(seg_type)
        if seg_type is None or seg_type == "all":
            segmentation = (
                Segmentation.objects.filter(image_preprocessing__in=image_list)
                .prefetch_related("image_preprocessing")
                .order_by("-created_at")
            )
        else:
            segmentation = (
                Segmentation.objects.filter(
                    image_preprocessing__in=image_list,
                    segmentation_type=seg_type,
                )
                .prefetch_related("image_preprocessing")
                .order_by("-created_at")
            )

        # Create paginator object
        paginator = Paginator(segmentation, self.paginate_by)

        # Get the current page number from the request's GET parameters
        page_number = self.request.GET.get("page")

        # Get the page object for the current page number
        page_obj = paginator.get_page(page_number)

        # Add the paginated images to the context and add image_list and paginator
        # to the context as well
        context["image_list"] = page_obj.object_list
        context["page_obj"] = page_obj
        # if page_obj is_paginated
        context["is_paginated"] = page_obj.has_other_pages()

        chartjs_data = {}

        if seg_type is None or seg_type == "all":
            chartjs_data = self.get_segmentation_data("all")
            # get 1st segmentation chartjs data
        else:
            chartjs_data = self.get_segmentation_data(seg_type)

        context["chartjs"] = chartjs_data

        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)
