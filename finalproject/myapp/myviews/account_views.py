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
from django.contrib.auth.models import User
from myapp.forms import UserForm
from django.urls import reverse_lazy


class BaseAccountView(View):
    template_name = "myapp/account/base.html"
    context = {
        "title": "Account",
        "content": "Welcome to WeeAI! Account",
        "contributor": "WeeAI Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }

    def get_object(self):
        username = self.kwargs.get("username")
        user = User.objects.get(username=username)
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.context)
        set_user_menus(self.request, context)
        user = self.get_object()
        context["account"] = user
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            return super().get(request, *args, **kwargs)


class AccountUpdateClassView(BaseAccountView, UpdateView):
    model = User
    template_name = "myapp/account/account_update.html"
    form_class = UserForm
    success_url = reverse_lazy("myapp:account")
    failure_url = "/account/update/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Account Update"
        return context

    def form_invalid(self, form):
        print(form.cleaned_data)
        return super().form_invalid(form)

    def form_valid(self, form):
        return super().form_valid(form)


class AccountClassView(BaseAccountView, DetailView):
    model = User
    template_name = "myapp/account/account.html"
    context_object_name = "account"
    success_url = reverse_lazy("myapp:account")
    failure_url = "/account/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Account"
        return context


class AccountProfileClassView(BaseAccountView):
    template_name = "myapp/account/profile.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            context = self.context
            context["title"] = "Account Profile"
            set_user_menus(request, context)
            return render(request, self.template_name, context)


class AccountChangePasswordClassView(BaseAccountView):
    template_name = "myapp/account/password.html"

    def get(self, request, username):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            context = self.context
            context["title"] = "Account Change Password"
            set_user_menus(request, context)
            return render(request, self.template_name, context)
