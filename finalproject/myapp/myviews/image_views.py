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
from django.db.models import Count, Q


# forms import
from myapp.forms import ImageForm

from django.urls import reverse_lazy

# cv2 import
import cv2

# numpy import
import numpy as np

from myapp.utils.image import (
    apply_spatial_filter,
    process_and_save_image_preprocessing,
    get_user_image_count,
)


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

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        queryset = super().get_queryset()

        if search_query:
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi yang diinginkan.
            queryset = queryset.filter(
                Q(image__icontains=search_query)
                | Q(uploader__username__icontains=search_query)
                | Q(color__icontains=search_query)
                | Q(width__icontains=search_query)
                | Q(height__icontains=search_query)
                | Q(distance__icontains=search_query)
                | Q(format__icontains=search_query)
                | Q(size__icontains=search_query)
                | Q(channel__icontains=search_query)
            )

        return queryset


class ImageUploaderView(ListView):
    model = Image
    template_name = "myapp/image/image_by_uploader.html"
    context_object_name = "images"
    ordering = ["-created_at"]
    paginate_by = 10

    # get queryset
    def get_queryset(self):
        uploader = self.kwargs["uploader"]
        search_query = self.request.GET.get("search")
        queryset = super().get_queryset()

        if search_query:
            queryset = Image.objects.filter(
                Q(uploader__username=uploader)
                & (
                    Q(image__icontains=search_query)
                    | Q(uploader__username__icontains=search_query)
                    | Q(color__icontains=search_query)
                    | Q(width__icontains=search_query)
                    | Q(height__icontains=search_query)
                    | Q(distance__icontains=search_query)
                    | Q(format__icontains=search_query)
                    | Q(size__icontains=search_query)
                    | Q(channel__icontains=search_query)
                )
            )
        return queryset

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
