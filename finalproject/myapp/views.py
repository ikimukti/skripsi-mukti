from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
import numpy as np
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from .menus import menus, it_admin_menus, staff_menus, researcher_menus, set_user_menus
from django.db.models import Count
from .models import Image
from django.contrib.auth.models import User, Group
from django.db.models import Q
from .forms import ImageForm, UserForm
import cv2


    
class AccountClassView(DetailView):
    model = User
    template_name = 'myapp/account/account.html'
    context_object_name = 'account'
    success_url = reverse_lazy('myapp:account')
    failure_url = '/account/'

    #update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Account'
        context['contributor'] = 'WeeAI Team'
        context['content'] = 'Welcome to WeeAI! Account'
        context['app_css'] = 'myapp/css/styles.css'
        context['app_js'] = 'myapp/js/scripts.js'
        context['logo'] = 'myapp/images/Logo.png'
        context['menus'] = menus
        set_user_menus(self.request, context)
        # get_object to retrieve user object
        user = self.get_object()
        context['account'] = user
        return context
    
    # override get_object method
    def get_object(self, queryset=None):
        # retrieve user object based on the provided username
        username = self.kwargs.get('username')
        return User.objects.get(username=username)
    
    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)
        
class ImageUpdateView(UpdateView):
    model = Image
    template_name = 'myapp/image/image_update.html'
    form_class = ImageForm
    success_url = reverse_lazy('myapp:image_list')
    failure_url = '/image/update/'

    #update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Image Update'
        context['contributor'] = 'WeeAI Team'
        context['content'] = 'Welcome to WeeAI! Update Image'
        context['app_css'] = 'myapp/css/styles.css'
        context['app_js'] = 'myapp/js/scripts.js'
        context['logo'] = 'myapp/images/Logo.png'
        context['menus'] = menus
        set_user_menus(self.request, context)
        return context
    
    # invalid form
    def form_invalid(self, form):
        print(form.cleaned_data)
        return super().form_invalid(form)

    # form save
    def form_valid(self, form):
        # rewrite save method in form
        # get image channel from form data image file
        # cv2 image channel get image channel from shape
        image_channel = cv2.imread(form.cleaned_data['image'].temporary_file_path()).shape[2]
        # rewrite channel in form data
        form.instance.channel = image_channel
        # cv2 get dpi from image file
        image_dpi = cv2.imread(form.cleaned_data['image'].temporary_file_path()).shape[0]
        # rewrite dpi in form data
        form.instance.dpi = image_dpi
        return super().form_valid(form)
    
    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)

class ImageDeleteView(DeleteView):
    model = Image
    template_name = 'myapp/image/image_delete.html'
    success_url = reverse_lazy('myapp:image_list')

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Image Delete'
        context['contributor'] = 'WeeAI Team'
        context['content'] = 'Welcome to WeeAI! Delete Image'
        context['app_css'] = 'myapp/css/styles.css'
        context['app_js'] = 'myapp/js/scripts.js'
        context['logo'] = 'myapp/images/Logo.png'
        context['menus'] = menus
        set_user_menus(self.request, context)
        return context
    
    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)

class ImageUploadView(CreateView):
    form_class = ImageForm
    template_name = 'myapp/image/image_upload.html'
    failure_url = '/image/upload/'
    # success_url = reverse_lazy('image_list')  # Assuming you have a URL name for the image list view

    # invalid form
    def form_invalid(self, form):
        print(form.cleaned_data)
        return super().form_invalid(form)

    # form save
    def form_valid(self, form):
        # rewrite save method in form
        # rewrite channel in form data
        # form.instance.channel = image_channel
        image_data = form.cleaned_data['image'].read()
        image_array = np.frombuffer(image_data, np.uint8)
        image_channel = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[2]
        form.instance.channel = image_channel
        # rewrite dpi in form data
        image_dpi = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[0]
        form.instance.dpi = image_dpi
        return super().form_valid(form)
    
    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Image Upload'
        context['contributor'] = 'WeeAI Team'
        context['content'] = 'Welcome to WeeAI! Create Image'
        context['app_css'] = 'myapp/css/styles.css'
        context['app_js'] = 'myapp/js/scripts.js'
        context['logo'] = 'myapp/images/Logo.png'
        context['menus'] = menus
        set_user_menus(self.request, context)
        return context
    
    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)
        
class ImageSummaryView(ListView):
    model = Image
    template_name = 'myapp/image/image_summary.html'
    context_object_name = 'images'
    ordering = ['-created_at']
    paginate_by = 8

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Image Summary'
        context['contributor'] = 'WeeAI Team'
        context['content'] = 'Welcome to WeeAI! Image Summary'
        context['app_css'] = 'myapp/css/styles.css'
        context['app_js'] = 'myapp/js/scripts.js'
        context['logo'] = 'myapp/images/Logo.png'
        context['menus'] = menus
        set_user_menus(self.request, context)
        # categories uploader name with name of uploader in User model
        uploaders_name = User.objects.filter(
            image__isnull=False).values('username').distinct()
        context['uploaders_name'] = uploaders_name
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)

