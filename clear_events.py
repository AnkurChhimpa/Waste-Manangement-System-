import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastemanagement.settings')
django.setup()

from project.models import Event, EventParticipation

# Delete all events and participations
EventParticipation.objects.all().delete()
Event.objects.all().delete()

print("All events and participations cleared.")