from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from sklearn.metrics import (
    adjusted_rand_score,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
    rand_score,
    jaccard_score,
    mean_squared_error,
    mean_absolute_error,
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

# model
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.db.models import Count, Q

# cv2 import
import cv2
import numpy as np
from PIL import Image as PILImage

# os
import os

# datetime
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
        uploaders_count = (
            Image.objects.values("uploader")
            .distinct()
            .annotate(count=Count("uploader"))
            .values_list("count", flat=True)
        )
        # Prepare uploaders data as a list of dictionaries
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({"name": name, "count": count})

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
            segmented = (
                image.segmentation_results.filter(
                    Q(
                        segmentation_type__in=[
                            "k-means",
                            "adaptive",
                            "otsu",
                            "sobel",
                            "prewitt",
                        ]
                    )
                    & Q(segmentation_type__isnull=False)
                ).count()
                == 5
            )
            image.segmented = segmented
            counter += 1
            print(f"Image {counter} segmented: {segmented}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

    def customize_context(self, context):
        # Override this method in derived views to customize the context
        pass


class SegmentationDetailClassView(DetailView):
    model = Image
    template_name = "myapp/segmentation/segmentation_detail.html"
    context_object_name = "segmentation"

    # Override the get_context_data method
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_menus(self.request, context)
        self.customize_context(context)  # Call the customize_context method

        context["title"] = "Segmentation Detail"
        context["contributor"] = "WeeAI Team"
        context[
            "content"
        ] = "Welcome to WeeAI! This is a website for image segmentation."
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"

        # Get the image object
        image = self.get_object()

        # Get segmentation results for the image with the specified segmentation types
        segmentation_types = [
            "k-means",
            "adaptive",
            "otsu",
            "sobel",
            "prewitt",
            "canny",
        ]
        segmentation_results = SegmentationResult.objects.filter(
            image=image, segmentation_type__in=segmentation_types
        )

        # Create a dictionary to hold the segmentation results
        segmentation_results_data = {}
        for segmentation_type in segmentation_types:
            segmentation_results_data[segmentation_type] = []

        # Iterate over the segmentation results and add them to the dictionary
        for segmentation_result in segmentation_results:
            segmentations = segmentation_results.filter(
                segmentation_type=segmentation_type
            )
            if segmentations:
                for segmentation_result in segmentations:
                    segmentation_results_data[segmentation_type].append(
                        segmentation_result
                    )
            else:
                segmentation_results_data[segmentation_type].append(None)

        # Add the segmentation results dictionary to the context
        context["segmentation_results_data"] = segmentation_results_data

        return context

    # Override the get method
    def get(self, request, *args, **kwargs):
        # condition to check if user is authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

    # Override the post method
    def post(self, request, *args, **kwargs):
        # Get the image object
        image = self.get_object()

        # Get the selected segmentation types from the POST data
        selected_segmentation_types = request.POST.getlist("segmentation_types")

        # Process the selected segmentation types
        for segmentation_type in selected_segmentation_types:
            # Check if segmentation data already exists
            if SegmentationResult.objects.filter(
                image=image, segmentation_type=segmentation_type
            ).exists():
                continue  # Skip processing if segmentation data already exists

            # Get the asso

            # Perform the desired action based on the segmentation type
            if segmentation_type == "k-means":
                # Perform k-means segmentation
                print("Performing k-means segmentation...")
                perform_k_means_segmentation(image)
            elif segmentation_type == "adaptive":
                # Perform adaptive segmentation
                perform_adaptive_segmentation(image)
            elif segmentation_type == "otsu":
                # Perform Otsu's thresholding segmentation
                perform_otsu_segmentation(image)
            elif segmentation_type == "sobel":
                # Perform Sobel edge detection segmentation
                perform_sobel_segmentation(image)
            elif segmentation_type == "prewitt":
                # Perform Prewitt edge detection segmentation
                perform_prewitt_segmentation(image)
            elif segmentation_type == "canny":
                # Perform Canny edge detection segmentation
                perform_canny_segmentation(image)

        # Redirect to the segmentation detail page
        return redirect("myapp:segmentation_detail", pk=image.pk)

    def customize_context(self, context):
        # Override this method in derived views to customize the context
        pass


def perform_k_means_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessings = ImagePreprocessing.objects.filter(image=image)

    # count Preprocessing objects
    preprocessing_count = preprocessings.count()
    print("preprocessing_count:", preprocessing_count)
    # Iterate over each preprocessing object
    counter = 0
    for preprocessing in preprocessings:
        # Perform k-means segmentation using the Image and ImagePreprocessing objects
        img = preprocessing.image_preprocessing_color
        img_file = cv2.imread(img.path)
        # conver image to RGB
        img_rgb = cv2.cvtColor(img_file, cv2.COLOR_BGR2RGB)
        img_2d = img_rgb.astype(np.float32)

        # Print the shape of img_2d to check its dimensions
        counter += 1
        print("img_2d shape:", img_2d.shape, "-->", counter)

        img_2d = img_2d.reshape(img_2d.shape[0] * img_2d.shape[1], img_2d.shape[2])

        # Verify the value of cluster is valid
        cluster = 3
        if cluster <= 0:
            raise ValueError("The number of clusters should be greater than zero.")

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(
            img_2d, cluster, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )

        center = np.uint8(center)

        segmented_data = center[label.flatten()]
        segmented_image = segmented_data.reshape(img_rgb.shape)

        # Dapatkan jalur file gambar
        ground_truth_path = preprocessing.image_ground_truth.path

        # Muat gambar sebagai array numerik
        ground_truth_array = cv2.imread(ground_truth_path)
        ground_truth_array = np.array(ground_truth_array)
        segmented_array = np.array(segmented_image)

        # Flatten array gambar
        ground_truth_flatten = ground_truth_array.flatten()
        segmented_flatten = segmented_array.flatten()

        type = "k-means"
        average = "weighted"
        zero_division = 1
        # Call the calculate_scores function
        scores = calculate_scores(
            ground_truth_flatten,
            segmented_flatten,
            type,
            average=average,
            zero_division=zero_division,
        )
        # save to model Segmentation()
        # Create a new Segmentation object
        segmentation_instance = Segmentation()
        segmentation_instance.image_preprocessing = preprocessing
        segmentation_instance.segmentation_type = "k-means"
        segmented_image = PILImage.fromarray(segmented_image)
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


def perform_adaptive_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessings = ImagePreprocessing.objects.filter(image=image)

    # count Preprocessing objects
    preprocessing_count = preprocessings.count()
    print("preprocessing_count:", preprocessing_count)
    # Iterate over each preprocessing object
    counter = 0
    pass


def perform_otsu_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessing = ImagePreprocessing.objects.get(image=image)

    # Perform Otsu's thresholding segmentation using the Image and ImagePreprocessing objects
    # You can access the Image and ImagePreprocessing data within this function

    pass


def perform_sobel_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessing = ImagePreprocessing.objects.get(image=image)

    # Perform Sobel edge detection segmentation using the Image and ImagePreprocessing objects
    # You can access the Image and ImagePreprocessing data within this function

    pass


def perform_prewitt_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessing = ImagePreprocessing.objects.get(image=image)

    # Perform Prewitt edge detection segmentation using the Image and ImagePreprocessing objects
    # You can access the Image and ImagePreprocessing data within this function

    pass


def perform_canny_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessing = ImagePreprocessing.objects.get(image=image)

    # Perform Canny edge detection segmentation using the Image and ImagePreprocessing objects
    # You can access the Image and ImagePreprocessing data within this function

    pass


def calculate_scores(ground_truth, segmented, type, average="binary", zero_division=1):
    scores = {}
    scores["type"] = type
    average = "weighted" if type == "kmeans" else average

    # convert the image segmented and ground truth to binary format (0 or 1)
    segmented = np.where(segmented == 0, 0, 1)
    ground_truth = np.where(ground_truth == 0, 0, 1)

    scores["f1_score"] = str(
        round(
            f1_score(
                ground_truth,
                segmented,
                average=average,
                zero_division=zero_division,
            ),
            4,
        )
    )
    if scores["f1_score"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["f1_score"] = str(
            round(
                f1_score(
                    ground_truth,
                    reverse_segmented,
                    average=average,
                    zero_division=zero_division,
                ),
                4,
            )
        )

    scores["precision"] = str(
        round(
            precision_score(
                ground_truth,
                segmented,
                average=average,
                zero_division=zero_division,
            ),
            4,
        )
    )
    if scores["precision"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["precision"] = str(
            round(
                precision_score(
                    ground_truth,
                    reverse_segmented,
                    average=average,
                    zero_division=zero_division,
                ),
                4,
            )
        )

    scores["recall"] = str(
        round(
            recall_score(
                ground_truth,
                segmented,
                average=average,
                zero_division=zero_division,
            ),
            4,
        )
    )
    if scores["recall"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["recall"] = str(
            round(
                recall_score(
                    ground_truth,
                    reverse_segmented,
                    average=average,
                    zero_division=zero_division,
                ),
                4,
            )
        )

    scores["accuracy"] = str(round(accuracy_score(ground_truth, segmented), 4))
    if scores["accuracy"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["accuracy"] = str(
            round(accuracy_score(ground_truth, reverse_segmented), 4)
        )

    scores["rand_score"] = str(round(rand_score(ground_truth, segmented), 4))
    if scores["rand_score"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["rand_score"] = str(
            round(rand_score(ground_truth, reverse_segmented), 4)
        )

    scores["jaccard_score"] = str(
        round(
            jaccard_score(
                ground_truth,
                segmented,
                average=average,
                zero_division=zero_division,
            ),
            4,
        )
    )
    if scores["jaccard_score"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["jaccard_score"] = str(
            round(
                jaccard_score(
                    ground_truth,
                    reverse_segmented,
                    average=average,
                    zero_division=zero_division,
                ),
                4,
            )
        )

    mse = np.mean((ground_truth - segmented) ** 2)
    scores["mse"] = str(round(mse, 4))
    scores["mae"] = str(round(mean_absolute_error(ground_truth, segmented), 4))
    scores["rmse"] = str(
        round(
            mean_squared_error(ground_truth, segmented, squared=False),
            4,
        )
    )
    scores["psnr"] = (
        "inf"
        if mse == 0
        else str(
            round(
                10 * np.log10((255**2) / np.mean((ground_truth - segmented) ** 4)), 4
            )
        )
    )

    return scores


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
