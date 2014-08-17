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

from django.conf.urls import patterns, include, url
from django.http import HttpResponse
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('conference.urls')),
    
    url(r'^favicon.ico', 'conference.views.index'),
    url(r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")),
    
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^portal/admin/', include(admin.site.urls), name='admin'),
    
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='panel-logout'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}, name='panel-login'),
    url(r'^accounts/$', RedirectView.as_view(url='/')),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/')),
    #url(r'^accounts/$', 'django.views.generic.simple.redirect_to', {'url': '/'}),
    #url(r'^accounts/profile/$', 'django.views.generic.simple.redirect_to', {'url': '/'}),
)
