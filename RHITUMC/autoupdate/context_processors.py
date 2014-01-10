'''
Created on Jan 10, 2014

@author: nick
'''

import importlib

from utils import get_all_modules

def autoupdate_cp(request):
    if request.method == 'GET' and 'admin' in request.get_full_path():
        for module_str in get_all_modules():
            try:
                module = importlib.import_module(module_str)
                print "'%s' version: %s" % (module_str, module.VERSION)
            except ImportError:
                print "'%s' version missing or specified incorrectly; skipping." % module_str
    return {}