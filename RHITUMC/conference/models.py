from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

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
    
    def __unicode__(self):
        return '%s, %s' % (self.last_name, self.first_name) 
    
    def clean(self):
        if self.is_submitting_talk:
            if self.paper_title == '':
                raise ValidationError(u'Paper Title is required if attendee is submitting a talk!')
            if self.paper_abstract == '':
                raise ValidationError(u'Paper Abstract is required if attendee is submitting a talk!')

class Conference(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField(help_text='yyyy-mm-dd')
    end_date = models.DateField(help_text='yyyy-mm-dd')
    
    participants = models.ManyToManyField(Attendee)
    
    def __unicode__(self):
        return self.name
