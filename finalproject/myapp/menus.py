def set_user_menus(request, context):
    # get username from request
    username = request.user.username
    if request.user.groups.filter(name="it_admin").exists():
        context["menus"] = it_admin_menus
    if request.user.groups.filter(name="staff").exists():
        context["menus"] = staff_menus
    if request.user.groups.filter(name="researcher").exists():
        context["menus"] = researcher_menus

    # change context['menus'] submenus url for imageUploader
    # change context['menus'] submenus url for account_detail
    for menu in context["menus"]:
        if menu["name"] == "Images":
            for submenu in menu["submenus"]:
                if submenu["name"] == "Image by Uploader":
                    submenu["url"] = "/image/uploader/" + username + "/"
        if menu["name"] == "Account":
            menu["url"] = "/account/" + username + "/"
            for submenu in menu["submenus"]:
                if submenu["name"] == "Profile":
                    submenu["url"] = "/account/" + username + "/"
                if submenu["name"] == "Change Password":
                    submenu["url"] = "/account/" + username + "/change-password/"


def create_menu(name, url, icon, dropdown=False, id="", submenus=None):
    menu = {"name": name, "url": url, "icon": icon, "dropdown": dropdown, "id": id}
    if submenus:
        menu["submenus"] = submenus
    return menu


menus = []

# Membuat menu untuk it_admin_menus
it_admin_menus = [
    create_menu("Dashboard", "/dashboard/", "fas fa-tachometer-alt", id="dashboard"),
    create_menu(
        "Administrator",
        "/admin/",
        "fas fa-user-shield",
        dropdown=False,
        id="administrator",
    ),
    create_menu(
        "Account",
        "/account/",
        "fas fa-user",
        dropdown=True,
        id="account_detail",
        submenus=[
            create_menu(
                "Profile",
                "/account/profile/",
                "fas fa-user-circle",
                id="account_detail",
            ),
            create_menu(
                "Change Password",
                "/account/change-password/",
                "fas fa-key",
                id="account_change_password",
            ),
        ],
    ),
    create_menu(
        "Manage User",
        "/manage/user/",
        "fa-solid fa-users-between-lines",
        id="manage_user",
    ),
    create_menu(
        "Images",
        "/image/",
        "fas fa-image",
        dropdown=True,
        id="image",
        submenus=[
            create_menu("Image All", "/image/", "fas fa-list", id="image"),
            create_menu(
                "Image by Uploader",
                "/image/uploader/",
                "fas fa-user",
                id="image_by_uploader",
            ),
            create_menu("Upload", "/image/upload/", "fas fa-upload", id="image_upload"),
            create_menu(
                "Summary", "/image/summary/", "fas fa-chart-bar", id="image_summary"
            ),
        ],
    ),
    create_menu(
        "Segmentation",
        "/segmentation/",
        "fas fa-chart-pie",
        dropdown=True,
        id="segmentation",
        submenus=[
            create_menu(
                "Segmentation All", "/segmentation/", "fas fa-list", id="segmentation"
            ),
            create_menu(
                "Summary",
                "/segmentation/summary/",
                "fas fa-chart-bar",
                id="segmentation_summary",
            ),
        ],
    ),
    create_menu(
        "Reports",
        "/report/",
        "fas fa-chart-bar",
        dropdown=True,
        id="report",
        submenus=[
            create_menu(
                "Segmentation",
                "/report/segmentation/",
                "fas fa-chart-pie",
                id="report_segmentation",
            ),
            create_menu(
                "Export Image",
                "/report/export/image/",
                "fas fa-file-image",
                id="report_export_image",
            ),
            create_menu(
                "Export Report",
                "/report/export/report/",
                "fas fa-file-pdf",
                id="report_export_report",
            ),
            create_menu(
                "Summary", "/report/summary/", "fas fa-chart-bar", id="report_summary"
            ),
        ],
    ),
    create_menu(
        "Preferences",
        "/preference/",
        "fas fa-cog",
        dropdown=True,
        id="preference",
        submenus=[
            create_menu(
                "Setting", "/preference/setting/", "fas fa-cog", id="preference_setting"
            ),
            create_menu("Help", "/help/", "fas fa-question-circle", id="help"),
            create_menu("Docs", "/docs/", "fas fa-book", id="docs"),
            create_menu("Blog", "/blog/", "fas fa-blog", id="blog"),
            create_menu("Contact", "/contact/", "fas fa-phone", id="contact"),
            create_menu("About", "/about/", "fas fa-info-circle", id="about"),
        ],
    ),
]

# Membuat menu untuk staff_menus
staff_menus = []
for menu in it_admin_menus:
    if (
        menu["name"] != "Images"
        and menu["name"] != "Reports"
        and menu["name"] != "Manage"
    ):
        staff_menus.append(menu)

# Membuat menu untuk researcher
researcher_menus = []
for menu in it_admin_menus:
    if menu["name"] != "Manage":
        researcher_menus.append(menu)
