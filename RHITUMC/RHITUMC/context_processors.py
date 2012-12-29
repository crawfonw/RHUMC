from datetime import datetime
#from django.db.models import F

from conference.models import Conference, Contactee, Page

def project_context_processor(request):
    
    c = Conference.objects.filter(end_date__gte=datetime.now())
    if c.count() > 0:
        c = c[0]
    else:
        c = None
    
    return {
            'CONF': c,
            'CONTACTS': Contactee.objects.filter(active_contact=True),
            'PAGES': Page.objects.all(),
            }