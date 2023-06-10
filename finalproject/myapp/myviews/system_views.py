from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.contrib.auth import authenticate, login, logout


class SignInClassView(View):
    context = {
        "title": "Sign In",
        "contributor": "WeeAI Team",
        "content": "Welcome to WeeAI!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/system/signin.html"

    # override method get
    def get(self, request):
        # codition request user is authenticated
        if request.user.is_authenticated:
            return redirect("myapp:dashboard")
        else:
            return render(request, self.template_name, self.context)

    # override method post
    def post(self, request):
        print(request.POST)
        # get username and password
        username_signin = request.POST["username"]
        password_signin = request.POST["password"]
        # authenticate user
        user = authenticate(request, username=username_signin, password=password_signin)
        print(user)
        # condition user is not None
        if user is not None:
            # login user
            login(request, user)
            return redirect("myapp:dashboard")
        else:
            # update context
            self.context["error"] = "Username or Password is incorrect!"
            return render(request, self.template_name, self.context)


class SignUpClassView(View):
    context = {
        "title": "Sign Up",
        "contributor": "WeeAI Team",
        "content": "Welcome to WeeAI!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/system/signup.html"

    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)

    # override method post


class SignOutClassView(View):
    context = {
        "title": "Sign Out",
        "contributor": "WeeAI Team",
        "content": "Welcome to WeeAI!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/system/signout.html"

    # override method get
    def get(self, request):
        # codition request user is authenticated
        if request.user.is_authenticated:
            return render(request, self.template_name, self.context)
        else:
            return redirect("myapp:signin")

    # override method post
    def post(self, request):
        print(request.POST)
        if request.POST["signout"] == "signout":
            # logout user
            logout(request)
            self.context["message"] = "Sign Out Successfully!"
            return redirect("myapp:signin")
        else:
            self.context["error"] = "Sign Out Failed!"
            return redirect("myapp:dashboard")
