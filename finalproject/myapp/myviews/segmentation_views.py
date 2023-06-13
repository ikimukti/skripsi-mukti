from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
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
from django.contrib.auth.models import User
# model
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.db.models import Count, Q
from sklearn.cluster import KMeans
from skimage import color


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
            segmented = image.segmentation_results.filter(
                Q(segmentation_type__in=["k-means", "adaptive", "otsu", "sobel", "prewitt"])
                & Q(segmentation_type__isnull=False)
            ).count() == 5
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
        segmentation_types = ["k-means", "adaptive", "otsu", "sobel", "prewitt", "canny"]
        segmentation_results = SegmentationResult.objects.filter(
            image=image, segmentation_type__in=segmentation_types
        )

        # Create a dictionary to hold the segmentation results
        segmentation_results_data = {}
        for segmentation_type in segmentation_types:
            segmentation_results_data[segmentation_type] = []

        # Iterate over the segmentation results and add them to the dictionary
        for segmentation_result in segmentation_results:
            segmentations = segmentation_results.filter(segmentation_type=segmentation_type)
            if segmentations:
                for segmentation_result in segmentations:
                    segmentation_results_data[segmentation_type].append(segmentation_result)
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
        selected_segmentation_types = request.POST.getlist('segmentation_types')

        # Process the selected segmentation types
        for segmentation_type in selected_segmentation_types:
            # Check if segmentation data already exists
            if SegmentationResult.objects.filter(image=image, segmentation_type=segmentation_type).exists():
                continue  # Skip processing if segmentation data already exists

            # Get the asso

            # Perform the desired action based on the segmentation type
            if segmentation_type == 'k-means':
                # Perform k-means segmentation
                print("Performing k-means segmentation...")
                perform_k_means_segmentation(image)
            elif segmentation_type == 'adaptive':
                # Perform adaptive segmentation
                perform_adaptive_segmentation(image)
            elif segmentation_type == 'otsu':
                # Perform Otsu's thresholding segmentation
                perform_otsu_segmentation(image)
            elif segmentation_type == 'sobel':
                # Perform Sobel edge detection segmentation
                perform_sobel_segmentation(image)
            elif segmentation_type == 'prewitt':
                # Perform Prewitt edge detection segmentation
                perform_prewitt_segmentation(image)
            elif segmentation_type == 'canny':
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

    # Iterate over each preprocessing object
    for preprocessing in preprocessings:
        #Perform k-means segmentation using the Image and ImagePreprocessing objects
        print(f"Performing k-means segmentation for preprocessing {preprocessing.pk}...")

def perform_adaptive_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessing = ImagePreprocessing.objects.get(image=image)
    
    # Perform adaptive segmentation using the Image and ImagePreprocessing objects
    # You can access the Image and ImagePreprocessing data within this function
    
    
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
