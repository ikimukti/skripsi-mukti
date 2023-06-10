from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus


class ManageBaseView(View):
    base_context = {
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }

    def get(self, request):
        return render(request, self.template_name, self.context)

    def post(self, request):
        return render(request, self.template_name, self.context)


class ManageClassView(ManageBaseView):
    template_name = "myapp/manage/manage.html"
    context = {
        "title": "Manage",
        **ManageBaseView.base_context,
    }

    # override get method
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return super().get(request)


class ManageUsersClassView(ManageBaseView):
    template_name = "myapp/manage/manage_users.html"
    context = {
        "title": "Manage Users",
        **ManageBaseView.base_context,
    }

    # override get method
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return super().get(request)


class ManagePermissionsClassView(ManageBaseView):
    template_name = "myapp/manage/manage_permissions.html"
    context = {
        "title": "Manage Permissions",
        **ManageBaseView.base_context,
    }

    # override get method
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return super().get(request)


class ManageRoleClassView(ManageBaseView):
    template_name = "myapp/manage/manage_role.html"
    context = {
        "title": "Manage Settings",
        **ManageBaseView.base_context,
    }

    # override get method
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return super().get(request)


class ManageGroupClassView(ManageBaseView):
    template_name = "myapp/manage/manage_group.html"
    context = {
        "title": "Manage Group",
        **ManageBaseView.base_context,
    }

    # override get method
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return super().get(request)
