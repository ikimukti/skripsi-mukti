from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus


class ReportClassView(View):
    context = {
        "title": "Report",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/report.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/report/report.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)  # set user menus
            return render(request, self.template_name, self.context)


class ReportSegmentationClassView(View):
    context = {
        "title": "Segmentation Report",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/report.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/report/reportSegmentation.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class ReportExportImageClassView(View):
    context = {
        "title": "Export Image Report",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/report.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/report/reportExportImage.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class ReportExportReportClassView(View):
    context = {
        "title": "Export Report",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/report.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/report/reportExportReport.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class ReportSummaryClassView(View):
    context = {
        "title": "Summary Report",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/report.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/report/reportSummary.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
