from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

# models import
from django.contrib.auth.models import User

# forms import
from myapp.forms import UserForm

from django.urls import reverse_lazy


class AccountUpdateClassView(UpdateView):
    model = User
    template_name = "myapp/account/account_update.html"
    form_class = UserForm
    success_url = reverse_lazy("myapp:account")
    failure_url = "/account/update/"

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Account Update"
        context["contributor"] = "WeeAI Team"
        context["content"] = "Welcome to WeeAI! Update Account"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        user = self.get_object()
        context["account"] = user
        return context

    # override get_object method
    def get_object(self, queryset=None):
        # retrieve user object based on the provided username and UserProfile object
        username = self.kwargs.get("username")
        user = User.objects.get(username=username)
        return user

    # invalid form
    def form_invalid(self, form):
        print(form.cleaned_data)
        return super().form_invalid(form)

    # form save
    def form_valid(self, form):
        return super().form_valid(form)

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class AccountClassView(DetailView):
    model = User
    template_name = "myapp/account/account.html"
    context_object_name = "account"
    success_url = reverse_lazy("myapp:account")
    failure_url = "/account/"

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Account"
        context["contributor"] = "WeeAI Team"
        context["content"] = "Welcome to WeeAI! Account"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        # get_object to retrieve user object and get user profile
        user = self.get_object()
        context["account"] = user
        return context

    # override get_object method
    def get_object(self, queryset=None):
        # retrieve user object based on the provided username and UserProfile object
        username = self.kwargs.get("username")
        user = User.objects.get(username=username)
        return user

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class AccountProfileClassView(View):
    context = {
        "title": "Profile",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/account/profile.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class AccountChangePasswordClassView(View):
    context = {
        "title": "Change Password",
        "content": "Welcome to WeeAI!",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/account/password.html"

    # override method get
    def get(self, request, username):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)  # set user menus
            return render(request, self.template_name, self.context)
