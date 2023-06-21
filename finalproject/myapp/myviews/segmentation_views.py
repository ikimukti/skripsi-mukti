from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from myapp.utils.segmentation import (
    perform_k_means_segmentation,
    get_top_segmentations,
    calculate_scores,
    perform_adaptive_segmentation,
    perform_otsu_segmentation,
    perform_sobel_segmentation,
    perform_canny_segmentation,
    perform_prewitt_segmentation,
    get_segmentation_results_data,
)
import io
from django.core.files.base import ContentFile
from myapp.menus import menus, set_user_menus
from myapp.models import (
    Image,
    ImagePreprocessing,
    Segmentation,
    SegmentationResult,
    UserProfile,
)
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
import uuid
from django.contrib.auth.models import User
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.db.models import Count, Q, F
import cv2
import numpy as np
from PIL import Image as PILImage
import os
from datetime import datetime


class SegmentationClassView(ListView):
    template_name = "myapp/segmentation/segmentation.html"
    model = Image
    context_object_name = "segmentation"
    ordering = ["-created_at"]
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            self.object_list = self.get_queryset()
            context = self.get_context_data(**kwargs)
            set_user_menus(request, context)
            self.customize_context(context)  # Call the customize_context method
            return render(request, self.template_name, context)

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("segmentation_results")

        # Get categories uploader name with name of uploader in User model
        uploaders_name = (
            User.objects.filter(image__isnull=False)
            .distinct()
            .values_list("username", flat=True)
        )
        # Count Image by uploader
        uploaders_count = Image.objects.filter(uploader__isnull=False)
        print(uploaders_count)
        # Prepare uploaders data as a list of dictionaries
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({"name": name, "count": count})
        print(uploaders)
        # Get categories color name
        colors = queryset.values_list("color", flat=True).distinct()

        self.extra_context = {
            "uploaders": uploaders,
            "colors": colors,
            "title": "Segmentation",
            "contributor": "WeeAI Team",
            "content": "Welcome to WeeAI! This is a website for image segmentation.",
            "app_css": "myapp/css/styles.css",
            "app_js": "myapp/js/scripts.js",
            "logo": "myapp/images/Logo.png",
        }

        # Iterate over the queryset and set the "segmented" column based on the segmentation types
        counter = 0
        for image in queryset:
            segmentation_types = [
                "kmeans",
                "adaptive",
                "otsu",
                "sobel",
                "prewitt",
                "canny",
            ]
            segmentation_count = image.segmentation_results.filter(
                segmentation_type__in=segmentation_types
            ).count()
            segmented = segmentation_count == 90
            image.segmented = segmented
            image.segmented_count = (
                segmentation_count  # Add the "segmented_count" variable
            )
            color = image.color
            # replace dash with space
            color = color.replace("-", " ")
            image.color = color
            counter += 1

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

    def customize_context(self, context):
        # Override this method in derived views to customize the context
        pass


def perform_segmentation(segmentation_type, segmentation_results_data, image):
    segmentations = {
        "kmeans": {
            "perform": perform_k_means_segmentation,
            "top": get_top_segmentations,
        },
        "adaptive": {
            "perform": perform_adaptive_segmentation,
            "top": get_top_segmentations,
        },
        "otsu": {
            "perform": perform_otsu_segmentation,
            "top": get_top_segmentations,
        },
        "sobel": {
            "perform": perform_sobel_segmentation,
            "top": get_top_segmentations,
        },
        "prewitt": {
            "perform": perform_prewitt_segmentation,
            "top": get_top_segmentations,
        },
        "canny": {
            "perform": perform_canny_segmentation,
            "top": get_top_segmentations,
        },
    }

    if (
        segmentation_type in segmentations
        and not segmentation_results_data[segmentation_type]["available"]
    ):
        print(f"Performing {segmentation_type} segmentation...")
        perform_func = segmentations[segmentation_type]["perform"]
        perform_func(image)
        top_func = segmentations[segmentation_type]["top"]
        if top_func:
            top_func(image, segmentation_type)


class SegmentationDetailClassView(DetailView):
    model = Image
    template_name = "myapp/segmentation/segmentation_detail.html"
    context_object_name = "segmentation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_menus(self.request, context)
        self.customize_context(context)

        context["title"] = "Segmentation Detail"
        context["contributor"] = "WeeAI Team"
        context[
            "content"
        ] = "Welcome to WeeAI! This is a website for image segmentation."
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"

        image = self.get_object()
        segmentation_results_data = get_segmentation_results_data(image)
        context["segmentation_results_data"] = segmentation_results_data
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        image = self.get_object()
        selected_segmentation_types = request.POST.getlist("segmentation_types")
        segmentation_results_data = get_segmentation_results_data(image)
        print("selected_segmentation_types:", selected_segmentation_types)

        for segmentation_type in selected_segmentation_types:
            if SegmentationResult.objects.filter(
                image=image, segmentation_type=segmentation_type
            ).exists():
                print(f"Segmentation {segmentation_type} already exists.")
                continue

            perform_segmentation(segmentation_type, segmentation_results_data, image)

        return redirect("myapp:segmentation_detail", pk=image.pk)

    def customize_context(self, context):
        pass


class SegmentationSummaryClassView(ListView):
    template_name = "myapp/segmentation/segmentation_summary.html"
    model = Image
    context_object_name = "segmentation"
    ordering = ["-created_at"]
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            self.object_list = self.get_queryset()
            context = self.get_context_data(**kwargs)
            set_user_menus(request, context)
            self.customize_context(context)  # Call the customize_context method
            return render(request, self.template_name, context)

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("segmentation_results")

        # Get categories uploader name with name of uploader in User model
        uploaders_name = (
            User.objects.filter(image__isnull=False)
            .distinct()
            .values_list("username", flat=True)
        )
        # Count Image by uploader
        uploaders_count = Image.objects.filter(uploader__isnull=False)
        print(uploaders_count)
        # Prepare uploaders data as a list of dictionaries
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({"name": name, "count": count})
        print(uploaders)
        # Get categories color name
        colors = queryset.values_list("color", flat=True).distinct()

        # Chart data for User Uploaders
        image_preprocessing = ImagePreprocessing.objects.filter(
            image__in=queryset,
        )
        segmentation = (
            Segmentation.objects.filter(
                image_preprocessing__in=image_preprocessing,
            )
            .prefetch_related("image_preprocessing")
            .prefetch_related("image_preprocessing__image")
        )
        # Get data user uploaders
        uploaders_name = segmentation.values_list(
            "image_preprocessing__image__uploader__username",
            flat=True,
        ).distinct()
        # Count data user uploaders
        uploaders_count = segmentation.values_list(
            "image_preprocessing__image__uploader__username",
        ).annotate(count=Count("image_preprocessing__image__uploader__username"))
        print(uploaders_count)

        chartjs_data = {
            "labels_user": uploaders_name,
            "data_user": uploaders_count,
        }

        self.extra_context = {
            "uploaders": uploaders,
            "colors": colors,
            "title": "Segmentation Summary",
            "contributor": "WeeAI Team",
            "content": "Welcome to WeeAI! This is a website for image segmentation.",
            "app_css": "myapp/css/styles.css",
            "app_js": "myapp/js/scripts.js",
            "logo": "myapp/images/Logo.png",
            "chartjs": chartjs_data,
        }

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

    def customize_context(self, context):
        # Override this method in derived views to customize the context
        pass
