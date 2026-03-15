from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from project.models import CrewMember

class Command(BaseCommand):
    help = 'Create a crew member'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the crew member')
        parser.add_argument('password', type=str, help='Password for the crew member')
        parser.add_argument('employee_id', type=str, help='Employee ID for the crew member')
        parser.add_argument('--phone', type=str, help='Phone number (optional)')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        employee_id = options['employee_id']
        phone = options.get('phone', '')

        try:
            # Create user
            user = User.objects.create_user(username=username, password=password)
            
            # Create crew member profile
            crew_member = CrewMember.objects.create(
                user=user,
                employee_id=employee_id,
                phone=phone
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created crew member "{username}" with ID "{employee_id}"'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating crew member: {e}')
            )