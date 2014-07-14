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
from views import *

urlpatterns = patterns('conference.views',
    url(r'^$', index, name='conference-index'),
    url(r'^register/$', register_attendee, name='conference-registration'),
    url(r'^page/(?P<page_id>[\d]+)/$', page, name='conference-page'),
    
    url(r'^portal/$', admin_portal, name='admin-portal'),
    url(r'^portal/badges/$', generate_badges, name='badges-generator'),
    url(r'^portal/batch/$', batch_update, name='batch-updater'),
    url(r'^portal/csvdump/$', csv_dump, name='csv-dump'),
    url(r'^portal/emailer/$', attendee_emailer, name='attendee-emailer'),
    #url(r'^portal/program/$', program, name='conference-program'),
    url(r'^portal/scheduler/$', generate_schedule, name='schedule-generator'),
)
