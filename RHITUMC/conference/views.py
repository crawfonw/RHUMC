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

from django.core.mail import EmailMultiAlternatives, send_mass_mail

from datetime import datetime

from forms import AttendeeEmailerForm, AttendeeForm, LaTeXForm
from models import Attendee, Conference, Contactee, Day, Page, Session, SpecialSession, Track, TimeSlot

from LaTeX import LaTeXFile

FORWARD_REGISTRATIONS = True

def _get_current_conference():
    c = Conference.objects.filter(end_date__gte=datetime.now())
    if c.count() > 0:
        c = c[0]
    else:
        c = None
    return c

def _get_active_conference_hosts_emails():
    return [host.email for host in Contactee.objects.filter(active_contact=True).all()]

def _email_hosts_registration_info(attendee):
    to = _get_active_conference_hosts_emails()
    if len(to) > 0:
        subject = 'New Conference Registration'
        from_email = 'mathconf@mathconf.csse.rose-hulman.edu'
        
        text_content = attendee.all_info()
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.send()
        
def _email_attendee_registration_info(attendee):
    subject = 'Conference Registration Confirmation'
    from_email = 'mathconf@mathconf.csse.rose-hulman.edu'
    to = [attendee.email]
    
    text_content = 'Thank you for registering for our conference! Here is the information you provided for your records. If you have any questions, comments, or concerns, please see the contact information on the conference webpage. Thanks!\n\n'
    text_content += attendee.all_info()
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.send()

def generic_page(request, page_title, text, template='conference/generic-text.html'):
    return render_to_response(template,
                              {'page_title': page_title,
                               'text': text,
                               },
                               RequestContext(request))

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
    if request.method == 'POST':
        form = AttendeeEmailerForm(request.POST)
        if form.is_valid():
            conf = form.cleaned_data['conference']
            host = form.cleaned_data['host']
            email_subject = form.cleaned_data['email_subject']
            email_body = form.cleaned_data['email_body']
            
            conference_attendees = Attendee.objects.filter(conference=conf)
            
            mail_messages = []
            for attendee in conference_attendees:
                mail_messages.append((email_subject, email_body, host.email, [attendee.email]))
            send_mass_mail(mail_messages, fail_silently=False)
            messages.add_message(request, messages.SUCCESS, 'Email sent to %s attendees.' % len(mail_messages))
            
    else:
        form = AttendeeEmailerForm()
    
    return render_to_response('conference/admin-attendee-emailer.html',
                              {'page_title': 'Email Attendees',
                               'form': form,
                               },
                               RequestContext(request)) 

@login_required
def generate_schedule(request):
    #grab the schedules ordered by Tracks!
    #Obj.objects.order_by('ORDERING')
    if not (request.user.is_staff or request.user.is_superuser): 
        return HttpResponseRedirect(reverse('conference-index'))
    if request.method == 'POST':
        form = LaTeXForm(request.POST)
        if form.is_valid():
            conf = form.cleaned_data['conference']
            sessions = Session.objects.filter(day__conference=conf)
            special_sessions = SpecialSession.objects.filter(day__conference=conf)
            tracks = Track.objects.filter(conference=conf)
            time_slots = TimeSlot.objects.filter(conference=conf)
            
            l = LaTeXFile(sessions, special_sessions, time_slots, tracks)
    
            response = HttpResponse(l.generate_program(), content_type='application/x-latex')
            response['Content-Disposition'] = 'attachment; filename="program.tex"'
            return response
    else:
        form = LaTeXForm()
        
    return render_to_response('conference/program-gen.html',
                              {'page_title': 'Generate LaTeX Program',
                               'form': form,
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
            f_max_degree = form.cleaned_data['max_degree']
            
            new_attendee = Attendee.objects.create(conference=c, \
                                    email=f_email, first_name=f_first_name, last_name=f_last_name, \
                                    sex=f_sex, school=f_school, size_of_institute=f_size_of_institute, \
                                    attendee_type=f_attendee_type, year=f_year, is_submitting_talk=f_is_submitting_talk, \
                                    paper_title=f_paper_title, paper_abstract=f_paper_abstract, \
                                    is_submitted_for_best_of_competition=f_is_submitted_for_best_of_competition, \
                                    dietary_restrictions=f_dietary_restrictions, requires_housing=f_requires_housing, comments=f_comments,
                                    max_degree=f_max_degree,)
            
            if FORWARD_REGISTRATIONS:
                _email_hosts_registration_info(new_attendee)
                _email_attendee_registration_info(new_attendee)
            
            return generic_page(request, 'Registration Complete', "<b>Thanks, you are now registered for the conference. A copy of your provided information has been emailed to %s for your records. Make sure to check your junk mail folder if you don't see it. We are looking forward to having you at the conference!</b>" % new_attendee.email)
            
            #messages.add_message(request, messages.SUCCESS, '<b>Thanks, you are now registered for the %s conference!</b>' % c.format_date())
            #return HttpResponseRedirect(reverse('conference-index'))
            
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
    #WIP
    #TODO: fix/update this
    ##This can probably be removed...
    ##I think the "Program" page was intended to be general,
    ##not contain the actual conference program schedule
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