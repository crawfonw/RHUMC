#!/usr/bin/env python
import os
from random import choice, randint, shuffle
from datetime import datetime, timedelta, time

def purge_and_create_site_and_auth():
    from django.contrib.sites.models import Site
    from django.conf import settings

    Site.objects.all().delete()

    site = Site()
    site.id = 1
    site.domain = 'http://www.rose-hulman.edu'
    site.name = 'Undergraduate Math Conference'
    site.save()

    from django.contrib.auth.models import Group, Permission, User
    
    User.objects.all().delete()
    
    user = User.objects.create_user('nick', 'fake@email.com')
    user.first_name = 'N'
    user.last_name = 'C'
    user.is_staff = True
    user.is_superuser = True
    user.set_password('temp123')
    user.save()


def run(purge):
    
    if purge:
        print 'Resetting site and auth data'
        purge_and_create_site_and_auth()
    
    from conference.models import Conference, Page, Room, TimeSlot
    
    Conference.objects.all().delete()
    Page.objects.all().delete()
    Room.objects.all().delete()
    TimeSlot.objects.all().delete()
    
    create_conferences_schedules_and_timeslots()
    create_attendees()

def create_conferences_schedules_and_timeslots():
    from conference.models import Conference, Day, Schedule, TimeSlot
    
    now = datetime.now()
    past_conf = Conference.objects.create(name='Past Conference', start_date=now-timedelta(days=35), end_date=now-timedelta(days=30))
    curr_conf = Conference.objects.create(name='Current Conference', start_date=now, end_date=now+timedelta(days=4))
    future_conf = Conference.objects.create(name='Future Conference', start_date=now+timedelta(days=30), end_date=now+timedelta(days=35))
    
    Schedule.objects.create(conference=past_conf)
    Schedule.objects.create(conference=future_conf)
    
    s = Schedule.objects.create(conference=curr_conf)
    d1 = Day.objects.create(schedule=s, date=now)
    d2 = Day.objects.create(schedule=s, date=now+timedelta(days=1))
    d3 = Day.objects.create(schedule=s, date=now+timedelta(days=2))
    d4 = Day.objects.create(schedule=s, date=now+timedelta(days=3))
    d5 = Day.objects.create(schedule=s, date=now+timedelta(days=4))
    
    t1 = TimeSlot.objects.create(name='First Time Slot', start_time=time(hour=12), end_time=time(hour=13))
    t1.day.add(d1,d2,d3,d4,d5)
    t1.save()
    
    t2 = TimeSlot.objects.create(name='Second Time Slot', start_time=time(hour=13, minute=30), end_time=time(hour=14, minute=30))
    t2.day.add(d1,d2,d3,d4,d5)
    t2.save()
    
    t3 = TimeSlot.objects.create(name='Third Time Slot', start_time=time(hour=10), end_time=time(hour=12))
    t3.day.add(d5)
    t3.save()

