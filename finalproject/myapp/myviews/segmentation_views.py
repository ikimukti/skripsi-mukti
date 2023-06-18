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
    paginate_by = 8

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


def get_segmentation_results_data(image):
    segmentation_types = ["kmeans", "adaptive", "otsu", "sobel", "prewitt", "canny"]

    segmentation_results = Segmentation.objects.filter(
        image_preprocessing__image=image, segmentation_type__in=segmentation_types
    )

    segmentation_count = {
        segmentation_type: 0 for segmentation_type in segmentation_types
    }

    for segmentation_result in segmentation_results:
        segmentation_type = segmentation_result.segmentation_type
        if segmentation_type in segmentation_count:
            segmentation_count[segmentation_type] += 1

    segmentation_results_data = {
        segmentation_type: {
            "available": segmentation_count[segmentation_type] > 0,
            "count": segmentation_count[segmentation_type],
        }
        for segmentation_type in segmentation_types
    }

    return segmentation_results_data


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


def perform_prewitt_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessings = ImagePreprocessing.objects.filter(image=image)

    # Count Preprocessing objects
    preprocessing_count = preprocessings.count()
    print("preprocessing_count:", preprocessing_count)

    # Iterate over each preprocessing object
    counter = 0
    for preprocessing in preprocessings:
        # Perform prewitt segmentation on the image
        img = preprocessing.image_preprocessing_gray
        img_file = cv2.imread(img.path)

        # Convert the image to grayscale
        img_file = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
        print("img_file shape:", img_file.shape)

        # Apply Prewitt operator
        # Filter Prewitt horizontal dan vertikal
        prewitt_x = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)
        prewitt_y = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)

        # Konvolusi dengan filter Prewitt
        prewitt_x_result = cv2.filter2D(img_file, -1, prewitt_x)
        prewitt_y_result = cv2.filter2D(img_file, -1, prewitt_y)

        # Menggabungkan hasil Prewitt x dan y
        prewitt_combined = cv2.addWeighted(
            cv2.convertScaleAbs(prewitt_x_result),
            0.5,
            cv2.convertScaleAbs(prewitt_y_result),
            0.5,
            0,
        )

        # Melakukan segmentasi menggunakan thresholding
        _, segmented = cv2.threshold(
            prewitt_combined, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Get image file path
        ground_truth_path = preprocessing.image_ground_truth.path

        # Muat gambar sebagai array numerik
        ground_truth = cv2.imread(ground_truth_path)
        ground_truth_array = np.array(ground_truth)
        segmented_array = np.zeros((segmented.shape[0], segmented.shape[1], 3))
        segmented_array = np.array(segmented_array)

        print("ground_truth:", ground_truth_array.shape)
        print("segmented_array:", segmented_array.shape)
        # Flatten array of images
        ground_truth_array = ground_truth_array.flatten()
        segmented_array = segmented_array.flatten()

        print("ground_truth_array:", ground_truth_array.shape)
        print("segmented_array:", segmented_array.shape)

        # Call the calculate_scores function
        type = "prewitt"
        average = "binary"
        zero_division = 1
        scores = calculate_scores(
            ground_truth_array, segmented_array, type, average, zero_division
        )

        # save to model Segmentation()
        # Create a new Segmentation object
        segmentation_instance = Segmentation()
        segmentation_instance.image_preprocessing = preprocessing
        segmentation_instance.segmentation_type = "prewitt"

        segmented_image = PILImage.fromarray(segmented)
        segmented_stream = io.BytesIO()
        segmented_image.save(segmented_stream, format="JPEG")
        segmented_stream.seek(0)

        # Set the segmented image
        segmentation_instance.image_segmented.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(segmented_stream.getvalue()),
            save=False,
        )
        # Set the scores
        segmentation_instance.f1_score = scores["f1_score"]
        segmentation_instance.accuracy = scores["accuracy"]
        segmentation_instance.precision = scores["precision"]
        segmentation_instance.recall = scores["recall"]
        segmentation_instance.rand_score = scores["rand_score"]
        segmentation_instance.jaccard_score = scores["jaccard_score"]
        segmentation_instance.mse = scores["mse"]
        segmentation_instance.psnr = scores["psnr"]
        segmentation_instance.mae = scores["mae"]
        segmentation_instance.rmse = scores["rmse"]

        # Save the Segmentation object
        segmentation_instance.save()

        # Save the result to /static/images/dump/
        # image_path = os.path.join("static", "images", "dump", f"prewitt_{counter}.jpg")
        # cv2.imwrite(image_path, segmented)

        counter += 1


