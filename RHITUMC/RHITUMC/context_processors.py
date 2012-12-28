from datetime import datetime
#from django.db.models import F

from conference.models import Conference, Page

def links_context_processor(request):
    
    return {
            'PAGES': Page.objects.all()
            }
    
def conference_context_processor(request):
    
    c = Conference.objects.filter(end_date__gte=datetime.now())
    if c.count() > 0:
        c = c[0]
    else:
        c = None
    
    return {
            'CONF': c
            }