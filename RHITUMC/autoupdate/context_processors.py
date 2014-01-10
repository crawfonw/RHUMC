'''
Created on Jan 10, 2014

@author: nick
'''

def autoupdate_cp(request):
    print dir(request)
    print request.get_full_path()
    if request.method == 'GET' and 'admin' in request.get_full_path():
        import autoupdate, conference, RHITUMC
        print 'Autoupdate version: ', autoupdate.VERSION
        print 'Conference version: ', conference.VERSION
        print 'RHITUMC version: ', RHITUMC.VERSION 
    return {}