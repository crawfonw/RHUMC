from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('conference.views',
    url(r'^$', index, name='conference-index'),
    url(r'^register/$', register_attendee, name='conference-registration'),
    url(r'^page/(?P<page_id>[\d]+)/$', page, name='conference-page'),
    
    url(r'^portal/$', admin_portal, name='admin-portal'),
    url(r'^portal/badges/$', generate_badges, name='badges-generator'),
    url(r'^portal/emailer/$', attendee_emailer, name='attendee-emailer'),
    url(r'^portal/program/$', program, name='conference-program'),
    url(r'^portal/scheduler/$', generate_schedule, name='schedule-generator'),
)
