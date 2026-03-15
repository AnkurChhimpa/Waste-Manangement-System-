from .models import CrewMember

def crew_member_context(request):
    """Add crew member information to template context"""
    context = {}
    
    if request.user.is_authenticated:
        try:
            crew_member = CrewMember.objects.get(user=request.user)
            context['is_crew_member'] = True
            context['crew_member'] = crew_member
        except CrewMember.DoesNotExist:
            context['is_crew_member'] = False
            context['crew_member'] = None
    else:
        context['is_crew_member'] = False
        context['crew_member'] = None
    
    return context