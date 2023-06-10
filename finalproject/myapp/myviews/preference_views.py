from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus


class IndexClassView(View):
    template_name = "myapp/index.html"
    context = {
        "title": "Home",
        "contributor": "WeeAI Team",
        "content": "Welcome to WeeAI!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "logo": "myapp/images/Logo.png",
        "menus": menus,
    }

    def get(self, request):
        # codition request user is authenticated
        if request.user.is_authenticated:
            return redirect("myapp:dashboard")
        else:
            return render(request, self.template_name, self.context)


class DashboardClassView(View):
    # set context first
    context = {
        "title": "Dashboard",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/dashboard.html"  # set template name

    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)  # set user menus
            return render(request, self.template_name, self.context)


class AboutClassView(View):
    context = {
        "title": "About",
        "contributor": "WeeAI Team",
        "content": "Welcome to WeeAI!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/about.html"

    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)


class BlogClassView(View):
    context = {
        "title": "Blog",
        "contributor": "WeeAI Team",
        "content": "Welcome to WeeAI!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
        "posts": [
            {
                "title": "Blog Post 1",
                "url": "/blog/post1/",
                "content": "Welcome to WeeAI!",
                "author": "WeeAI Team",
                "date_posted": "August 27, 2018",
            },
            {
                "title": "Blog Post 2",
                "url": "/blog/post2/",
                "content": "Welcome to WeeAI!",
                "author": "WeeAI Team",
                "date_posted": "August 28, 2018",
            },
            {
                "title": "Blog Post 3",
                "url": "/blog/post3/",
                "content": "Welcome to WeeAI!",
                "author": "WeeAI Team",
                "date_posted": "August 29, 2018",
            },
        ],
    }
    template_name = "myapp/blog.html"

    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)


class ContactClassView(View):
    context = {
        "title": "Contact",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/contact.html"

    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)


class DocsClassView(View):
    context = {
        "title": "Docs",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/docs.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class HelpClassView(View):
    context = {
        "title": "Help",
        "contributor": "WeeAI Team",
        "content": "Welcome to WeeAI!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/help.html"

    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)


class PreferenceSettingClassView(View):
    context = {
        "title": "Setting",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/preference.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/preference/preferenceSetting.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class PreferenceClassView(View):
    context = {
        "title": "Preferences",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/preference.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/preference/preference.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class SettingClassView(View):
    context = {
        "title": "Settings",
        "contributor": "WeeAI Team",
        "content": "Welcome to WeeAI!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/preference/preferenceSetting.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
