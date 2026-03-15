from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from project.models import Event
from datetime import date, time, timedelta

class Command(BaseCommand):
    help = 'Create test events for demonstration'

    def handle(self, *args, **options):
        try:
            # Get or create admin user as organizer
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            
            # Create upcoming events
            events_data = [
                {
                    'title': 'Beach Cleanup Drive',
                    'description': 'Join us for a morning beach cleanup to remove plastic waste and debris from our beautiful coastline. We will provide all necessary equipment including gloves, bags, and pickup tools.',
                    'event_type': 'cleanup',
                    'location': 'Marina Beach, Chennai',
                    'date': date.today() + timedelta(days=3),
                    'time': time(9, 0),
                    'max_participants': 30
                },
                {
                    'title': 'Community Garden Cleanup',
                    'description': 'Help maintain our community garden by removing weeds, organizing tools, and preparing beds for new plantings. Perfect for families and beginners.',
                    'event_type': 'cleanup',
                    'location': 'Green Valley Community Garden',
                    'date': date.today() + timedelta(days=7),
                    'time': time(16, 0),
                    'max_participants': 15
                },
                {
                    'title': 'Environmental Awareness Workshop',
                    'description': 'Learn about sustainable living practices, waste reduction techniques, and how to make a positive environmental impact in your daily life.',
                    'event_type': 'workshop',
                    'location': 'Community Center Hall A',
                    'date': date.today() + timedelta(days=10),
                    'time': time(14, 0),
                    'max_participants': 50
                },
                {
                    'title': 'Tree Planting Initiative',
                    'description': 'Join our tree planting drive to increase green cover in urban areas. We will plant native species that are well-suited to our local climate.',
                    'event_type': 'tree_planting',
                    'location': 'City Park Extension Area',
                    'date': date.today() + timedelta(days=14),
                    'time': time(8, 0),
                    'max_participants': 25
                },
                {
                    'title': 'Recycling Drive & Education',
                    'description': 'Bring your recyclable materials and learn about proper sorting techniques. We will also demonstrate how to create useful items from waste materials.',
                    'event_type': 'recycling',
                    'location': 'School Playground, Main Street',
                    'date': date.today() + timedelta(days=21),
                    'time': time(10, 0),
                    'max_participants': 40
                }
            ]
            
            # Create past events
            past_events_data = [
                {
                    'title': 'Park Cleanup Initiative',
                    'description': 'Successfully cleaned 2 hectares of park area, collected 45kg of waste and organized community participation.',
                    'event_type': 'cleanup',
                    'location': 'Central Park',
                    'date': date.today() - timedelta(days=7),
                    'time': time(8, 0),
                    'max_participants': 20
                },
                {
                    'title': 'River Bank Restoration',
                    'description': 'Removed invasive plants and litter from river banks, planted native vegetation to prevent erosion.',
                    'event_type': 'cleanup',
                    'location': 'Riverside Park',
                    'date': date.today() - timedelta(days=14),
                    'time': time(7, 0),
                    'max_participants': 35
                }
            ]
            
            created_count = 0
            
            # Create upcoming events
            for event_data in events_data:
                event, created = Event.objects.get_or_create(
                    title=event_data['title'],
                    defaults={
                        'description': event_data['description'],
                        'event_type': event_data['event_type'],
                        'location': event_data['location'],
                        'date': event_data['date'],
                        'time': event_data['time'],
                        'organizer': admin_user,
                        'max_participants': event_data['max_participants']
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f"Created upcoming event: {event.title}")
            
            # Create past events
            for event_data in past_events_data:
                event, created = Event.objects.get_or_create(
                    title=event_data['title'],
                    defaults={
                        'description': event_data['description'],
                        'event_type': event_data['event_type'],
                        'location': event_data['location'],
                        'date': event_data['date'],
                        'time': event_data['time'],
                        'organizer': admin_user,
                        'max_participants': event_data['max_participants']
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f"Created past event: {event.title}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} test events'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test events: {e}')
            )