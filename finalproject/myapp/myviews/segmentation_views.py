from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus


class SegmentationClassView(View):
    context = {
        "title": "Segmentation",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/segmentation.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/segmentation/segmentation.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class SegmentationProcessClassView(View):
    context = {
        "title": "Segmentation Process",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/segmentation.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/segmentation/segmentation_process.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class SegmentationSummaryClassView(View):
    context = {
        "title": "Segmentation Summary",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/segmentation.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/segmentation/segmentation_summary.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
