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

from datetime import datetime

from forms import AttendeeForm
from models import Attendee, Conference, Day, Page, Session, SpecialSession, Track, TimeSlot

from LaTeX import LaTeXFile

def _get_current_conference():
    c = Conference.objects.filter(end_date__gte=datetime.now())
    if c.count() > 0:
        c = c[0]
    else:
        c = None
    return c

@login_required
def admin_portal(request):
    if not (request.user.is_staff or request.user.is_superuser): 
        return HttpResponseRedirect(reverse('conference-index'))
    return render_to_response('conference/admin-portal.html',
                              {'page_title': 'Administrative Portal',
                               },
                               RequestContext(request))

@login_required
def attendee_emailer(request):
    if not (request.user.is_staff or request.user.is_superuser): 
        return HttpResponseRedirect(reverse('conference-index'))
    c = _get_current_conference()
    if c is None:
        messages.add_message(request, messages.ERROR, 'You have no upcoming conference objects in the database. If you believe this is an error, please double check the Management System.')
    if request.method == 'POST':
        #TODO: implement
        pass
    else:
        attendee_groups = [Attendee.objects.filter(conference=conf) for conf in c]
        print attendee_groups, [len(g) for g in attendee_groups]
    
    return render_to_response('conference/admin-attendee-emailer.html',
                              {'page_title': 'Email Attendees',
                               'attendee_groups': attendee_groups,
                               },
                               RequestContext(request)) 

@login_required
def generate_schedule(request):
    #grab the schedules ordered by Tracks!
    #Obj.objects.order_by('ORDERING')
    if not (request.user.is_staff or request.user.is_superuser): 
        return HttpResponseRedirect(reverse('conference-index'))
    c = _get_current_conference()
    if c is None:
        return generic_page(request, 'No Conference', 'No conferences avaliable.')
    sessions = Session.objects.filter(day__conference=c)
    special_sessions = SpecialSession.objects.filter(day__conference=c)
    tracks = Track.objects.filter(conference=c)
    time_slots = TimeSlot.objects.filter(conference=c)
    
    print 'Sessions: %s\nSpecial: %s\nTracks: %s\nTime Slots: %s\n' % (sessions, special_sessions, tracks, time_slots)
    
    #Build LaTeX file
    l = LaTeXFile(sessions, special_sessions, time_slots, tracks)
    print l.build_table_of_contents()
    print
    print l.build_special_sessions()
    print
    
    return generic_page(request, 'DNE', 'Not implemented yet.')

def generic_page(request, page_title, text):
    return render_to_response('conference/generic-text.html',
                              {'page_title': page_title,
                               'text': text,
                               },
                               RequestContext(request))

def index(request):
    return render_to_response('conference/index.html',
                              {'page_title': 'Rose-Hulman Undergraduate Math Conference',
                               },
                               RequestContext(request))

def register_attendee(request):    
    c = _get_current_conference()
    if c is None:
        text = 'We are sorry, but currently there is no conference scheduled. Please check back later.'
        return generic_page(request, 'Registration', text)
    if request.method == 'POST':
        form = AttendeeForm(request.POST)
        if form.is_valid():
            f_email = form.cleaned_data['email']
            f_first_name = form.cleaned_data['first_name']
            f_last_name = form.cleaned_data['last_name']
            f_sex = form.cleaned_data['sex']
            f_school = form.cleaned_data['school']
            f_size_of_institute = form.cleaned_data['size_of_institute']
            f_attendee_type = form.cleaned_data['attendee_type']
            f_year = form.cleaned_data['year']
            f_is_submitting_talk = form.cleaned_data['is_submitting_talk']
            f_paper_title = form.cleaned_data['paper_title']
            f_paper_abstract = form.cleaned_data['paper_abstract']
            f_is_submitted_for_best_of_competition = form.cleaned_data['is_submitted_for_best_of_competition']
            f_dietary_restrictions = form.cleaned_data['dietary_restrictions']
            f_requires_housing = form.cleaned_data['requires_housing']
            f_comments = form.cleaned_data['comments']
            
            Attendee.objects.create(conference=c, \
                                    email=f_email, first_name=f_first_name, last_name=f_last_name, \
                                    sex=f_sex, school=f_school, size_of_institute=f_size_of_institute, \
                                    attendee_type=f_attendee_type, year=f_year, is_submitting_talk=f_is_submitting_talk, \
                                    paper_title=f_paper_title, paper_abstract=f_paper_abstract, \
                                    is_submitted_for_best_of_competition=f_is_submitted_for_best_of_competition, \
                                    dietary_restrictions=f_dietary_restrictions, requires_housing=f_requires_housing, comments=f_comments,
                                    )
            messages.add_message(request, messages.SUCCESS, '<b>Thanks, you are now registered for the %s conference!</b>' % c.format_date())
            return HttpResponseRedirect(reverse('conference-index'))
            
    else:
        form = AttendeeForm()
    return render_to_response('conference/registration-form.html',
                              {'page_title': 'Registration',
                               'form': form,
                               },
                               RequestContext(request))

def page(request, page_id):
    p = get_object_or_404(Page, pk=page_id)
    return generic_page(request, p.title, p.page_text)

def program(request):
    #TODO: fix/update this
    c = _get_current_conference()
    if c is not None:
        if c.show_program:
            current_schedule = Track.objects.filter(conference=c)
            days = Day.objects.filter(schedule=current_schedule)
            time_slots = TimeSlot.objects.filter(schedule=current_schedule)
            sessions = Session.objects.filter(day__in=days, time__in=time_slots)
            
            if days.count() == 0  or time_slots.count() == 0:
                text = 'The schedule of times have not been set for this conference yet. Please check back later.'
                return generic_page(request, 'Program', text)
            
            days_and_timeslots = []
            for day in days:
                d = [day, []]
                for session in sessions:
                    if session.day == day and session.time not in d[1]:
                        d[1].append(session.time)
                days_and_timeslots.append(d)
            
            return render_to_response('conference/program.html',
                                      {'page_title': 'Program',
                                       'sessions': sessions,
                                       'days_and_timeslots': days_and_timeslots,
                                       },
                                       RequestContext(request))
        else:
            text = 'The schedule of times have not been set for this conference yet. Please check back later.'
            return generic_page(request, 'Program', text)
    else:
        text = 'We are sorry, but currently there is no conference scheduled. Please check back later.'
        return generic_page(request, 'Program', text)