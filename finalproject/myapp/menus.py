menus = [
    {'name': 'Dashboard', 'url': '/dashboard/', 'icon': 'fas fa-tachometer-alt', 'id': 'dashboard'},
    
    {'name': 'Account', 'url': '/account/', 'icon': 'fas fa-user', 'dropdown': True, 'id': 'account'
    ,'submenus': [
        {'name': 'Profile', 'url': '/account/profile/', 'icon': 'fas fa-user-circle', 'id': 'accountProfile'},
        {'name': 'Change Password', 'url': '/account/change-password/', 'icon': 'fas fa-key', 'id': 'accountChangePassword'},
    ]},
    {'name': 'Images', 'url': '/image/', 'icon': 'fas fa-image', 'dropdown': True, 'id': 'image'
    ,'submenus': [
        {'name': 'Image All', 'url': '/image/', 'icon': 'fas fa-list', 'id': 'image'},
        {'name': 'Image by Uploader', 'url': '/image/uploader/', 'icon': 'fas fa-user', 'id': 'imageUploader'},
        {'name': 'Upload', 'url': '/image/upload/', 'icon': 'fas fa-upload', 'id': 'imageUpload'},
        {'name': 'Summary', 'url': '/image/summary/', 'icon': 'fas fa-chart-bar', 'id': 'imageSummary'},
        {'name': 'Manage', 'url': '/image/manage/', 'icon': 'fas fa-cog', 'id': 'imageManage'},
    ]},
    # submenus manage
    {'name': 'Manage', 'url': '/manage/', 'icon': 'fas fa-cogs', 'dropdown': True, 'id': 'manage'
    ,'submenus': [
        {'name': 'User', 'url': '/manage/user/', 'icon': 'fas fa-user', 'id': 'manageUser'},
        {'name': 'Role', 'url': '/manage/role/', 'icon': 'fas fa-user-tag', 'id': 'manageRole'},
        {'name': 'Permission', 'url': '/manage/permission/', 'icon': 'fas fa-user-lock', 'id': 'managePermission'},
        {'name': 'Group', 'url': '/manage/group/', 'icon': 'fas fa-users', 'id': 'manageGroup'},
    ]},
    {'name': 'Reports', 'url': '/report/', 'icon': 'fas fa-chart-bar', 'dropdown': True, 'id': 'report'
    ,'submenus': [
        {'name': 'Segmentation', 'url': '/report/segmentation/', 'icon': 'fas fa-chart-pie', 'id': 'reportSegmentation'},
        {'name': 'Export Image', 'url': '/report/export/image/', 'icon': 'fas fa-file-image', 'id': 'reportExportImage'},
        {'name': 'Export Report', 'url': '/report/export/report/', 'icon': 'fas fa-file-pdf', 'id': 'reportExportReport'},
        {'name': 'Summary', 'url': '/report/summary/', 'icon': 'fas fa-chart-bar', 'id': 'reportSummary'},
    ]},
    {'name': 'Preferences', 'url': '/preference/', 'icon': 'fas fa-cog', 'dropdown': True, 'id': 'preference'
    ,'submenus': [
        {'name': 'Setting', 'url': '/preference/setting/', 'icon': 'fas fa-cog', 'id': 'preferenceSetting'},
        {'name': 'Help', 'url': '/help/', 'icon': 'fas fa-question-circle', 'id': 'preferenceHelp'},
        {'name': 'Docs', 'url': '/docs/', 'icon': 'fas fa-book', 'id': 'preferenceDocs'},
        {'name': 'Blog', 'url': '/blog/', 'icon': 'fas fa-blog', 'id': 'preferenceBlog'},
        {'name': 'Contact', 'url': '/contact/', 'icon': 'fas fa-phone', 'id': 'preferenceContact'},
        {'name': 'About', 'url': '/about/', 'icon': 'fas fa-info-circle', 'id': 'preferenceAbout'},
    ]},
]