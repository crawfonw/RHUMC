from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

import datetime

class Conference(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField(help_text='yyyy-mm-dd')
    end_date = models.DateField(help_text='yyyy-mm-dd')
    
    class Meta:
        ordering = ('start_date', 'end_date',)
    
    def __unicode__(self):
        return self.name
    
    def format_date(self):
        if self.start_date.month == self.end_date.month:
            return '%s - %s' % (self.start_date.strftime('%b %d'), self.end_date.strftime('%d, %Y'))
        else:
            return '%s - %s' % ((self.start_date.strftime('%b %d'), self.end_date.strftime('%b %d, %Y')))
        
    def _is_in_past(self):
        return self.end_date < datetime.date.today()
    past_conference = property(_is_in_past)
    
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
              )
    
    YEAR = (('FR', 'FR'),
            ('SO', 'SO'),
            ('JR', 'JR'),
            ('SR', 'SR'),
            ('Other', 'Other'),
            )
    
    owner = models.ForeignKey(User) #whomever created this attendee
    conference = models.ForeignKey(Conference)
    
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    sex = models.CharField(choices=GENDER, max_length=6, blank=True)
    
    school = models.CharField(max_length=100)
    size_of_institute = models.CharField(choices=SIZE, max_length=10, blank=True)
    attendee_type = models.CharField(choices=STATUS, max_length=7)
    year = models.CharField(choices=YEAR, max_length=5, blank=True)
    
    is_submitting_talk = models.BooleanField()
    paper_title = models.CharField(max_length=100, blank=True)
    paper_abstract = models.TextField(blank=True)
    is_submitted_for_best_of_competition = models.BooleanField()
    
    dietary_restrictions = models.TextField(blank=True)
    requires_housing = models.BooleanField()
    comments = models.TextField(blank=True)
    
    class Meta:
        ordering = ('last_name', 'first_name',)
    
    def __unicode__(self):
        return '%s, %s' % (self.last_name, self.first_name) 
    
    def clean(self):
        if self.is_submitting_talk:
            if self.paper_title == '':
                raise ValidationError(u'Paper Title is required if attendee is submitting a talk!')
            if self.paper_abstract == '':
                raise ValidationError(u'Paper Abstract is required if attendee is submitting a talk!')

class Room(models.Model):
    building = models.CharField(max_length=100)
    room_number = models.CharField(max_length=100)

    class Meta:
        ordering = ('building', 'room_number',)
        unique_together = (('building', 'room_number',),)

    def __unicode__(self):
        return '%s %s' % (self.building, self.room_number)

class Schedule(models.Model):
    conference = models.ForeignKey(Conference, limit_choices_to=models.Q(end_date__gte=datetime.date.today))
    
    def __unicode__(self):
        return '%s schedule' % self.conference

class Day(models.Model):
    schedule = models.ForeignKey(Schedule)
    date = models.DateField(help_text='yyyy-mm-dd')
    
    class Meta:
        ordering = ('schedule', 'date',)
        unique_together = (('schedule', 'date',),)

    def __unicode__(self):
        return '%s during %s' % (self.date, self.schedule)
    
    def clean(self):
        if self.date > self.schedule.conference.end_date or self.date < self.schedule.conference.start_date:
            raise ValidationError(u"This day's date must be within the Schedule's conference dates.")

class TimeSlot(models.Model):
    name = models.CharField(max_length=100)
    day = models.ForeignKey(Day)
    start_time = models.TimeField(help_text='hh:mm')
    end_time = models.TimeField(help_text='hh:mm')
    
    def clean(self):
        if self.end_time < self.start_time:
            raise ValidationError(u'The end date may not be before the start date.')
        
class Session(models.Model):
    speaker = models.ForeignKey(Attendee, limit_choices_to=models.Q(conference__end_date__gte=datetime.date.today)) #is it always one person? filter attendees to just the certain conference
    room = models.ForeignKey(Room)
    time = models.ForeignKey(TimeSlot)

class Page(models.Model):
    title = models.CharField(max_length=100)
    is_link = models.BooleanField(help_text='Is this an external URL?')
    link = models.URLField(blank=True, help_text='Only for external URLs.')
    on_sidebar = models.BooleanField(help_text='Should this page show up on the main sidebar?')
    page_text = models.TextField(blank=True, help_text='For internal pages.')
    
    def __unicode__(self):
        return self.title
    
    def clean(self):
        if self.is_link and self.link == None:
            raise ValidationError(u'You must specify a URL for the indicated link.')
        
        
        
