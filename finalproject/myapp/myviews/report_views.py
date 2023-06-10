from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus


class ReportBaseView(View):
    base_context = {
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
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


class ReportClassView(ReportBaseView):
    template_name = "myapp/report/report.html"
    context = {
        "title": "Report",
        **ReportBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Report"  # Add this line
        return super().get(request)  # Call the parent's get method


class ReportSegmentationClassView(ReportBaseView):
    template_name = "myapp/report/report_segmentation.html"
    context = {
        "title": "Segmentation Report",
        **ReportBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Segmentation Report"  # Add this line
        return super().get(request)  # Call the parent's get method


class ReportExportImageClassView(ReportBaseView):
    template_name = "myapp/report/report_export_image.html"
    context = {
        "title": "Export Image Report",
        **ReportBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Export Image Report"  # Add this line
        return super().get(request)  # Call the parent's get method


class ReportExportReportClassView(ReportBaseView):
    template_name = "myapp/report/report_export_report.html"
    context = {
        "title": "Export Report",
        **ReportBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Export Report"  # Add this line
        return super().get(request)  # Call the parent's get method


class ReportSummaryClassView(ReportBaseView):
    template_name = "myapp/report/report_summary.html"
    context = {
        "title": "Summary Report",
        **ReportBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Summary Report"  # Add this line
        return super().get(request)  # Call the parent's get method
