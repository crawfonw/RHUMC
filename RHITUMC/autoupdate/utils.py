'''
Created on Jan 10, 2014

@author: nick
'''

def get_all_modules():
    modules = get_nondjango_installed_apps()
    modules.append(get_instance_name_from_settings())
    return modules

def get_instance_name_from_settings():
    from django.conf import settings
    return settings.WSGI_APPLICATION.split('.')[0]

def get_nondjango_installed_apps():
    from django.conf import settings
    apps = []
    for app in settings.INSTALLED_APPS:
        if 'django' not in app:
            apps.append(app)
    return apps