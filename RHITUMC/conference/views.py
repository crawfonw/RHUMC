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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.models import model_to_dict
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.core.mail import EmailMultiAlternatives, send_mass_mail

import csv
from datetime import datetime
import os
from shutil import rmtree
import StringIO

from forms import AttendeeEmailerForm, AttendeeForm, BatchUpdateForm, CSVDumpForm, LaTeXBadgesForm, LaTeXProgramForm
from models import Attendee, Conference, Contactee, Day, Page, Session, SpecialSession, Track, TimeSlot

from LaTeX import LaTeXBadges, LaTeXProgram
from utils import clean_unicode_for_dict, compile_latex_to_pdf, escape_latex_for_dict, str_to_file, zip_files_together

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
        msg = EmailMultiAlternatives(subject, text_content, from_email, to, headers = {'Reply-To': attendee.email})
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
                              {'title': 'Administrative Portal',
                               'atportal': True,
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
                              {'title': 'Email Attendees',
                               'form': form,
                               },
                               RequestContext(request))
    
@login_required
def csv_dump(request):
    if not (request.user.is_staff or request.user.is_superuser): 
        return HttpResponseRedirect(reverse('conference-index'))
    if request.method == 'POST':
        form = CSVDumpForm(request.POST)
        if form.is_valid():
            conf = form.cleaned_data['conference']
            target_fields = map(lambda x: x.strip(), form.cleaned_data['csv_fields'].split(','))
            
            #conference_attendees = Attendee.objects.filter(conference=conf).iterator() #.iterator() if this gets huge (but it shouldn't...)
            conference_attendees = Attendee.objects.filter(conference=conf)
            model = conference_attendees.model
            model_fields = [x.name for x in model._meta.fields]
            
            valid = True
            headers = []
            error_headers = []
            for field in target_fields:
                if field in model_fields:
                    headers.append(field)
                else:
                    valid = False
                    error_headers.append(field)
            
            if valid:
                output = StringIO.StringIO()
                writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
                writer.writerow(headers)
                
                for obj in conference_attendees:
                    row = []
                    for field in headers:
                        val = getattr(obj, field)
                        if callable(val):
                            val = val()
                        if type(val) == unicode:
                            val = val.encode('utf-8')
                        row.append(val)
                    writer.writerow(row)
                    print row
                
                response = HttpResponse(output.getvalue(), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="%s.csv"' % conf.name
                output.close()
                
                return response
            else:
                form._errors['csv_fields'] = form.error_class([u'Field error - field%s "%s" not present in %s model.' % ('s' if len(error_headers) > 1 else '', ', '.join(error_headers), model._meta.model_name)])
    else:
        form = CSVDumpForm()
        form.fields['csv_fields'].initial = ','.join([x.name for x in Attendee._meta.fields])
        
    return render_to_response('conference/csv-dump.html',
                              {'title': 'Attendee Data Dumper',
                               'form' : form,
                                },
                              RequestContext(request))

@login_required
def generate_schedule(request):
    #grab the schedules ordered by Tracks!
    #Obj.objects.order_by('ORDERING')
    if not (request.user.is_staff or request.user.is_superuser): 
        return HttpResponseRedirect(reverse('conference-index'))
    if request.method == 'POST':
        form = LaTeXProgramForm(request.POST)
        if form.is_valid():
            try:
                action = form.cleaned_data['action']
            except:
                action = None
            conf = form.cleaned_data['conference']
            file_name = form.cleaned_data['file_name']
            opts = dict({('display_titles', form.cleaned_data['display_titles']), \
                         ('display_schools', form.cleaned_data['display_schools']), \
                         ('squish', form.cleaned_data['squish'])})
            sessions = [model_to_dict(s) for s in Session.objects.filter(day__conference=conf)]
            special_sessions = SpecialSession.objects.filter(day__conference=conf)
            tracks = Track.objects.filter(conference=conf)
            time_slots = TimeSlot.objects.filter(conference=conf)
            days = Day.objects.filter(conference=conf)
            
            for session in sessions:
                session['chair'] = Attendee.objects.get(id=session['chair'])
                session['speakers'] = [model_to_dict(a) for a in Attendee.objects.filter(id__in=session['speakers'])]
                session['track'] = Track.objects.get(id=session['track'])
                session['day'] = Day.objects.get(id=session['day'])
                session['time'] = TimeSlot.objects.get(id=session['time'])
            
            if form.cleaned_data['convert_unicode']:
                for session in sessions:
                    session['speakers'] = map(clean_unicode_for_dict, session['speakers'])
            
            if form.cleaned_data['escape_latex']:
                for session in sessions:
                    session['speakers'] = map(escape_latex_for_dict, session['speakers'])
            try:
                l = LaTeXProgram(opts, sessions, special_sessions, time_slots, tracks, days).generate_program()
            except:
                l = None
            
            if l is None:
                form._errors[NON_FIELD_ERRORS] = form.error_class([u'An unexpected error occurred whilst generating the LaTeX file. This is most likely due to bad data. Try again and if the problem persists then verify your data in the Management System.'])
            else:
                if action is None or action == 'tex':
                    response = HttpResponse(l, content_type='application/x-latex')
                    response['Content-Disposition'] = 'attachment; filename="%s.tex"' % file_name
                elif action == 'pdf':
                    try:
                        fd, path = compile_latex_to_pdf(l, file_name)
                    except:
                        raise Http404('Error compiling PDF file from LaTeX code.')
                    try:
                        pdf = os.fdopen(fd, 'rb')
                        pdf_out = pdf.read()
                        pdf.close()
                    except OSError:
                        raise Http404('Error compiling PDF file from LaTeX code.')
                    
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % file_name
                    response.write(pdf_out)
                    
                    rmtree(os.path.split(path)[0])
                elif action == 'all':
                    try:
                        tex_fd, tex_path = str_to_file(l, file_name, 'tex')
                        tex = os.fdopen(tex_fd, 'rb')
                        tex_out = tex.read()
                        tex.close()
                    except OSError:
                        raise Http404('Error writing LaTeX code to file.')
                    
                    try:
                        pdf_fd, pdf_path = compile_latex_to_pdf(l, file_name)
                        pdf = os.fdopen(pdf_fd, 'rb')
                        pdf_out = pdf.read()
                        pdf.close()
                    except OSError:
                        raise Http404('Error compiling PDF file from LaTeX code.')
                    
                    try:
                        zip_fd, zip_path = zip_files_together([pdf_path, tex_path], file_name)
                        zip = os.fdopen(zip_fd, 'rb')
                        zip_out = zip.read()
                        zip.close()
                    except OSError:
                        raise Http404('Error zipping .pdf and .tex files together.')
                    
                    response = HttpResponse(content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename="%s.zip"' % file_name
                    response.write(zip_out)
                    
                return response
    else:
        form = LaTeXProgramForm()
        
    return render_to_response('conference/program-gen.html',
                              {'title': 'Generate LaTeX Program',
                               'form': form,
                               },
                               RequestContext(request)) 
@login_required
def generate_badges(request):
    if not (request.user.is_staff or request.user.is_superuser): 
        return HttpResponseRedirect(reverse('conference-index'))
    if request.method == 'POST':
        form = LaTeXBadgesForm(request.POST)
        if form.is_valid():
            conf = form.cleaned_data['conference']
            width = form.cleaned_data['width']
            height = form.cleaned_data['height']
            opts = dict({('width', width), ('height', height)})
            attendees = Attendee.objects.filter(conference=conf)
            
            l = LaTeXBadges(opts, attendees)
    
            response = HttpResponse(l.generate_badges(), content_type='application/x-latex')
            response['Content-Disposition'] = 'attachment; filename="badges.tex"'
            return response
    else:
        form = LaTeXBadgesForm()
        
    return render_to_response('conference/badges-gen.html',
                              {'title': 'Generate LaTeX Badges',
                               'form': form,
                               },
                               RequestContext(request))

@login_required
def batch_update(request):
    if not (request.user.is_staff or request.user.is_superuser): 
        return HttpResponseRedirect(reverse('conference-index'))
    if request.method == 'POST':
        form = BatchUpdateForm(request.POST)
        if form.is_valid():
            selection = form.cleaned_data['selection']
            replace = form.cleaned_data['replace']
            
            attendees_to_update = Attendee.objects.filter(school=selection)
            for attendee in attendees_to_update:
                attendee.school = replace
                attendee.save()
            messages.add_message(request, messages.SUCCESS, 'All instances of "%s" have been replaced with "%s".' % (selection, replace))
            return HttpResponseRedirect(reverse('batch-updater'))
    else:
        schools = []
        school_tuples = []
        for s in Attendee.objects.all().values('school'):
            if s['school'] not in schools:
                schools.append(s['school'])
                school_tuples.append((s['school'], s['school']))
        form = BatchUpdateForm(initial={'selection': school_tuples})
        
    return render_to_response('conference/batch-updater.html',
                              {'title': 'Batch Updater',
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
    elif not c.registration_open:
        text = 'We are sorry, but registration has closed for this conference.'
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
                                    max_degree=f_max_degree, has_been_paired_for_housing=False)
            
            if FORWARD_REGISTRATIONS and not settings.DEBUG:
                _email_hosts_registration_info(new_attendee)
                _email_attendee_registration_info(new_attendee)
            
            return generic_page(request, 'Registration Complete', "<b>Thanks, you are now registered for the conference. A copy of your provided information has been emailed to %s for your records. Make sure to check your junk mail folder if you don't see it. We are looking forward to having you at the conference!</b>" % new_attendee.email)
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
