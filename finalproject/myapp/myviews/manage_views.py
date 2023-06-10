from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus


class ManageClassView(View):
    context = {
        "title": "Manage Account",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/manage/manage.html"

    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)  # set user menus
            return render(request, self.template_name, self.context)


class ManageUserClassView(View):
    context = {
        "title": "Manage User",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/manage/manageUser.html"

    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class ManageRoleClassView(View):
    context = {
        "title": "Manage Role",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/manage/manageRole.html"

    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class ManagePermissionClassView(View):
    context = {
        "title": "Manage Permission",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/manage/managePermission.html"

    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class ManageGroupClassView(View):
    context = {
        "title": "Manage Group",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/manage/manageGroup.html"

    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
