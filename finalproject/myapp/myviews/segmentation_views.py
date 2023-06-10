from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus


class SegmentationBaseView(View):
    base_context = {
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/segmentation.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            self.context = {**self.base_context}  # Add this line
            set_user_menus(request, self.context)
            self.context["title"] = self.title  # Add this line
            return render(
                request, self.template_name, self.context
            )  # Replace `context` with `self.context`


class SegmentationClassView(SegmentationBaseView):
    template_name = "myapp/segmentation/segmentation.html"
    context = {
        "title": "Segmentation",
        **SegmentationBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Segmentation"  # Add this line
        return super().get(request)  # Call the parent's get method


class SegmentationProcessClassView(SegmentationBaseView):
    template_name = "myapp/segmentation/segmentation_process.html"
    context = {
        "title": "Segmentation Process",
        **SegmentationBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Segmentation Process"  # Add this line
        return super().get(request)  # Call the parent's get method


class SegmentationSummaryClassView(SegmentationBaseView):
    template_name = "myapp/segmentation/segmentation_summary.html"
    context = {
        "title": "Segmentation Summary",
        **SegmentationBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Segmentation Summary"  # Add this line
        return super().get(request)  # Call the parent's get method
