from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from project.models import Event
from datetime import date, time, timedelta

class Command(BaseCommand):
    help = 'Add sample events to the database'

    def handle(self, *args, **options):
        # Get or create admin user as organizer
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@worth2waste.com', 'is_staff': True, 'is_superuser': True}
        )
        
        # Sample events data
        events_data = [
            {
                'title': 'Community Beach Cleanup Drive',
                'description': 'Join us for a massive beach cleanup to remove plastic waste and debris from our coastline. Volunteers will be provided with gloves, bags, and refreshments.',
                'event_type': 'cleanup',
                'location': 'Marina Beach, Chennai',
                'date': date.today() + timedelta(days=7),
                'time': time(9, 0),
                'max_participants': 100
            },
            {
                'title': 'Plastic-Free Living Workshop',
                'description': 'Learn practical tips and techniques to reduce plastic consumption in daily life. Expert speakers will share sustainable alternatives and eco-friendly practices.',
                'event_type': 'workshop',
                'location': 'Green Community Center, Mumbai',
                'date': date.today() + timedelta(days=14),
                'time': time(14, 0),
                'max_participants': 50
            },
            {
                'title': 'Tree Plantation Campaign',
                'description': 'Help us plant 500 native trees in the city park. Each participant will plant and adopt a tree. Saplings and tools will be provided.',
                'event_type': 'tree_planting',
                'location': 'Central Park, Delhi',
                'date': date.today() + timedelta(days=21),
                'time': time(8, 0),
                'max_participants': 200
            },
            {
                'title': 'E-Waste Collection Drive',
                'description': 'Bring your old electronics for proper recycling. We accept phones, laptops, batteries, and other electronic items for safe disposal.',
                'event_type': 'recycling',
                'location': 'Tech Hub, Bangalore',
                'date': date.today() + timedelta(days=10),
                'time': time(10, 0),
                'max_participants': 75
            },
            {
                'title': 'Zero Waste Awareness Campaign',
                'description': 'Street awareness program to educate citizens about zero waste lifestyle. Volunteers will distribute pamphlets and conduct mini-sessions.',
                'event_type': 'awareness',
                'location': 'Commercial Street, Pune',
                'date': date.today() + timedelta(days=5),
                'time': time(16, 0),
                'max_participants': 30
            },
            {
                'title': 'River Cleanup Initiative',
                'description': 'Clean the riverbank and remove floating waste from the water. Boats and safety equipment will be provided for water cleanup activities.',
                'event_type': 'cleanup',
                'location': 'Yamuna River, Agra',
                'date': date.today() + timedelta(days=28),
                'time': time(7, 0),
                'max_participants': 80
            }
        ]
        
        # Create events
        created_count = 0
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
                self.stdout.write(f"Created event: {event.title}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {created_count} sample events')
        )