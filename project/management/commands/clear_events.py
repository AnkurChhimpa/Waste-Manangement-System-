from django.core.management.base import BaseCommand
from project.models import Event, EventParticipation

class Command(BaseCommand):
    help = 'Clear all events and event participations from the database'

    def handle(self, *args, **options):
        # Delete all event participations first (due to foreign key constraints)
        participation_count = EventParticipation.objects.count()
        EventParticipation.objects.all().delete()
        
        # Delete all events
        event_count = Event.objects.count()
        Event.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {event_count} events and {participation_count} participations'
            )
        )