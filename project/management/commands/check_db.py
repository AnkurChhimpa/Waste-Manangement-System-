from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from project.models import WasteReport, CrewMember, Event, EventParticipation

class Command(BaseCommand):
    help = 'Check database status'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DATABASE STATUS ==='))
        
        # Users
        total_users = User.objects.count()
        admin_users = User.objects.filter(is_superuser=True).count()
        regular_users = User.objects.filter(is_superuser=False).count()
        
        self.stdout.write(f'Users: {total_users} total ({admin_users} admin, {regular_users} regular)')
        
        # Crew Members
        crew_members = CrewMember.objects.all()
        active_crew = crew_members.filter(is_active=True).count()
        inactive_crew = crew_members.filter(is_active=False).count()
        
        self.stdout.write(f'Crew Members: {crew_members.count()} total ({active_crew} active, {inactive_crew} inactive)')
        
        for crew in crew_members:
            self.stdout.write(f'  - {crew.user.username} (ID: {crew.employee_id}, Active: {crew.is_active})')
        
        # Reports
        reports = WasteReport.objects.all()
        pending_reports = reports.filter(status='pending').count()
        assigned_reports = reports.filter(status='assigned').count()
        in_progress_reports = reports.filter(status='in_progress').count()
        completed_reports = reports.filter(status='completed').count()
        
        self.stdout.write(f'Reports: {reports.count()} total')
        self.stdout.write(f'  - Pending: {pending_reports}')
        self.stdout.write(f'  - Assigned: {assigned_reports}')
        self.stdout.write(f'  - In Progress: {in_progress_reports}')
        self.stdout.write(f'  - Completed: {completed_reports}')
        
        # Events
        events = Event.objects.count()
        participants = EventParticipation.objects.count()
        
        self.stdout.write(f'Events: {events} total')
        self.stdout.write(f'Event Participants: {participants} total')
        
        # Recent reports
        recent_reports = WasteReport.objects.order_by('-created_at')[:3]
        if recent_reports:
            self.stdout.write('Recent Reports:')
            for report in recent_reports:
                self.stdout.write(f'  - ID {report.id}: {report.waste_type} at {report.location} ({report.status})')
        
        self.stdout.write(self.style.SUCCESS('=== END STATUS ==='))