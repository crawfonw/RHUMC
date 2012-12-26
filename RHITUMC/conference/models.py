from django.contrib.auth.models import User, UserManager
from django.db import models

class UMCUser(User):
    school = models.CharField(max_length=100)
    
    objects = UserManager()

class Conference(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField(help_text='yyyy-mm-dd')
    end_date = models.DateField(help_text='yyyy-mm-dd')
    
    participants = models.ManyToManyField(UMCUser)
    
    def __unicode__(self):
        return self.name
