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

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django import get_version
if get_version() < '1.6':
    from django.contrib.localflavor.us.models import PhoneNumberField
else:
    from localflavor.us.models import PhoneNumberField

import datetime

class Conference(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField(help_text='yyyy-mm-dd')
    end_date = models.DateField(help_text='yyyy-mm-dd')
    registration_open = models.BooleanField(default=True)
    show_program = models.BooleanField(help_text='WORK IN PROGRESS: Check if you want to show a version of the Conference Program directly on the website')
    
    class Meta:
        ordering = ('start_date', 'end_date',)
    
    def __unicode__(self):
        return unicode(self.name)
    
    def format_date(self):
        if self.start_date.month == self.end_date.month:
            return '%s - %s' % (self.start_date.strftime('%b %d'), self.end_date.strftime('%d, %Y'))
        else:
            return '%s - %s' % ((self.start_date.strftime('%b %d'), self.end_date.strftime('%b %d, %Y')))
        
    def past_conference(self):
        return self.end_date < datetime.date.today()
    past_conference.boolean = True
    
    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(u'The end date may not be before the start date.')

class Attendee(models.Model):
    ETHNICITY = (('American Indian or Alaska Native', 'American Indian or Alaska Native'),
                 ('Asian', 'Asian'),
                 ('Black or African American', 'Black or African American'),
                 ('Hispanic or Latino', 'Hispanic or Latino'),
                 ('Native Hawaiian or Other Pacific Islander', 'Native Hawaiian or Other Pacific Islander'),
                 ('White', 'White'),
                 ('Other', 'Other'),
                 )
    
    GENDER = (('Female', 'Female'),
              ('Male', 'Male'),
              )
    
    SIZE = (('<2000', '<2000'),
            ('2000-15000', '2000-15000'),
            ('15000+', '15000+'),
            )
    
    STATUS = (('Student', 'Student'),
              ('Faculty', 'Faculty'),
              ('Other', 'Other'),
              )
    
    YEAR = (('FR', 'FR'),
            ('SO', 'SO'),
            ('JR', 'JR'),
            ('SR', 'SR'),
            ('Other', 'Other'),
            )
    
    DEG = (("Bachelor's", "Bachelor's"),
           ("Master's", "Master's"),
           ('Doctorate', 'Doctorate'),)
    
    conference = models.ForeignKey(Conference)
    
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    sex = models.CharField(choices=GENDER, max_length=6, blank=True)
    
    school = models.CharField(max_length=100)
    size_of_institute = models.CharField(choices=SIZE, max_length=10, blank=True)
    attendee_type = models.CharField(choices=STATUS, max_length=7)
    year = models.CharField(choices=YEAR, max_length=5, blank=True)
    max_degree = models.CharField(choices=DEG, max_length=10, blank=True)
    
    is_submitting_talk = models.BooleanField()
    paper_title = models.CharField(max_length=100, blank=True)
    paper_abstract = models.TextField(blank=True)
    is_submitted_for_best_of_competition = models.BooleanField()
    
    dietary_restrictions = models.TextField(blank=True)
    requires_housing = models.BooleanField()
    has_been_paired_for_housing = models.BooleanField() 
    comments = models.TextField(blank=True)
    
    class Meta:
        ordering = ('last_name', 'first_name',)
    
    def __unicode__(self):
        return u'%s, %s' % (self.last_name, self.first_name)
    
    def clean(self):
        if self.is_submitting_talk:
            if self.paper_title == '':
                raise ValidationError(u'Paper Title is required if attendee is submitting a talk!')
            if self.paper_abstract == '':
                raise ValidationError(u'Paper Abstract is required if attendee is submitting a talk!')
            
    def all_info(self):
        info = 'Registration for: %s\n\nName: %s\nEmail: %s\nType: %s\nSchool: %s\n\n' % (self.conference, str(self), self.email, self.attendee_type, self.school)
        if self.year != '':
            info += 'Year in School: %s\n' % self.year
        if self.size_of_institute != '':
            info += 'Size of Institute: %s\n' % self.size_of_institute
        if self.max_degree != '':
            info += 'Max Math Degree at Institute: %s\n\n' % self.max_degree
        if self.is_submitting_talk:
            info += 'Paper submission info:\n\nTitle: %s\nAbstract:\n%s\n\n' % (self.paper_title, self.paper_abstract)
            if self.is_submitted_for_best_of_competition:
                info += 'To be considered for best of competition.\n\n'
        else:
            info += 'Not submitting a talk.\n\n'
        if self.sex != '':
            info += 'Sex: %s\n\n' % self.sex
        if self.requires_housing:
            info += 'Requires housing.\n\n'
        else:
            info += 'Does not need housing.\n\n'
        if self.dietary_restrictions != '':
            info += 'Dietary restrictions:\n%s\n\n' % self.dietary_restrictions
        if self.comments != '':
            info += 'Additional comments:\n%s\n' % self.comments
        return info
    
    def assigned_to_session(self):
        return Session.objects.filter(speakers__id__exact=self.id).count() > 0
    assigned_to_session.boolean = True

class Room(models.Model):
    building = models.CharField(max_length=100)
    room_number = models.CharField(max_length=100)

    class Meta:
        ordering = ('building', 'room_number',)
        unique_together = (('building', 'room_number',),)

    def __unicode__(self):
        return u'%s %s' % (self.building, self.room_number)

class Track(models.Model):
    conference = models.ForeignKey(Conference, limit_choices_to=models.Q(end_date__gte=datetime.date.today))
    name = models.CharField(max_length=100, help_text='Eg.: "Track A"')
    room = models.ForeignKey(Room)
    
    def __unicode__(self):
        return u'%s' % self.name

class Day(models.Model):
    conference = models.ForeignKey(Conference, limit_choices_to=models.Q(end_date__gte=datetime.date.today))
    date = models.DateField(help_text='yyyy-mm-dd')
    
    class Meta:
        ordering = ('date',)

    def __unicode__(self):
        return u'%s' % datetime.date.strftime(self.date, '%A %m/%d/%Y')
    
    def clean(self):
        if self.date > self.conference.end_date or self.date < self.conference.start_date:
            raise ValidationError(u"This day's date must be within the Conference dates.")

class TimeSlot(models.Model):
    #TODO: remove conference reference or change unique_together
    conference = models.ForeignKey(Conference, limit_choices_to=models.Q(end_date__gte=datetime.date.today))
    start_time = models.TimeField(help_text='hh:mm (input in 24-hour format)')
    end_time = models.TimeField(help_text='hh:mm (input in 24-hour format)')
    
    class Meta:
        ordering = ('start_time', 'end_time',)
        unique_together = (('start_time', 'end_time',),)
    
    def __unicode__(self):
        return u'%s - %s' % (datetime.time.strftime(self.start_time, '%I:%M %p'), datetime.time.strftime(self.end_time, '%I:%M %p'))
    
    def clean(self):
        if self.end_time < self.start_time:
            raise ValidationError(u'The end time may not be before the start time.')
        if self.start_time == self.end_time:
            raise ValidationError(u'The start and end times may not be the same.')
        
class Session(models.Model):
    chair = models.ForeignKey(Attendee, limit_choices_to=models.Q(conference__end_date__gte=datetime.date.today), related_name='chair')
    speakers = models.ManyToManyField(Attendee, limit_choices_to=(models.Q(conference__end_date__gte=datetime.date.today) \
                                                                    & models.Q(is_submitting_talk=True)), related_name='speakers') #is it always one person? filter attendees to just the certain conference
    track = models.ForeignKey(Track, limit_choices_to=models.Q(conference__end_date__gte=datetime.date.today))
    time = models.ForeignKey(TimeSlot)
    day = models.ForeignKey(Day, limit_choices_to=models.Q(date__gte=datetime.date.today))
    
    class Meta:
        ordering = ('day', 'time', 'track',)
    
    def __unicode__(self):
        return u'Speakers: %s' % '; '.join([unicode(x) for x in self.speakers.all()])
    
class SpecialSession(models.Model):
    speaker = models.CharField(max_length=100)
    long_title = models.CharField(max_length=100, help_text='Eg.: CEO of Metron Scientific Solutions.')
    short_title = models.CharField(max_length=100, blank=True, help_text='Eg.: Metron.')
    short_description = models.CharField(max_length=100, help_text='To appear in the program index. Eg. Planery Talk.')
    long_description = models.TextField(blank=True, help_text='To appear on a dedicated page of the program; extensive description of the individual, etc.')
    
    room = models.ForeignKey(Room)
    time = models.ForeignKey(TimeSlot)
    day = models.ForeignKey(Day, limit_choices_to=models.Q(date__gte=datetime.date.today))
    
    has_page_in_program = models.BooleanField(help_text='Check if you want this to have an extended page in the program. Eg. for a Plenary Talk. Leave unchecked if you just want the information to appear in the program index.')
    
    def __unicode__(self):
        return u'Special Session: %s' % self.speaker

class Page(models.Model):
    title = models.CharField(max_length=100)
    is_link = models.BooleanField(help_text='Is this an external URL?')
    link = models.URLField(blank=True, help_text='Only for external URLs.')
    on_sidebar = models.BooleanField(help_text='Should this page show up on the main sidebar?')
    page_text = models.TextField(blank=True, help_text='For internal pages.')
    
    def __unicode__(self):
        return unicode(self.title)
    
    def clean(self):
        if self.is_link and self.link == None:
            raise ValidationError(u'You must specify a URL for the indicated link.')
        
class Contactee(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField()
    active_contact = models.BooleanField()
    
    class Meta:
        ordering = ('name',)
        
    def __unicode__(self):
        return unicode(self.name)
        
