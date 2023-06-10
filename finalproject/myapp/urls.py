from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.SignUpClassView.as_view(), name="signup"),
    path("signout/", views.SignOutClassView.as_view(), name="signout"),
    path("signin/", views.SignInClassView.as_view(), name="signin"),
    path(
        "segmentation/summary/",
        views.SegmentationSummaryClassView.as_view(),
        name="segmentation_summary",
    ),
    path(
        "segmentation/process/",
        views.SegmentationProcessClassView.as_view(),
        name="segmentation_process",
    ),
    path("segmentation/", views.SegmentationClassView.as_view(), name="segmentation"),
    path("setting/", views.SettingClassView.as_view(), name="setting"),
    path(
        "report/summary/", views.ReportSummaryClassView.as_view(), name="report_summary"
    ),
    path(
        "report/segmentation/",
        views.ReportSegmentationClassView.as_view(),
        name="report_segmentation",
    ),
    path(
        "report/export/report/",
        views.ReportExportReportClassView.as_view(),
        name="report_export_report",
    ),
    path(
        "report/export/image/",
        views.ReportExportImageClassView.as_view(),
        name="report_export_image",
    ),
    path("report/", views.ReportClassView.as_view(), name="report"),
    path(
        "preference/setting/",
        views.PreferenceSettingClassView.as_view(),
        name="preference_setting",
    ),
    path("preference/", views.PreferenceClassView.as_view(), name="preference"),
    path("manage/user/", views.ManageUsersClassView.as_view(), name="manage_user"),
    path("manage/role/", views.ManageRoleClassView.as_view(), name="manage_role"),
    path(
        "manage/permission/",
        views.ManagePermissionsClassView.as_view(),
        name="manage_permission",
    ),
    path("manage/group/", views.ManageGroupClassView.as_view(), name="manage_group"),
    path("manage/", views.ManageClassView.as_view(), name="manage"),
    path(
        "image/uploader/<str:uploader>/",
        views.ImageUploaderView.as_view(),
        name="image_uploader",
    ),
    path("image/upload/", views.ImageUploadView.as_view(), name="image_upload"),
    path(
        "image/update/<int:pk>/", views.ImageUpdateView.as_view(), name="image_update"
    ),
    path("image/summary/", views.ImageSummaryView.as_view(), name="image_summary"),
    path(
        "image/delete/<int:pk>/", views.ImageDeleteView.as_view(), name="image_delete"
    ),
    path(
        "image/detail/<int:pk>/", views.ImageDetailView.as_view(), name="image_detail"
    ),
    path("image/", views.ImageListView.as_view(), name="image_list"),
    path("help/", views.HelpClassView.as_view(), name="help"),
    path("docs/", views.DocsClassView.as_view(), name="docs"),
    path("dashboard/", views.DashboardClassView.as_view(), name="dashboard"),
    path("contact/", views.ContactClassView.as_view(), name="contact"),
    path("blog/", views.BlogClassView.as_view(), name="blog"),
    path(
        "account/profile/",
        views.AccountProfileClassView.as_view(),
        name="account_profile",
    ),
    path(
        "account/<str:username>/update/",
        views.AccountUpdateClassView.as_view(),
        name="account_update",
    ),
    path(
        "account/<str:username>/change-password/",
        views.AccountChangePasswordClassView.as_view(),
        name="account_change_password",
    ),
    path("account/<str:username>/", views.AccountClassView.as_view(), name="account"),
    path("about/", views.AboutClassView.as_view(), name="about"),
    path("", views.IndexClassView.as_view(), name="index"),
]
