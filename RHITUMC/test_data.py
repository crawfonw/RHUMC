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
    
    from conference.models import Conference, Contactee, Page, Room, TimeSlot
    
    Conference.objects.all().delete()
    Contactee.objects.all().delete()
    Page.objects.all().delete()
    Room.objects.all().delete()
    TimeSlot.objects.all().delete()
    
    create_conferences_schedules_and_timeslots()
    create_attendees()
    create_rooms()
    create_sessions()
    create_pages()
    create_contacts()

def create_conferences_schedules_and_timeslots():
    from conference.models import Conference, Day, Schedule, TimeSlot
    
    now = datetime.now()
    past_conf = Conference.objects.create(name='Past Conference', start_date=now-timedelta(days=35), end_date=now-timedelta(days=30), registration_open=False)
    curr_conf = Conference.objects.create(name='Current Conference', start_date=now, end_date=now+timedelta(days=4), registration_open=True)
    future_conf = Conference.objects.create(name='Future Conference', start_date=now+timedelta(days=30), end_date=now+timedelta(days=35), registration_open=False)
    
    Schedule.objects.create(conference=past_conf)
    Schedule.objects.create(conference=future_conf)
    
    s = Schedule.objects.create(conference=curr_conf)
    d1 = Day.objects.create(schedule=s, date=now)
    d2 = Day.objects.create(schedule=s, date=now+timedelta(days=1))
    d3 = Day.objects.create(schedule=s, date=now+timedelta(days=2))
    d4 = Day.objects.create(schedule=s, date=now+timedelta(days=3))
    d5 = Day.objects.create(schedule=s, date=now+timedelta(days=4))
    
    TimeSlot.objects.create(name='First Time Slot', schedule=s, start_time=time(hour=12), end_time=time(hour=13))
    TimeSlot.objects.create(name='Second Time Slot', schedule=s, start_time=time(hour=13, minute=30), end_time=time(hour=14, minute=30))
    TimeSlot.objects.create(name='Third Time Slot', schedule=s, start_time=time(hour=10), end_time=time(hour=12))
    
def create_pages():
    from conference.models import Page
    
    Page.objects.create(title='Call For Papers', on_sidebar=True, page_text='The Rose-Hulman conference has from its inception been focused on undergraduates presenting their mathematical findings.  Topics across the mathematical landscape are encouraged and supported, and we aim to provide a pleasant atmosphere in which students can initiate their foray into mathematical presentation.  All talks except for the plenaries are presented by undergraduates, for undergraduates, and to undergraduates. Each session is chaired by an undergraduate. <ul> <li> Each talk receives 15 minutes and is part of a session of  \tthree talks. </li> <li> Talks can be submitted to the <i>Best Talk of 2013</i> competition. </li> <li> Talks are given in parallel sessions throughout the conference.</li> </ul>All speakers must register for the conference to give a talk, and talks are submitted on the <a href="register.shtml">registration page</a>. Speakers  may want to see some <u><a href="speakerGuidelines.shtml">guidelines</a></u>.')
    Page.objects.create(title='Accomodations', on_sidebar=True, page_text='The conference hotel is the <u><a href="http://www.qualityinn.com/hotel-terre_haute-indiana-IN352">Quality Inn of Terre Haute</a></u>. Our goal is to pay for accomodations for registered undergraduate participants (non-Rose students) on the evening of Friday, 4/19/2013. We currently have 20 rooms reserved to house the first 40 registered particpants.  These rooms are offered on a <i>first come </i> basis, and registering early is the best way to ensure that we will cover housing costs. <p> To Make Reservations: </p><ul> <li> Register for the conference on our <u><a href="register.shtml">registration page</a></u>. </li><li> Make sure to note during the registration that you are requesting housing  \t(this is the default). </li> <li> If you have a preference of a roomate, please include this information as you register. </li> <li> We will make reservations for you, so all you have to do is arrive, check-in, \tand enjoy. </li> </ul> If you wish to stay nights other than 4/19/2013, then the conference is not responsible for these costs and you will have to pay for the additional nights. <p> Visiting faculty have been extended a rate of $52.50 per night.  These arrangements need to be made with the hotel directly.  Simply alert the staff that your stay is part of the Rose-Hulman conference. </p><p> The conference will provide buss service to and from the conference.  The undergraduate party will be held at the Quality Inn the evening of 4/19/2013.  Breakfast is included with your stay.       </p>')
    Page.objects.create(title='Directions', on_sidebar=True, page_text='Directions will be posted soon.')
    Page.objects.create(title='Maps', on_sidebar=True, page_text='Maps will be posted soon.')
    Page.objects.create(title='Archives', is_link=True, link='http://www.rose-hulman.edu/class/ma/web/mathconf/history.php')
    Page.objects.create(title='RHIT Math', is_link=True, link='http://www.rose-hulman.edu/math.aspx')
    
def create_contacts():
    from conference.models import Contactee
    
    Contactee.objects.create(name='Allen Holder', email='holder@rose-hulman.edu', phone='812-877-8682', active_contact=True)
    Contactee.objects.create(name='Vin Isaia', email='isaia@rose-hulman.edu', phone='812-877-8543', active_contact=True)

