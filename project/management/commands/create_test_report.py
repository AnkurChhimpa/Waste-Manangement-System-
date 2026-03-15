from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from project.models import WasteReport

class Command(BaseCommand):
    help = 'Create a test waste report'

    def add_arguments(self, parser):
        parser.add_argument('--location', type=str, default='Test Location - Main Street', help='Location of waste')
        parser.add_argument('--waste-type', type=str, default='plastic', help='Type of waste')
        parser.add_argument('--severity', type=str, default='medium', help='Severity level')
        parser.add_argument('--description', type=str, default='Test waste report for crew assignment', help='Description')

    def handle(self, *args, **options):
        location = options['location']
        waste_type = options['waste_type']
        severity = options['severity']
        description = options['description']

        try:
            # Get or create a test user
            user, created = User.objects.get_or_create(
                username='test_reporter',
                defaults={'password': 'testpass123'}
            )
            
            # Create waste report
            report = WasteReport.objects.create(
                user=user,
                location=location,
                latitude=40.7128,  # Example coordinates (New York)
                longitude=-74.0060,
                waste_type=waste_type,
                severity=severity,
                description=description,
                status='pending'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created test waste report #{report.id} at "{location}"'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test report: {e}')
            )