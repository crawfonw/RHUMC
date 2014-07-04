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

#Based on filters in Django docs
#https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter

import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

from models import Session

class AttendeeAssignedToSessionFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('assigned to session')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'in_session'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('Y', _('assigned')),
            ('N', _('not assigned')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'Y':
            return queryset.filter(id__in=Session.speakers.through.objects.all().values('attendee_id'))
        if self.value() == 'N':
            return queryset.exclude(id__in=Session.speakers.through.objects.all().values('attendee_id'))
        
class PastConferenceFilter(SimpleListFilter):
    title = _('past conference')
    parameter_name = 'past'

    def lookups(self, request, model_admin):
        return (
            ('Y', _('Past')),
            ('N', _('Current or future')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Y':
            return queryset.filter(end_date__lt=datetime.date.today())
        if self.value() == 'N':
            return queryset.filter(end_date__gte=datetime.date.today())