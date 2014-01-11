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

import json
import os
import urllib2

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

EMPTY_VERSION = {'app': None, 'version': None, 'info': None, 'author': None,
                 'remote_version': None}

def get_version_json_from_url(url):
    response = None
    try:
        response = urllib2.urlopen(url, timeout=1)
    except:
        #TODO: Make more robust later
        #Though we _really_ don't care how it failed
        print 'Error opening URL: ', url
        return EMPTY_VERSION
        
    try:
        remote_version = json.load(response)
        return remote_version
    except ValueError:
        print 'Remote versioning file for %s contains errors.' % url
        return EMPTY_VERSION

def get_version_json_from_module(name):
    json_file = os.getcwd() + os.path.sep + name + os.path.sep + 'version.json'
    version = {}
    json_data = None
    try:
        json_data = open(json_file)
    except IOError:
        print 'Versioning file for %s not found.' % name
        return EMPTY_VERSION
    
    try:
        version = json.load(json_data)
    except ValueError:
        json_data.close()
        print 'Versioning file for %s contains syntax errors.' % name
        return EMPTY_VERSION
    
    json_data.close()
    return version

def clean_version_json_data(data):
    #this is all very ugly
    try:
        data['app']
    except KeyError:
        print 'App name missing.'
        data['app'] = None
    
    try:
        data['version']
    except KeyError:
        print 'Version number missing.'
        data['version'] = None
        
    try:
        if not isinstance(data['info'], dict):
            print 'Version info is not in correct dict format; removing.'
            data['info'] = None
    except KeyError:
        data['info'] = None
    
    try:
        if not isinstance(data['author'], dict):
            print 'Version author is not in correct dict format; removing.'
            data['author'] = None
    except KeyError:
        data['author'] = None
        
    try:
        data['remote_version']
        try:
            URLValidator(data['remote_version'])
        except ValidationError, e:
            print e
            data['remote_version'] = None
    except KeyError:
        print 'Remote versioning url missing.'
        data['remote_version'] = None
        
    return data