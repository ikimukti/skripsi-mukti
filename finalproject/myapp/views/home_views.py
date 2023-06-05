from django.shortcuts import render
from django.views import View
from ..menus import menus


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
