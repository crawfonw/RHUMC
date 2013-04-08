from django.conf.urls import patterns, include, url

from django.http import HttpResponse

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'RHITUMC.views.home', name='home'),
    url(r'^', include('conference.urls')),
    
    url(r'^favicon.ico', 'conference.views.index'),
    url(r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")),
    
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='panel-logout'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}, name='panel-login'),
    url(r'^accounts/$', 'django.views.generic.simple.redirect_to', {'url': '/'}),
    url(r'^accounts/profile/$', 'django.views.generic.simple.redirect_to', {'url': '/'}),
)