def perform_canny_segmentation(image):
    preprocessings = ImagePreprocessing.objects.filter(image=image)
    preprocessing_count = preprocessings.count()
    print("preprocessing_count:", preprocessing_count)
    counter = 0
    for preprocessing in preprocessings:
        img = preprocessing.image_preprocessing_gray
        img_file = cv2.imread(img.path)

        # Apply Otsu's thresholding to get optimal threshold values
        img_gray = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
        threshold_value, _ = cv2.threshold(
            img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Calculate low and high threshold values
        low_threshold = 0.5 * threshold_value
        high_threshold = 1.5 * threshold_value

        # Apply Canny edge detection
        canny_edges = cv2.Canny(
            img_gray, low_threshold, high_threshold, L2gradient=True
        )

        # Perform dilation on the edges
        kernel_size = (int(img_file.shape[0] / 100), int(img_file.shape[1] / 100))
        kernel = np.ones(kernel_size, np.uint8)
        dilated_edges = cv2.dilate(canny_edges, kernel, iterations=1)

        segmented = cv2.bitwise_not(dilated_edges)

        ground_truth_path = preprocessing.image_ground_truth.path

        # Muat gambar sebagai array numerik
        ground_truth = cv2.imread(ground_truth_path)
        ground_truth_array = np.array(ground_truth)
        segmented_array = np.zeros((segmented.shape[0], segmented.shape[1], 3))
        segmented_array = np.array(segmented_array)

        print("ground_truth:", ground_truth_array.shape)
        print("segmented:", segmented_array.shape)
        # Flatten array of images
        ground_truth_array = ground_truth_array.flatten()
        segmented_array = segmented_array.flatten()

        print("ground_truth_array:", ground_truth_array.shape)
        print("segmented_array:", segmented_array.shape)

        # Call the calculate_scores function
        type = "canny"
        average = "binary"
        zero_division = 1
        scores = calculate_scores(
            ground_truth_array, segmented_array, type, average, zero_division
        )

        # save to model Segmentation()
        # Create a new Segmentation object
        segmentation_instance = Segmentation()
        segmentation_instance.image_preprocessing = preprocessing
        segmentation_instance.segmentation_type = "canny"

        segmented_image = PILImage.fromarray(segmented)
        segmented_stream = io.BytesIO()
        segmented_image.save(segmented_stream, format="JPEG")
        segmented_stream.seek(0)

        # Set the segmented image
        segmentation_instance.image_segmented.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(segmented_stream.getvalue()),
            save=False,
        )
        # Set the scores
        segmentation_instance.f1_score = scores["f1_score"]
        segmentation_instance.accuracy = scores["accuracy"]
        segmentation_instance.precision = scores["precision"]
        segmentation_instance.recall = scores["recall"]
        segmentation_instance.rand_score = scores["rand_score"]
        segmentation_instance.jaccard_score = scores["jaccard_score"]
        segmentation_instance.mse = scores["mse"]
        segmentation_instance.psnr = scores["psnr"]
        segmentation_instance.mae = scores["mae"]
        segmentation_instance.rmse = scores["rmse"]

        # Save the Segmentation object
        segmentation_instance.save()

        # Save the result to /static/images/dump/
        # image_path = os.path.join("static", "images", "dump", f"canny_{counter}.jpg")
        # cv2.imwrite(image_path, segmented)

        counter += 1


class SegmentationSummaryClassView(View):
    context = {}
    template_name = "myapp/segmentation/segmentation_summary.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            self.extra_context = {
                "title": "Segmentation Summary",
                "contributor": "WeeAI Team",
                "content": "Welcome to WeeAI! This is a website for image segmentation.",
                "app_css": "myapp/css/styles.css",
                "app_js": "myapp/js/scripts.js",
                "logo": "myapp/images/Logo.png",
            }
            context = self.context
            context.update(self.extra_context)
            return render(request, self.template_name, context)