class ImageListView(ListView):
    model = Image
    template_name = 'myapp/image/image_list.html'
    context_object_name = 'images'
    ordering = ['-created_at']
    paginate_by = 8

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Image List'
        context['contributor'] = 'WeeAI Team'
        context['content'] = 'Welcome to WeeAI!'
        context['app_css'] = 'myapp/css/styles.css'
        context['app_js'] = 'myapp/js/scripts.js'
        context['logo'] = 'myapp/images/Logo.png'
        context['menus'] = menus
        set_user_menus(self.request, context)
        # categories uploader name with name of uploader in User model
        uploaders_name = User.objects.filter(image__isnull=False).distinct().values_list('username', flat=True)
        # count Image by uploader
        uploaders_count = Image.objects.values('uploader').distinct().annotate(count=Count('uploader')).values_list('count', flat=True)
        # context['uploaders'] = {'name': uploaders_name, 'count': uploaders_count}
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({'name': name, 'count': count})
        context['uploaders'] = uploaders
        # categories color name
        context['colors'] = self.model.objects.values_list('color', flat=True).distinct()
        return context
    
    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)

    
        
class ImageUploaderView(ListView):
    model = Image
    template_name = 'myapp/image/image_by_uploader.html'
    context_object_name = 'images'
    ordering = ['-created_at']
    paginate_by = 8
    # get queryset
    def get_queryset(self):
        uploader = self.kwargs['uploader']
        return Image.objects.filter(uploader__username=uploader)
    
    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Capitalize first letter of uploader
        context['title'] = 'Image Uploader ' + self.kwargs['uploader'].capitalize()
        context['kwargs_uploader'] = self.kwargs['uploader']
        context['contributor'] = 'WeeAI Team'
        context['content'] = 'Welcome to WeeAI!'
        context['app_css'] = 'myapp/css/styles.css'
        context['app_js'] = 'myapp/js/scripts.js'
        context['logo'] = 'myapp/images/Logo.png'
        context['menus'] = menus
        set_user_menus(self.request, context)
        # categories uploader name with name of uploader in User model
        uploaders_name = User.objects.filter(image__isnull=False).distinct().values_list('username', flat=True)
        # count Image by uploader
        uploaders_count = Image.objects.values('uploader').distinct().annotate(count=Count('uploader')).values_list('count', flat=True).order_by('-count')
        # context['uploaders'] = {'name': uploaders_name, 'count': uploaders_count}
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({'name': name, 'count': count})
        context['uploaders'] = uploaders
        # categories color name
        context['colors'] = self.model.objects.values_list('color', flat=True).distinct()
        return context
    
    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)

class ImageDetailView(DetailView):
    model = Image
    template_name = 'myapp/image/image_detail.html'
    context_object_name = 'image'
    # update context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Image Detail'
        context['contributor'] = 'WeeAI Team'
        context['content'] = 'Welcome to WeeAI!'
        context['app_css'] = 'myapp/css/styles.css'
        context['app_js'] = 'myapp/js/scripts.js'
        context['logo'] = 'myapp/images/Logo.png'
        context['menus'] = menus
        set_user_menus(self.request, context)
        # categories uploader by uploader name in Image model uploader_id
        context['uploader'] = User.objects.get(id=self.object.uploader_id)
        # get 5 image by uploader lastest
        context['images'] = Image.objects.filter(uploader_id=self.object.uploader_id).order_by('-created_at')[:5]

        return context
    
    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class IndexClassView(View):
    template_name = 'myapp/index.html'
    context = {
        'title': 'Home',
        'contributor': 'WeeAI Team',
        'content': 'Welcome to WeeAI!',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'logo': 'myapp/images/Logo.png',
        'menus': menus,
    }
    def get(self, request):
        # codition request user is authenticated
        if request.user.is_authenticated:
            return redirect('myapp:dashboard')
        else:
            return render(request, self.template_name, self.context)

class DashboardClassView(View):
    # set context first
    context = {
        'title': 'Dashboard',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/dashboard.html' # set template name
    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)  # set user menus
            return render(request, self.template_name, self.context)

