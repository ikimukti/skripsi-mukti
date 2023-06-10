from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
import numpy as np
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from .menus import menus, it_admin_menus, staff_menus, researcher_menus, set_user_menus
from django.db.models import Count
from .models import Image, UserProfile
from django.contrib.auth.models import User, Group
from django.db.models import Q
from .forms import ImageForm, UserForm
import cv2

from myapp.myviews.manage_views import (
    ManageClassView,
    ManageUserClassView,
    ManageRoleClassView,
    ManagePermissionClassView,
    ManageGroupClassView,
)

from myapp.myviews.report_views import (
    ReportClassView,
    ReportExportImageClassView,
    ReportExportReportClassView,
    ReportSegmentationClassView,
    ReportSummaryClassView,
)

from myapp.myviews.segmentation_views import (
    SegmentationClassView,
    SegmentationProcessClassView,
    SegmentationSummaryClassView,
)

from myapp.myviews.system_views import (
    SignInClassView,
    SignOutClassView,
    SignUpClassView,
)

from myapp.myviews.preference_views import (
    PreferenceClassView,
    AboutClassView,
    BlogClassView,
    ContactClassView,
    PreferenceSettingClassView,
    HelpClassView,
    DocsClassView,
    SettingClassView,
    DashboardClassView,
    IndexClassView,
)

from myapp.myviews.account_views import (
    AccountChangePasswordClassView,
    AccountClassView,
    AccountUpdateClassView,
    AccountProfileClassView,
)

from myapp.myviews.image_views import (
    ImageDeleteView,
    ImageDetailView,
    ImageListView,
    ImageUpdateView,
    ImageUploadView,
    ImageSummaryView,
    ImageUploaderView,
)
