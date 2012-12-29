from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('conference.views',
    url(r'^$', index, name='conference-index'),
    url(r'^register/$', register_attendee, name='conference-registration'),
    url(r'^program/$', program, name='conference-program'),
    url(r'^page/(?P<page_id>[\d]+)/$', page, name='conference-page')
)
