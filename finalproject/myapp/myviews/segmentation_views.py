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
from django.db.models import Count, Q, F

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
                            "kmeans",
                            "adaptive",
                            "otsu",
                            "sobel",
                            "prewitt",
                            "canny",
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


def get_segmentation_results_data(image):
    segmentation_types = ["kmeans", "adaptive", "otsu", "sobel", "prewitt", "canny"]

    segmentation_results = SegmentationResult.objects.filter(
        image=image, segmentation_type__in=segmentation_types
    )

    segmentation_results_data = {
        segmentation_type: False for segmentation_type in segmentation_types
    }

    for segmentation_result in segmentation_results:
        segmentation_type = segmentation_result.segmentation_type
        segmentation_results_data[segmentation_type] = True

    return segmentation_results_data


def perform_segmentation(segmentation_type, segmentation_results_data, image):
    segmentations = {
        "kmeans": {
            "perform": perform_k_means_segmentation,
            "top": get_top_segmentations,
        },
        "adaptive": {"perform": perform_adaptive_segmentation, "top": None},
        "otsu": {"perform": perform_otsu_segmentation, "top": None},
        "sobel": {"perform": perform_sobel_segmentation, "top": None},
        "prewitt": {"perform": perform_prewitt_segmentation, "top": None},
        "canny": {"perform": perform_canny_segmentation, "top": None},
    }

    if (
        segmentation_type in segmentations
        and not segmentation_results_data[segmentation_type]
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

        for segmentation_type in selected_segmentation_types:
            if SegmentationResult.objects.filter(
                image=image, segmentation_type=segmentation_type
            ).exists():
                continue

            perform_segmentation(segmentation_type, segmentation_results_data, image)

        return redirect("myapp:segmentation_detail", pk=image.pk)

    def customize_context(self, context):
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
        # Perform kmeans segmentation using the Image and ImagePreprocessing objects
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

        type = "kmeans"
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
        segmentation_instance.segmentation_type = "kmeans"
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


def get_top_segmentations(Image, segmentation_type):
    top_segmentations = (
        Segmentation.objects.select_related("image_preprocessing__image")
        .filter(image_preprocessing__image=Image)
        .order_by(
            F("image_preprocessing__resize").asc(),
            F("image_preprocessing__resize_percent").asc(),
            F("image_preprocessing__resize_width").asc(),
            F("image_preprocessing__resize_height").asc(),
            F("f1_score").desc(),
            F("accuracy").desc(),
            F("precision").desc(),
            F("recall").desc(),
            F("rand_score").desc(),
            F("jaccard_score").desc(),
            F("mse").desc(),
            F("psnr").desc(),
            F("mae").desc(),
            F("rmse").desc(),
        )[:15]
    )

    segmentation_instances = []
    rank = 1  # Start with rank 1

    for segmentation in top_segmentations:
        segmentation_instance = SegmentationResult.objects.create(
            image=Image,
            segmentation_type=segmentation_type,
            rank=rank,
        )

        segmentation_instance.segmentations.add(segmentation)
        segmentation_instances.append(segmentation_instance)
        rank += 1

    return segmentation_instances


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
    preprocessing = ImagePreprocessing.objects.filter(image=image)

    # count Preprocessing objects
    preprocessing_count = preprocessing.count()
    print("preprocessing_count:", preprocessing_count)
    # Iterate over each preprocessing object
    counter = 0

    pass


def perform_sobel_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessing = ImagePreprocessing.objects.filter(image=image)

    # count Preprocessing objects
    preprocessing_count = preprocessing.count()
    print("preprocessing_count:", preprocessing_count)
    # Iterate over each preprocessing object
    counter = 0

    pass


def perform_prewitt_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessing = ImagePreprocessing.objects.filter(image=image)

    # count Preprocessing objects
    preprocessing_count = preprocessing.count()
    print("preprocessing_count:", preprocessing_count)
    # Iterate over each preprocessing object
    counter = 0

    pass


def perform_canny_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessing = ImagePreprocessing.objects.filter(image=image)

    # count Preprocessing objects
    preprocessing_count = preprocessing.count()
    print("preprocessing_count:", preprocessing_count)
    # Iterate over each preprocessing object
    counter = 0

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
    print(scores)
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