def create_attendees(n=30):
    from django.contrib.auth.models import User
    from conference.models import Attendee, Conference
    
    n_owner = User.objects.get(username='nick')
    conf = Conference.objects.get(name='Current Conference') 
    schools = ['Carnegie Mellon University', 'Davidson College', 'Indiana University', 'Kenyon College', 'Michigan State University', 'Purdue University', 'Rose-Hulman Institute of Technology', 'Stanford', 'University of Louisville']
    first_names = ['Alan', 'Alexa', 'Alexandra', 'Alfonso', 'Alice', 'Alvin', 'Amaya', 'Amber', 'Amy', 'Avram', 'Barclay', 'Boris', 'Brian', 'Brock', 'Cailin', 'Cameran', 'Cameron', 'Carl', 'Chanda', 'Channing', 'Chester', 'Claire', 'Clementine', 'Dai', 'Davis', 'Davis', 'Demetrius', 'Driscoll', 'Dustin', 'Erica', 'Faith', 'Fiona', 'Frances', 'Gary', 'Gary', 'Genevieve', 'George', 'Hadassah', 'Hadassah', 'Hayden', 'Idola', 'Idona', 'Illana', 'Ivy', 'Jackson', 'Jacob', 'Joelle', 'Jolie', 'Kaye', 'Kelsie', 'Lance', 'Lareina', 'Lawrence', 'Lesley', 'Levi', 'Lewis', 'Lyle', 'Madaline', 'Mallory', 'Mannix', 'Mara', 'Marsden', 'Matthew', 'Maxine', 'Meredith', 'Michelle', 'Naomi', 'Nina', 'Nomlanga', 'Norman', 'Pamela', 'Piper', 'Quin', 'Quinn', 'Quyn', 'Rachel', 'Rashad', 'Rebekah', 'Reece', 'Regina', 'Rhea', 'Robert', 'Rose', 'Russell', 'Sacha', 'Sage', 'Shannon', 'Shea', 'Shelby', 'Simon', 'Sylvia', 'Tatum', 'Ulla', 'Vance', 'Willa', 'Winter', 'Xerxes', 'Yael', 'Yuli', 'Zorita']
    last_names = ['Adkins', 'Arnold', 'Ashley', 'Ballard', 'Barry', 'Berger', 'Blackburn', 'Blackwell', 'Blake', 'Bridges', 'Burch', 'Burgess', 'Cameron', 'Cardenas', 'Carrillo', 'Cash', 'Castaneda', 'Christian', 'Cleveland', 'Copeland', 'Cotton', 'Crawford', 'Cunningham', 'Curry', 'Dale', 'Dalton', 'Davidson', 'Dillard', 'Evans', 'Figueroa', 'Fleming', 'Flores', 'Foley', 'Freeman', 'Galloway', 'Gibbs', 'Gilbert', 'Gonzales', 'Gray', 'Hansen', 'Harding', 'Higgins', 'Hobbs', 'Hodges', 'Hunter', 'Irwin', 'Joyce', 'Kent', 'Kramer', 'Lancaster', 'Lang', 'Lindsey', 'Little', 'Lynch', 'Marks', 'Marsh', 'Mathis', 'Maynard', 'Mccall', 'Mcclure', 'Merrill', 'Merritt', 'Middleton', 'Miles', 'Mitchell', 'Morrison', 'Nieves', 'Obrien', 'Petersen', 'Pittman', 'Powell', 'Pugh', 'Ramos', 'Richmond', 'Rivas', 'Rodriquez', 'Rosario', 'Salinas', 'Sampson', 'Sandoval', 'Scott', 'Shields', 'Spears', 'Stark', 'Terrell', 'Townsend', 'Tran', 'Tucker', 'Valenzuela', 'Vargas', 'Wade', 'Walker', 'Walton', 'Warren', 'Wells', 'Whitney', 'Wolf', 'Wong', 'Wright', 'Yang']
    for i in range(n):
        f = choice(first_names)
        l = choice(last_names)
        a = Attendee.objects.create(owner=n_owner, conference=conf, email='%s@%s.com' % (f, l), \
                                    first_name = f, last_name=l, school=choice(schools), attendee_type=choice(['Student', 'Faculty']))
        if randint(0,n/10) == 0:
            a.is_submitting_talk = True
            a.paper_title = 'Lorem Ipsum'
            a.paper_abstract = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus luctus posuere egestas. Integer posuere nisl sit amet ipsum faucibus sollicitudin. Maecenas est mi, tempor sit amet feugiat adipiscing, porta quis sapien. Vivamus sit amet ultricies orci. Ut tristique eleifend sem. Sed porttitor, augue auctor fringilla mattis, tellus enim tristique tellus, eleifend scelerisque nisi urna elementum ipsum. In hac habitasse platea dictumst. Vivamus at ultricies neque.'
            if randint(0,1) == 0:
                a.is_submitted_for_best_of_competition = True
        if randint(0,2) == 0:
            a.requires_housing = True
            if randint(0,1) == 0:
                a.has_been_paired_for_housing = True
        a.save()

def create_rooms(n=5):
    from conference.models import Room
    
    for i in range(n):
        Room.objects.create(building='Crapo', room_number='G2%s' % (20 + i))

def create_sessions():
    pass

if __name__ == '__main__':
    import argparse, os
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store_true', help='Reset site settings and auth system.')
    args = parser.parse_args()
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RHITUMC.settings")
    run(args.p)