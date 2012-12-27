from conference.models import PageLink

def links_context_processor(request):
    
    return {
            'LINKS': PageLink.objects.all()
            }
    
def conference_context_processor(request):
    
    return {
            
            }