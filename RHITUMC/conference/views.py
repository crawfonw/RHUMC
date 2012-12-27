# TODO: Clean up imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import apnumber
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.template.defaultfilters import date, time
from django.template.loader import render_to_string
from django.middleware import csrf
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile 
from django.db.models import Q

def index(request):
    return render_to_response('conference/index.html',
                              {'page_title': 'Item Drawer',
                               },
                               RequestContext(request))
