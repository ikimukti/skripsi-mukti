def set_user_menus(request, context):
    # get username from request
    username = request.user.username
    print(username)
    if request.user.groups.filter(name='it_admin').exists():
        context['menus'] = it_admin_menus
    if request.user.groups.filter(name='staff').exists():
        context['menus'] = staff_menus
    if request.user.groups.filter(name='researcher').exists():
        context['menus'] = researcher_menus

    # change context['menus'] submenus url for imageUploader
    for menu in context['menus']:
        if menu['name'] == 'Images':
            for submenu in menu['submenus']:
                if submenu['name'] == 'Image by Uploader':
                    submenu['url'] = '/image/uploader/' + username + '/'

def create_menu(name, url, icon, dropdown=False, id='', submenus=None):
    menu = {'name': name, 'url': url, 'icon': icon, 'dropdown': dropdown, 'id': id}
    if submenus:
        menu['submenus'] = submenus
    return menu


menus = []

# Membuat menu untuk it_admin_menus
it_admin_menus = [
    create_menu('Dashboard', '/dashboard/', 'fas fa-tachometer-alt', id='dashboard'),
    create_menu('Account', '/account/', 'fas fa-user', dropdown=True, id='account', submenus=[
        create_menu('Profile', '/account/profile/', 'fas fa-user-circle', id='accountProfile'),
        create_menu('Change Password', '/account/change-password/', 'fas fa-key', id='accountChangePassword'),
    ]),
    create_menu('Images', '/image/', 'fas fa-image', dropdown=True, id='image', submenus=[
        create_menu('Image All', '/image/', 'fas fa-list', id='image'),
        create_menu('Image by Uploader', '/image/uploader/', 'fas fa-user', id='imageUploader'),
        create_menu('Upload', '/image/upload/', 'fas fa-upload', id='imageUpload'),
        create_menu('Summary', '/image/summary/', 'fas fa-chart-bar', id='imageSummary'),
    ]),
    create_menu('Manage', '/manage/', 'fas fa-cogs', dropdown=True, id='manage', submenus=[
        create_menu('User', '/manage/user/', 'fas fa-user', id='manageUser'),
        create_menu('Role', '/manage/role/', 'fas fa-user-tag', id='manageRole'),
        create_menu('Permission', '/manage/permission/', 'fas fa-user-lock', id='managePermission'),
        create_menu('Group', '/manage/group/', 'fas fa-users', id='manageGroup'),
    ]),
    create_menu('Reports', '/report/', 'fas fa-chart-bar', dropdown=True, id='report', submenus=[
        create_menu('Segmentation', '/report/segmentation/', 'fas fa-chart-pie', id='reportSegmentation'),
        create_menu('Export Image', '/report/export/image/', 'fas fa-file-image', id='reportExportImage'),
        create_menu('Export Report', '/report/export/report/', 'fas fa-file-pdf', id='reportExportReport'),
        create_menu('Summary', '/report/summary/', 'fas fa-chart-bar', id='reportSummary'),
    ]),
    create_menu('Preferences', '/preference/', 'fas fa-cog', dropdown=True, id='preference', submenus=[
        create_menu('Setting', '/preference/setting/', 'fas fa-cog', id='preferenceSetting'),
        create_menu('Help', '/help/', 'fas fa-question-circle', id='preferenceHelp'),
        create_menu('Docs', '/docs/', 'fas fa-book', id='preferenceDocs'),
        create_menu('Blog', '/blog/', 'fas fa-blog', id='preferenceBlog'),
        create_menu('Contact', '/contact/', 'fas fa-phone', id='preferenceContact'),
        create_menu('About', '/about/', 'fas fa-info-circle', id='preferenceAbout'),
    ]),
]

# Membuat menu untuk staff_menus
staff_menus = []
for menu in it_admin_menus:
    if menu['name'] != 'Images' and menu['name'] != 'Reports' and menu['name'] != 'Manage':
        staff_menus.append(menu)

# Membuat menu untuk researcher
researcher_menus = []
for menu in it_admin_menus:
    if menu['name'] != 'Manage':
        researcher_menus.append(menu)