def create_attendees(n=30):
    from django.contrib.auth.models import User
    from conference.models import Attendee, Conference
    
    n_owner = User.objects.get(username='nick')
    conferences = Conference.objects.all()
    schools = ['Carnegie Mellon University', 'Davidson College', 'Indiana University', 'Kenyon College', 'Michigan State University', 'Purdue University', 'Rose-Hulman Institute of Technology', 'Stanford', 'University of Louisville']
    first_names = ['Alan', 'Alexa', 'Alexandra', 'Alfonso', 'Alice', 'Alvin', 'Amaya', 'Amber', 'Amy', 'Avram', 'Barclay', 'Boris', 'Brian', 'Brock', 'Cailin', 'Cameran', 'Cameron', 'Carl', 'Chanda', 'Channing', 'Chester', 'Claire', 'Clementine', 'Dai', 'Davis', 'Davis', 'Demetrius', 'Driscoll', 'Dustin', 'Erica', 'Faith', 'Fiona', 'Frances', 'Gary', 'Gary', 'Genevieve', 'George', 'Hadassah', 'Hadassah', 'Hayden', 'Idola', 'Idona', 'Illana', 'Ivy', 'Jackson', 'Jacob', 'Joelle', 'Jolie', 'Kaye', 'Kelsie', 'Lance', 'Lareina', 'Lawrence', 'Lesley', 'Levi', 'Lewis', 'Lyle', 'Madaline', 'Mallory', 'Mannix', 'Mara', 'Marsden', 'Matthew', 'Maxine', 'Meredith', 'Michelle', 'Naomi', 'Nina', 'Nomlanga', 'Norman', 'Pamela', 'Piper', 'Quin', 'Quinn', 'Quyn', 'Rachel', 'Rashad', 'Rebekah', 'Reece', 'Regina', 'Rhea', 'Robert', 'Rose', 'Russell', 'Sacha', 'Sage', 'Shannon', 'Shea', 'Shelby', 'Simon', 'Sylvia', 'Tatum', 'Ulla', 'Vance', 'Willa', 'Winter', 'Xerxes', 'Yael', 'Yuli', 'Zorita']
    last_names = ['Adkins', 'Arnold', 'Ashley', 'Ballard', 'Barry', 'Berger', 'Blackburn', 'Blackwell', 'Blake', 'Bridges', 'Burch', 'Burgess', 'Cameron', 'Cardenas', 'Carrillo', 'Cash', 'Castaneda', 'Christian', 'Cleveland', 'Copeland', 'Cotton', 'Crawford', 'Cunningham', 'Curry', 'Dale', 'Dalton', 'Davidson', 'Dillard', 'Evans', 'Figueroa', 'Fleming', 'Flores', 'Foley', 'Freeman', 'Galloway', 'Gibbs', 'Gilbert', 'Gonzales', 'Gray', 'Hansen', 'Harding', 'Higgins', 'Hobbs', 'Hodges', 'Hunter', 'Irwin', 'Joyce', 'Kent', 'Kramer', 'Lancaster', 'Lang', 'Lindsey', 'Little', 'Lynch', 'Marks', 'Marsh', 'Mathis', 'Maynard', 'Mccall', 'Mcclure', 'Merrill', 'Merritt', 'Middleton', 'Miles', 'Mitchell', 'Morrison', 'Nieves', 'Obrien', 'Petersen', 'Pittman', 'Powell', 'Pugh', 'Ramos', 'Richmond', 'Rivas', 'Rodriquez', 'Rosario', 'Salinas', 'Sampson', 'Sandoval', 'Scott', 'Shields', 'Spears', 'Stark', 'Terrell', 'Townsend', 'Tran', 'Tucker', 'Valenzuela', 'Vargas', 'Wade', 'Walker', 'Walton', 'Warren', 'Wells', 'Whitney', 'Wolf', 'Wong', 'Wright', 'Yang']
    for i in range(n):
        f = choice(first_names)
        l = choice(last_names)
        a = Attendee.objects.create(owner=n_owner, conference=conferences[i % len(conferences)], email='%s@%s.com' % (f, l), \
                                    first_name = f, last_name=l, school=choice(schools), attendee_type=choice(['Student', 'Faculty']))
        if randint(0,n/10) == 0:
            a.is_submitting_talk = True
            a.paper_title = 'Lorem Ipsum'
            a.paper_abstract = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus luctus posuere egestas. Integer posuere nisl sit amet ipsum faucibus sollicitudin. Maecenas est mi, tempor sit amet feugiat adipiscing, porta quis sapien. Vivamus sit amet ultricies orci. Ut tristique eleifend sem. Sed porttitor, augue auctor fringilla mattis, tellus enim tristique tellus, eleifend scelerisque nisi urna elementum ipsum. In hac habitasse platea dictumst. Vivamus at ultricies neque.'
            if randint(0,1) == 0:
                a.is_submitted_for_best_of_competition = True
        if randint(0,2) == 0:
            a.requires_housing = True
        a.save()
    
if __name__ == '__main__':
    import argparse, os
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store_true', help='Reset site settings and auth system.')
    args = parser.parse_args()
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RHITUMC.settings")
    run(args.p)