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
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

class TestPagesDoLoadProperly(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('admin', 'admin@test.com', 'aaa')
        self.user.is_superuser = True
        self.user.save()
    
    def testAdminPagesDoRequireLogin(self):
        response =  self.client.get(reverse('admin-portal'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('admin-portal'))
        
        response =  self.client.get(reverse('badges-generator'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('badges-generator'))
        
        response =  self.client.get(reverse('batch-updater'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('batch-updater'))
        
        response =  self.client.get(reverse('csv-dump'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('csv-dump'))
        
        response =  self.client.get(reverse('attendee-emailer'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('attendee-emailer'))
        
        response =  self.client.get(reverse('schedule-generator'))
        self.assertRedirects(response, '/accounts/login/?next=%s' % reverse('schedule-generator'))
        
    def testAdminPagesDoRedirectIfNonStaffIsLoggedIn(self):
        User.objects.create_user('noadmin', 'noadmin@test.com', 'aaa')
        self.client.login(username='noadmin', password='aaa')
        
        response =  self.client.get(reverse('admin-portal'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response =  self.client.get(reverse('badges-generator'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response =  self.client.get(reverse('batch-updater'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response =  self.client.get(reverse('csv-dump'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response =  self.client.get(reverse('attendee-emailer'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
        
        response =  self.client.get(reverse('schedule-generator'))
        self.assertRedirects(response, reverse('conference-index'), status_code=302, target_status_code=200)
    
    def testAdminPortalPageDoesLoadAfterLogin(self):
        self.client.login(username='admin', password='aaa')
        
        response =  self.client.get(reverse('admin-portal'))
        self.assertEqual(response.status_code, 200)
        
        response =  self.client.get(reverse('badges-generator'))
        self.assertEqual(response.status_code, 200)
        
        response =  self.client.get(reverse('batch-updater'))
        self.assertEqual(response.status_code, 200)
        
        response =  self.client.get(reverse('csv-dump'))
        self.assertEqual(response.status_code, 200)
        
        response =  self.client.get(reverse('attendee-emailer'))
        self.assertEqual(response.status_code, 200)
        
        response =  self.client.get(reverse('schedule-generator'))
        self.assertEqual(response.status_code, 200)

    def testRegistrationPageDoesLoad(self):
        response = self.client.get(reverse('conference-registration'))
        self.assertEqual(response.status_code, 200)
        
class TestAttendeeRegistration(TestCase):
    
    def setUp(self):
        pass