"""
    Conference scheduling software for undergraduate institutions.
    Created specifically for the Mathematics department of the
    Rose-Hulman Institute of Technology (http://www.rose-hulman.edu/math.aspx).
    
    Copyright (C) 2013-2014  Nick Crawford <crawfonw -at- gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

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