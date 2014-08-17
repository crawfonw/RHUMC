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

import datetime
import importlib

from json_reader import get_version_json_from_url
from utils import get_all_modules

UPDATE_PATHS = ['admin', 'portal'] #where it will check and notify

#We'll just store this in memory. If the program gets restarted,
#then it doesn't hurt to check again.
last_check = None

def autoupdate_cp(request):
    global last_check
    print 'Last update check: ', last_check
    if request.method == 'GET' and \
        len([i for i in UPDATE_PATHS if i in  request.get_full_path()]) > 0:
        if last_check is None or last_check >= datetime.datetime.now() + \
            datetime.timedelta(weeks=1):
            for module_str in get_all_modules():
                try:
                    module = importlib.import_module(module_str)
                    remote = get_version_json_from_url(module.VERSION['remote_version'])
                    print "'%s' local version: %s" % (module_str, module.VERSION)
                    print "'%s' remote version: %s" % (module_str, remote)
                except ImportError:
                    print "'%s' version missing or specified incorrectly; skipping." % module_str
            last_check = datetime.datetime.now()
    return {}