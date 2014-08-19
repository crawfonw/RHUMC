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

from contextlib import nested
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

import mock

from conference import views
from conference.models import Attendee, Conference

class TestPagesDoLoadProperly(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('admin', 'admin@test.com', 'aaa')
        self.user.is_superuser = True
        self.user.save()
    
    def testAdminPagesDoRequireLogin(self):
        response = self.client.get(reverse('admin-portal'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('admin-portal'))
        
        response = self.client.get(reverse('badges-generator'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('badges-generator'))
        
        response = self.client.get(reverse('batch-updater'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('batch-updater'))
        
        response = self.client.get(reverse('csv-dump'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('csv-dump'))
        
        response = self.client.get(reverse('attendee-emailer'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('attendee-emailer'))
        
        response = self.client.get(reverse('schedule-generator'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('schedule-generator'))
        
    def testAdminPagesDoRedirectIfNonStaffIsLoggedIn(self):
        User.objects.create_user('noadmin', 'noadmin@test.com', 'aaa')
        self.client.login(username='noadmin', password='aaa')
        
        response = self.client.get(reverse('admin-portal'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response = self.client.get(reverse('badges-generator'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response = self.client.get(reverse('batch-updater'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response = self.client.get(reverse('csv-dump'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response = self.client.get(reverse('attendee-emailer'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response = self.client.get(reverse('schedule-generator'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
    
    def testAdminPortalPageDoesLoadAfterLogin(self):
        self.client.login(username='admin', password='aaa')
        
        response = self.client.get(reverse('admin-portal'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('badges-generator'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('batch-updater'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('csv-dump'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('attendee-emailer'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('schedule-generator'))
        self.assertEqual(response.status_code, 200)

    def testRegistrationPageDoesLoad(self):
        response = self.client.get(reverse('conference-registration'))
        self.assertEqual(response.status_code, 200)
        
class TestValidAttendeeRegistrationCreationInDB(TestCase):
    
    def setUp(self):
        self.form_data = {'email':'a@b.com', 'confirm_email':'a@b.com',
                          'first_name':'foo', 'last_name':'bar', 'sex':'Male',
                          'school':'University College', 'size_of_institute':'<2000',
                          'max_degree':"Bachelor's", 'attendee_type':'Student',
                          'year':'FR', 'is_submitting_talk':True, 'paper_title':'Title',
                          'paper_abstract':'Abstract', 'is_submitted_for_best_of_competition':True,
                          'dietary_restrictions':'Foods', 'requires_housing':True,
                          'comments':'Wootsauce'}
    
    def testCannotRegisterIfNoConference(self):
        response = self.client.post(reverse('conference-registration'), self.form_data)
        self.assertEqual(Attendee.objects.count(), 0)
        
    def testCanRegisterIfConference(self):
        now = datetime.now()
        Conference.objects.create(name='Current Conference', start_date=now - timedelta(days=15), end_date=now + timedelta(days=60), registration_open=True, show_program=False)
        response = self.client.post(reverse('conference-registration'), self.form_data)
        self.assertEqual(Attendee.objects.count(), 1)
        
class TestAttendeeRegistrationFormValidation(TestCase):

    def setUp(self):
        self.form_data = {'email':'a@b.com', 'confirm_email':'a@b.com',
                          'first_name':'foo', 'last_name':'bar', 'sex':'Male',
                          'school':'University College', 'size_of_institute':'<2000',
                          'max_degree':"Bachelor's", 'attendee_type':'Student',
                          'year':'FR', 'is_submitting_talk':True, 'paper_title':'Title',
                          'paper_abstract':'Abstract', 'is_submitted_for_best_of_competition':True,
                          'dietary_restrictions':'Foods', 'requires_housing':True,
                          'comments':'Wootsauce'}
        
        self.mock_request = mock.Mock()
        self.mock_request.method = 'POST'
        self.mock_request.POST = self.form_data
        
        self.mock_conference = mock.Mock()
        self.mock_conference.registration_open = True
        
        self.mock_attendee = mock.Mock()
        self.mock_attendee.conference = self.mock_conference
        self.mock_attendee.email = self.form_data['email']
        
        def render_to_response_echo(*args, **kwargs):
            context = args[1]
            context['template_name'] = args[0]  
            return context
        
        self.response_patcher = mock.patch('conference.views.render_to_response', render_to_response_echo)
        self.attendee_create_patcher = mock.patch('conference.views.Attendee.objects.create', mock.Mock(return_value=self.mock_attendee))
        self.current_conference_patcher = mock.patch.multiple('conference.views',
                                 _get_current_conference=mock.Mock(return_value=self.mock_conference),
                                 FORWARD_REGISTRATIONS=False
                                 )
        
        self.response_patcher.start()
        self.attendee_create_patcher.start()
        
    def tearDown(self):
        mock.patch.stopall()
        
    def testCannotRegisterIfNoActiveConference(self):
        with mock.patch('conference.views._get_current_conference', mock.Mock(return_value=None)):
            response = views.register_attendee(self.mock_request)
            self.assertEqual(response['template_name'], 'conference/generic-text.html')
            self.assertEqual(response['text'], 'We are sorry, but currently there is no conference scheduled. Please check back later.')
      
    def testCannotRegisterWithClosedConference(self):
        with mock.patch('conference.views._get_current_conference', mock.Mock(return_value=self.mock_conference)):
            self.mock_conference.registration_open = False
        
            response = views.register_attendee(self.mock_request)
            self.assertEqual(response['template_name'], 'conference/generic-text.html')
            self.assertEqual(response['text'], 'We are sorry, but registration has closed for this conference.')
    
    def testCanRegisterWithOpenConference(self):
        self.current_conference_patcher.start()
        response = views.register_attendee(self.mock_request)
        self.assertEqual(response['template_name'], 'conference/generic-text.html')
        self.assertEqual(response['page_title'], 'Registration Complete')
        self.assertEqual(response['text'], "<b>Thanks, you are now registered for the conference. A copy of your provided information has been emailed to %s for your records. Make sure to check your junk mail folder if you don't see it. We are looking forward to having you at the conference!</b>" % self.form_data['email'])
    
    def testMismatchedConfirmEmail(self):
        self.current_conference_patcher.start()
        self.form_data['confirm_email'] = 'b@a.com'
        response = views.register_attendee(self.mock_request)
        self.assertEqual(len(response['form'].errors), 3) #Non-field error + 2 field errors
        self.assertFormError(mock.Mock(context=response), 'form', 'email', 'Email addresses must match!')
        self.assertFormError(mock.Mock(context=response), 'form', 'confirm_email', 'Email addresses must match!')
        
    def testIsSubmittingTalkCheckedButTitleAndAbstractOmitted(self):
        self.current_conference_patcher.start()
        self.form_data['is_submitting_talk'] = True
        self.form_data['paper_title'] = ''
        self.form_data['paper_abstract'] = ''
        response = views.register_attendee(self.mock_request)
        self.assertEqual(len(response['form'].errors), 3)
        self.assertFormError(mock.Mock(context=response), 'form', 'paper_title', "You must provide your paper's title if you are submitting a talk.")
        self.assertFormError(mock.Mock(context=response), 'form', 'paper_abstract', "You must provide your paper's abstract if you are submitting a talk.")
        
    def testIsSubmittingTalkCheckedButTitleOmitted(self):
        self.current_conference_patcher.start()
        self.form_data['is_submitting_talk'] = True
        self.form_data['paper_title'] = ''
        response = views.register_attendee(self.mock_request)
        self.assertEqual(len(response['form'].errors), 2)
        self.assertFormError(mock.Mock(context=response), 'form', 'paper_title', "You must provide your paper's title if you are submitting a talk.")
        
    def testIsSubmittingTalkCheckedButAbstractOmitted(self):
        self.current_conference_patcher.start()
        self.form_data['is_submitting_talk'] = True
        self.form_data['paper_abstract'] = ''
        response = views.register_attendee(self.mock_request)
        self.assertEqual(len(response['form'].errors), 2)
        self.assertFormError(mock.Mock(context=response), 'form', 'paper_abstract', "You must provide your paper's abstract if you are submitting a talk.")
    
    def testOnlyPaperTitleFilled(self):
        self.current_conference_patcher.start()
        self.form_data['is_submitting_talk'] = False
        self.form_data['paper_abstract'] = ''
        response = views.register_attendee(self.mock_request)
        self.assertEqual(len(response['form'].errors), 3)
        self.assertFormError(mock.Mock(context=response), 'form', 'is_submitting_talk', "Make sure to check this if you are submitting a talk!")
        self.assertFormError(mock.Mock(context=response), 'form', 'paper_abstract', "You must provide your paper's abstract if you are submitting a talk.")
        
    def testOnlyPaperAbstractFilled(self):
        self.current_conference_patcher.start()
        self.form_data['is_submitting_talk'] = False
        self.form_data['paper_title'] = ''
        response = views.register_attendee(self.mock_request)
        self.assertEqual(len(response['form'].errors), 3)
        self.assertFormError(mock.Mock(context=response), 'form', 'is_submitting_talk', "Make sure to check this if you are submitting a talk!")
        self.assertFormError(mock.Mock(context=response), 'form', 'paper_title', "You must provide your paper's title if you are submitting a talk.")
        
    def testPaperTitleAndAbstractFilled(self):
        self.current_conference_patcher.start()
        self.form_data['is_submitting_talk'] = False
        response = views.register_attendee(self.mock_request)
        self.assertEqual(len(response['form'].errors), 2)
        self.assertFormError(mock.Mock(context=response), 'form', 'is_submitting_talk', "Make sure to check this if you are submitting a talk!")
        
    def testEmptyRequireHousingDefaultsToNo(self):
        self.current_conference_patcher.start()
        self.form_data['requires_housing'] = None
        response = views.register_attendee(self.mock_request)
        self.assertTrue('form' not in response.keys())
        self.assertEqual(response['template_name'], 'conference/generic-text.html')
        self.assertEqual(response['page_title'], 'Registration Complete')
        