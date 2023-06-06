from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

# Create your views here.
from django.views import View
# get menus = [] from .menus
from .menus import menus
# Count
from django.db.models import Count

from .models import Image
# model user
from django.contrib.auth.models import User
# form
from .forms import ImageForm

class ImageUploadView(CreateView):
    form_class = ImageForm
    template_name = 'myapp/image/image_upload.html'
    success_url = '/image/'
    failure_url = '/image/upload/'
    # form_valid
    def form_valid(self, form):
        form.instance.uploader = self.request.user
        print("error nya mau di cek")
        return super().form_valid(form)
    # form_invalid
    def form_invalid(self, form):
        form = ImageForm(self.request.POST, self.request.FILES)
        # a = reqeust.FILES
        files = self.request.FILES.getlist('image')
        if files:
            # chage files to form image
            form.instance.image = files[0]

    # form save
    def form_save(self, form):
        form.instance.uploader = self.request.user
        print("error nya mau di cek 3")
        return super().form_save(form)
    
    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Image Create'
        context['contributor'] = 'WeeAI Team'
        context['content'] = 'Welcome to WeeAI! Create Image'
        context['app_css'] = 'myapp/css/styles.css'
        context['app_js'] = 'myapp/js/scripts.js'
        context['logo'] = 'myapp/images/Logo.png'
        context['menus'] = menus
        return context

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
        # categories uploader by uploader name in Image model uploader_id
        context['uploader'] = User.objects.get(id=self.object.uploader_id)
        # get 5 image by uploader lastest
        context['images'] = Image.objects.filter(uploader_id=self.object.uploader_id).order_by('-created_at')[:5]

        return context


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
        
        return render(request, self.template_name, self.context)

class DashboardClassView(View):
    context = {
        'title': 'Dashboard',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/dashboard.html'
    # override method get
    def get(self, request):
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
        return render(request, self.template_name, self.context)
    
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
        return render(request, self.template_name, self.context)
    
class AccountClassView(View):
    context = {
        'title': 'Account',
        'content': 'Welcome to WeeAI!',
        'contributor': 'WeeAI Team',
        'app_css': 'myapp/css/styles.css',
        'app_js': 'myapp/js/scripts.js',
        'menus': menus,
        'logo': 'myapp/images/Logo.png',
    }
    template_name = 'myapp/account/account.html'
    # override method get
    def get(self, request):
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
    def get(self, request):
        return render(request, self.template_name, self.context)