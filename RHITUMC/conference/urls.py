from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('conference.views',
    url(r'^$', index, name='conference-index'),
)