class SignInClassView(View):
    context = {
        'title': 'Sign In',
        'contributor': 'WeeAI Team',
        'content': 'Welcome to WeeAI!',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/system/signin.html'
    # override method get
    def get(self, request):
        # codition request user is authenticated
        if request.user.is_authenticated:
            return redirect('myapp:dashboard')
        else:
            return render(request, self.template_name, self.context)
        
    # override method post
    def post(self, request):
        print(request.POST)
        # get username and password
        username_signin = request.POST['username']
        password_signin = request.POST['password']
        # authenticate user
        user = authenticate(request, username=username_signin, password=password_signin)
        print(user)
        # condition user is not None
        if user is not None:
            # login user
            login(request, user)
            return redirect('myapp:dashboard')
        else:
            # update context
            self.context['error'] = 'Username or Password is incorrect!'
            return render(request, self.template_name, self.context)

class SignUpClassView(View):
    context = {
        'title': 'Sign Up',
        'contributor': 'WeeAI Team',
        'content': 'Welcome to WeeAI!',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/system/signup.html'
    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)
    
    # override method post

    
# @login_required(login_url='myapp:signin')
class SignOutClassView(View):
    context = {
        'title': 'Sign Out',
        'contributor': 'WeeAI Team',
        'content': 'Welcome to WeeAI!',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/system/signout.html'
    # override method get
    def get(self, request):
        # codition request user is authenticated
        if request.user.is_authenticated:
            return render(request, self.template_name, self.context)
        else:
            return redirect('myapp:signin')
    
    # override method post
    def post(self, request):
        print(request.POST)
        if request.POST['signout'] == 'signout':
            # logout user
            logout(request)
            self.context['message'] = 'Sign Out Successfully!'
            return redirect('myapp:signin')
        else:
            self.context['error'] = 'Sign Out Failed!'
            return redirect('myapp:dashboard')
    
class AboutClassView(View):
    context = {
        'title': 'About',
        'contributor': 'WeeAI Team',
        'content': 'Welcome to WeeAI!',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/about.html'
    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)
    
class BlogClassView(View):
    context = {
        'title': 'Blog',
        'contributor': 'WeeAI Team',
        'content': 'Welcome to WeeAI!',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
        'posts': [
            {'title': 'Blog Post 1', 'url': '/blog/post1/', 'content': 'Welcome to WeeAI!','author': 'WeeAI Team','date_posted': 'August 27, 2018'},
            {'title': 'Blog Post 2', 'url': '/blog/post2/', 'content': 'Welcome to WeeAI!','author': 'WeeAI Team','date_posted': 'August 28, 2018'},
            {'title': 'Blog Post 3', 'url': '/blog/post3/', 'content': 'Welcome to WeeAI!','author': 'WeeAI Team','date_posted': 'August 29, 2018'},
        ],
    }
    template_name = 'myapp/blog.html'
    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)
    
class ContactClassView(View):
    context = {
        'title': 'Contact',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/contact.html'
    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)
    
class DocsClassView(View):
    context = {
        'title': 'Docs',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/docs.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
        
    
class HelpClassView(View):
    context = {
        'title': 'Help',
        'contributor': 'WeeAI Team',
        'content': 'Welcome to WeeAI!',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/help.html'
    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)
    
class PreferenceSettingClassView(View):
    context = {
        'title': 'Setting',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/preference.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/preference/preferenceSetting.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
        
class PreferenceClassView(View):
    context = {
        'title': 'Preferences',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/preference.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/preference/preference.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context) 
    
class SettingClassView(View):
    context = {
        'title': 'Settings',
        'contributor': 'WeeAI Team',
        'content': 'Welcome to WeeAI!',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/preference/preferenceSetting.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
        
class ReportClassView(View):
    context = {
        'title': 'Report',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/report.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/report/report.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)  # set user menus
            return render(request, self.template_name, self.context)
    
class ReportSegmentationClassView(View):
    context = {
        'title': 'Segmentation Report',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/report.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/report/reportSegmentation.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)

class ReportExportImageClassView(View):
    context = {
        'title': 'Export Image Report',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/report.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/report/reportExportImage.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
        

class ReportExportReportClassView(View):
    context = {
        'title': 'Export Report',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/report.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/report/reportExportReport.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)

class ReportSummaryClassView(View):
    context = {
        'title': 'Summary Report',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/report.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/report/reportSummary.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
        
class SegmentationClassView(View):
    context = {
        'title': 'Segmentation',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/segmentation.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/segmentation/segmentation.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)

class SegmentationProcessClassView(View):
    context = {
        'title': 'Segmentation Process',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/segmentation.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/segmentation/segmentation_process.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated 
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
        
class SegmentationSummaryClassView(View):
    context = {
        'title': 'Segmentation Summary',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/segmentation.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/segmentation/segmentation_summary.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)

class ManageClassView(View):
    context = {
        'title': 'Manage Account',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/manage/manage.html'
    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)  # set user menus
            return render(request, self.template_name, self.context)
    
class ManageUserClassView(View):
    context = {
        'title': 'Manage User',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/manage/manageUser.html'
    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
    
class ManageRoleClassView(View):
    context = {
        'title': 'Manage Role',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/manage/manageRole.html'
    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)

class ManagePermissionClassView(View):
    context = {
        'title': 'Manage Permission',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/manage/managePermission.html'
    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
        

class ManageGroupClassView(View):
    context = {
        'title': 'Manage Group',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/manage/manageGroup.html'
    # override method get
    def get(self, request):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
        

        

class AccountProfileClassView(View):
    context = {
        'title': 'Profile',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/account/profile.html'
    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)

class AccountChangePasswordClassView(View):
    context = {
        'title': 'Change Password',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/account/password.html'
    # override method get
    def get(self, request, username):
        # codition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect('myapp:signin')
        else:
            set_user_menus(request, self.context)  # set user menus
            return render(request, self.template_name, self.context)