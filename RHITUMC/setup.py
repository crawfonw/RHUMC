"""
    Conference scheduling software for undergraduate institutions.
    Created specifically for the Mathematics department of the
    Rose-Hulman Institute of Technology (http://www.rose-hulman.edu/math.aspx).
    
    Copyright (C) 2014  Nick Crawford <crawfonw -at- gmail.com>

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
#!/usr/bin/env python
import os
import sys

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'RHITUMC')

SETTINGS = '''
"""
Django settings for RHUMC project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
AUTH_PROFILE_MODULE = 'conference.UserProfile'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# Anyone in the ADMIN tuple will receieve server error emails

ADMINS = (
#    ('Admin Name', 'admin@email.com'),
)

MANAGERS = ADMINS

# SECURITY WARNING: keep the secret key used in production secret!
# Try not to lose/modify it!
# Adapted from https://gist.github.com/ndarville/3452907
# For use on services like Heroku see comments on gist

SECRET_FILE = os.path.join(BASE_DIR, 'secret.txt')
try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    import random, string
    SECRET_KEY = ''.join([random.SystemRandom().choice("{}{}{}".format(string.ascii_letters, string.digits, string.punctuation)) for i in range(50)])
    secret = file(SECRET_FILE, 'w')
    secret.write(SECRET_KEY)
    secret.close()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = %s
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = %s

SITE_ID = 1

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'conference',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'RHITUMC.urls'

WSGI_APPLICATION = 'RHITUMC.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        %s
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Email server host and port
# Use the python command below to use in testing
# python -m smtpd -n -c DebuggingServer localhost:1025

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
'''

WSGI = '''
import os, sys 
 
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
if path not in sys.path: 
    sys.path.append(path) 
 
os.environ["DJANGO_SETTINGS_MODULE"] = "RHITUMC.settings"

# This application object is used by any WSGI server configured to use this 
# file. This includes Django's development server, if the WSGI_APPLICATION 
# setting points here. 
from django.core.wsgi import get_wsgi_application 
application = get_wsgi_application()
'''

def create_wsgi():
    wsgi = file(os.path.join(BASE_DIR, 'wsgi.py'), 'w')
    wsgi.write(WSGI)
    wsgi.close()

def create_settings(is_test, hosts, db):
    if is_test:
        settings_doc = SETTINGS % (is_test, ['localhost'], db)
    else:
        settings_doc = SETTINGS % (is_test, hosts, db)
    
    settings = file(os.path.join(BASE_DIR, 'settings.py'), 'w')
    settings.write(settings_doc)
    settings.close()

def main(t, hosts, db):
    create_wsgi()
    create_settings(t, hosts, db)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='Setup settings.py for local testing (does not create wsgi.py)', action='store_true')
    parser.add_argument('-w', help='Allowed hosts for this app i.e. ".example.com"', nargs='+', type=str)
    parser.add_argument('-d', help='Database type', choices=['postgres', 'mysql', 'oracle', 'sqlite'])
    args = parser.parse_args()
    
    db = ''
    if args.d == 'sqlite' or args.d is None:
        db = """'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),"""
    else:
        if args.d == 'postgres':
            db = 'postgresql_psycopg2'
        elif args.d == 'mysql':
            db = 'mysql'
        elif args.d == 'oracle':
            db = 'oracle'
        db = """'ENGINE': 'django.db.backends.%s',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',""" % db
    
    main(args.t, "['localhost']" if args.w is None else args.w, db)
