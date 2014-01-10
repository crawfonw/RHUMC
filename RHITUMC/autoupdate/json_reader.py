'''
Created on Jan 10, 2014

@author: nick
'''

import json
import os

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

def get_version_json_from_file(f):
    json_file = os.getcwd() + os.path.sep + f + os.path.sep + 'version.json'
    version = {}
    json_data = None
    try:
        json_data = open(json_file)
    except IOError:
        print 'Versioning file for %s not found.' % f
        version['app'] = None
        version['version'] = None
        version['info'] = None
        version['author'] = None
        version['remote_version'] = None
        return version
    
    try:
        version = json.load(json_data)
    except ValueError:
        json_data.close()
        print 'Versioning file for %s contains syntax errors.' % f
        version['app'] = None
        version['version'] = None
        version['info'] = None
        version['author'] = None
        version['remote_version'] = None
        return version
    
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