from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WasteReport, Event, CrewMember, EventParticipation, ContactMessage
from django.utils import timezone
from django.db import models
import json

def home(request):
    # Calculate real statistics
    total_reports = WasteReport.objects.count()
    total_users = User.objects.filter(is_superuser=False).count()
    areas_cleaned = WasteReport.objects.filter(status='completed').count()
    
    context = {
        'total_reports': total_reports,
        'total_users': total_users,
        'areas_cleaned': areas_cleaned,
        'show_training_popup': request.session.pop('show_training_popup', False),
    }
    return render(request, 'pages/home.html', context)

def roles(request):
    return render(request, 'pages/roles.html')

def signin(request):
    return render(request, 'pages/signin.html')

def join(request):
    return render(request, 'pages/join.html')

def about(request):
    return render(request, 'pages/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'pages/contact.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        print(f"Login attempt: {username}")
        
        if not username:
            messages.error(request, 'Username is required.')
        elif not password:
            messages.error(request, 'Password is required.')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                print(f"User logged in: {user.username}, is_superuser: {user.is_superuser}")
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('/')
            else:
                messages.error(request, 'Invalid username or password.')
    return render(request, 'pages/login.html')

def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    users = User.objects.all().order_by('-date_joined')
    reports = WasteReport.objects.all().order_by('-created_at')[:10]  # Latest 10 reports
    volunteers = User.objects.filter(is_superuser=False)  # All non-admin users as potential volunteers
    
    # Get crew members with their crew member details
    crew_members = User.objects.filter(crewmember__isnull=False, crewmember__is_active=True).select_related('crewmember')
    
    # Get recent contact messages
    contact_messages = ContactMessage.objects.all().order_by('-created_at')[:10]
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    
    print(f"Admin dashboard - Found {crew_members.count()} active crew members")
    for crew in crew_members:
        print(f"Crew member: {crew.username} (ID: {crew.id}, Employee ID: {crew.crewmember.employee_id})")
    
    # Calculate analytics data
    total_reports = WasteReport.objects.count()
    completed_reports = WasteReport.objects.filter(status='completed').count()
    pending_reports = WasteReport.objects.filter(status='pending').count()
    in_progress_reports = WasteReport.objects.filter(status='in_progress').count()
    total_events = Event.objects.count()
    total_participants = EventParticipation.objects.filter(status='approved').count()
    
    # Calculate resolution rate
    resolution_rate = round((completed_reports / total_reports * 100) if total_reports > 0 else 0)
    
    print(f"Admin dashboard - Found {reports.count()} reports, {pending_reports} pending")
    print(f"Admin dashboard - Total events in database: {total_events}")
    
    context = {
        'users': users, 
        'reports': reports, 
        'volunteers': volunteers,
        'crew_members': crew_members,
        'total_reports': total_reports,
        'completed_reports': completed_reports,
        'pending_reports': pending_reports,
        'in_progress_reports': in_progress_reports,
        'resolution_rate': resolution_rate,
        'total_events': total_events,
        'total_participants': total_participants,
        'contact_messages': contact_messages,
        'unread_messages': unread_messages,
    }
    return render(request, 'pages/admin_dashboard.html', context)

def admin_reports(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    all_reports = WasteReport.objects.all().order_by('-created_at')
    total_reports = all_reports.count()
    pending_reports = all_reports.filter(status='pending').count()
    in_progress_reports = all_reports.filter(status='in_progress').count()
    completed_reports = all_reports.filter(status='completed').count()
    
    # Get crew members and volunteers for assignment
    crew_members = User.objects.filter(crewmember__isnull=False, crewmember__is_active=True).select_related('crewmember')
    volunteers = User.objects.filter(is_superuser=False)
    
    context = {
        'all_reports': all_reports,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'in_progress_reports': in_progress_reports,
        'completed_reports': completed_reports,
        'crew_members': crew_members,
        'volunteers': volunteers,
    }
    return render(request, 'pages/admin_reports.html', context)

def admin_users(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    users = User.objects.all().order_by('-date_joined')
    
    # Calculate real statistics
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    volunteers = users.filter(is_superuser=False).count()
    
    # Calculate new users this week
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    new_this_week = users.filter(date_joined__gte=week_ago).count()
    
    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'volunteers': volunteers,
        'new_this_week': new_this_week,
    }
    return render(request, 'pages/admin_users.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        print(f"Registration attempt: {username}, {email}, password length: {len(password)}")
        
        # Validation
        if not username:
            messages.error(request, 'Username is required.')
        elif not email:
            messages.error(request, 'Email is required.')
        elif not password:
            messages.error(request, 'Password is required.')
        elif len(password) < 3:  # Reduced minimum length for testing
            messages.error(request, 'Password must be at least 3 characters long.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                print(f"User created successfully: {user.username}")
                messages.success(request, 'Account created successfully! Please login.')
                return redirect('/login/')
            except Exception as e:
                print(f"Error creating user: {e}")
                messages.error(request, f'Error creating account: {str(e)}')
    return render(request, 'pages/register.html')

def mission(request):
    return render(request, 'pages/mission.html')

def vision(request):
    return render(request, 'pages/vision.html')

def training(request):
    return render(request, 'pages/training.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def user_dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access the dashboard.')
        return redirect('login')
    
    user_reports = WasteReport.objects.filter(user=request.user)
    total_reports = user_reports.count()
    completed_reports = user_reports.filter(status='completed').count()
    points = total_reports * 5  # 5 points per report
    
    # Calculate real rank from leaderboard
    from django.db.models import Count
    all_users = User.objects.filter(is_superuser=False, crewmember__isnull=True).annotate(
        total_reports=Count('wastereport')
    )
    
    users_data = []
    for user in all_users:
        user_points = user.total_reports * 5
        users_data.append({
            'user': user,
            'points': user_points
        })
    
    # Sort by points descending
    users_data.sort(key=lambda x: x['points'], reverse=True)
    
    # Find current user's rank
    user_rank = next((i+1 for i, data in enumerate(users_data) if data['user'] == request.user), None)
    
    context = {
        'total_reports': total_reports,
        'completed_reports': completed_reports,
        'points': points,
        'user_rank': user_rank,
    }
    return render(request, 'pages/user_dashboard.html', context)

@csrf_exempt
def report_waste(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create waste report
            report = WasteReport.objects.create(
                user=request.user if request.user.is_authenticated else None,
                location=data.get('location', ''),
                latitude=float(data.get('latitude')) if data.get('latitude') else None,
                longitude=float(data.get('longitude')) if data.get('longitude') else None,
                waste_type=data.get('wasteType', ''),
                severity=data.get('severity', ''),
                description=data.get('description', ''),
                image=data.get('image', ''),
                photo_timestamp=data.get('timestamp', '')
            )
            
            return JsonResponse({'success': True, 'message': 'Report submitted successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return render(request, 'pages/report_waste.html')

def leaderboard(request):
    # Get all users with their report counts and calculate points
    from django.db.models import Count
    
    users_data = []
    # Exclude crew members from leaderboard
    all_users = User.objects.filter(is_superuser=False, crewmember__isnull=True).annotate(
        total_reports=Count('wastereport'),
        completed_reports=Count('wastereport', filter=models.Q(wastereport__status='completed'))
    )
    
    for user in all_users:
        points = user.total_reports * 5  # 5 points per report
        users_data.append({
            'user': user,
            'total_reports': user.total_reports,
            'completed_reports': user.completed_reports,
            'points': points
        })
    
    # Sort by points descending
    users_data.sort(key=lambda x: x['points'], reverse=True)
    
    # Get current user's data if authenticated
    current_user_data = None
    if request.user.is_authenticated and not request.user.is_superuser:
        user_reports = WasteReport.objects.filter(user=request.user)
        total_reports = user_reports.count()
        completed_reports = user_reports.filter(status='completed').count()
        points = total_reports * 5  # 5 points per report
        
        # Find user's rank
        user_rank = next((i+1 for i, data in enumerate(users_data) if data['user'] == request.user), None)
        
        current_user_data = {
            'total_reports': total_reports,
            'completed_reports': completed_reports,
            'points': points,
            'rank': user_rank
        }
    
    context = {
        'users_data': users_data,
        'current_user_data': current_user_data,
    }
    return render(request, 'pages/leaderboard.html', context)

def dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access the dashboard.')
        return redirect('login')
    
    user_reports = WasteReport.objects.filter(user=request.user)
    total_reports = user_reports.count()
    completed_reports = user_reports.filter(status='completed').count()
    pending_reports = user_reports.filter(status='pending').count()
    points = total_reports * 5  # 5 points per report
    
    # Weekly activity data (current week as Week 1)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    weeks = int(request.GET.get('weeks', 4))
    weekly_data = []
    
    for i in range(weeks-1, -1, -1):
        week_start = today - timedelta(days=today.weekday() + 7*i)
        week_end = week_start + timedelta(days=6)
        reports_count = user_reports.filter(created_at__date__range=[week_start, week_end]).count()
        weekly_data.append(reports_count)
    
    context = {
        'total_reports': total_reports,
        'completed_reports': completed_reports,
        'pending_reports': pending_reports,
        'points': points,
        'user_reports': user_reports.order_by('-created_at'),
        'weekly_data': weekly_data,
        'weeks': weeks,
    }
    return render(request, 'pages/dashboard.html', context)

def volunteer_dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access the volunteer dashboard.')
        return redirect('login')
    
    # Get reports assigned to this volunteer
    assigned_reports = WasteReport.objects.filter(assigned_volunteer=request.user, status='assigned')
    in_progress_reports = WasteReport.objects.filter(assigned_volunteer=request.user, status='in_progress')
    completed_reports = WasteReport.objects.filter(assigned_volunteer=request.user, status='completed')
    
    context = {
        'assigned_reports': assigned_reports,
        'in_progress_reports': in_progress_reports,
        'completed_reports': completed_reports,
    }
    return render(request, 'pages/volunteer_dashboard.html', context)

@csrf_exempt
def organize_events(request):
    if request.method == 'POST':
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'message': 'Admin access required'})
            
        try:
            data = json.loads(request.body)
            event_id = data.get('event_id')
            
            if event_id:
                # Update existing event
                event = Event.objects.get(id=event_id)
                event.title = data.get('title')
                event.description = data.get('description', '')
                event.event_type = data.get('event_type')
                event.location = data.get('location')
                event.date = data.get('date')
                event.time = data.get('time')
                event.max_participants = int(data.get('max_participants', 50))
                event.save()
                return JsonResponse({'success': True, 'message': 'Event updated successfully!'})
            else:
                # Create new event
                event = Event.objects.create(
                    title=data.get('title'),
                    description=data.get('description', ''),
                    event_type=data.get('event_type'),
                    location=data.get('location'),
                    date=data.get('date'),
                    time=data.get('time'),
                    organizer=request.user,
                    max_participants=int(data.get('max_participants', 50))
                )
                return JsonResponse({'success': True, 'message': 'Event created successfully!'})
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    from datetime import date
    upcoming_events = Event.objects.filter(date__gte=date.today()).order_by('date', 'time')
    past_events = Event.objects.filter(date__lt=date.today()).order_by('-date', '-time')[:5]
    
    for event in upcoming_events:
        event.participant_count = EventParticipation.objects.filter(event=event).count()
        event.approved_count = EventParticipation.objects.filter(event=event, status='approved').count()
        # Check if current user has already joined this event
        if request.user.is_authenticated:
            event.user_joined = EventParticipation.objects.filter(
                event=event, 
                user=request.user, 
                status='approved'
            ).exists()
        else:
            event.user_joined = False
    
    for event in past_events:
        event.participant_count = EventParticipation.objects.filter(event=event).count()
        event.approved_count = EventParticipation.objects.filter(event=event, status='approved').count()
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'pages/organize_events.html', context)

def verify_reports(request):
    return render(request, 'pages/verify_reports.html')

@csrf_exempt
def assign_volunteer(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})
    
    try:
        data = json.loads(request.body)
        report_id = data.get('report_id')
        volunteer_id = data.get('volunteer_id')
        assignee_type = data.get('assignee_type', 'volunteer')
        
        if not report_id or not volunteer_id:
            return JsonResponse({'success': False, 'message': 'Missing required fields'})
        
        # Get report
        report = WasteReport.objects.get(id=report_id)
        
        # Get assignee
        assignee = User.objects.get(id=volunteer_id)
        
        # Check if already assigned
        if report.assigned_volunteer:
            return JsonResponse({
                'success': False, 
                'message': f'Report already assigned to {report.assigned_volunteer.username}'
            })
        
        # Assign the report
        report.assigned_volunteer = assignee
        report.status = 'assigned'
        report.assigned_at = timezone.now()
        report.save()
        
        assignee_title = 'crew member' if assignee_type == 'crew' else 'volunteer'
        
        return JsonResponse({
            'success': True, 
            'message': f'Report assigned to {assignee_title} {assignee.username} successfully!'
        })
        
    except WasteReport.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Report not found'})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

def admin_dashboard_simple(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    users = User.objects.all().order_by('-date_joined')
    reports = WasteReport.objects.all().order_by('-created_at')[:5]  # Latest 5 reports
    volunteers = User.objects.filter(is_superuser=False)
    crew_members = User.objects.filter(crewmember__isnull=False, crewmember__is_active=True).select_related('crewmember')
    
    # Calculate analytics data
    total_reports = WasteReport.objects.count()
    completed_reports = WasteReport.objects.filter(status='completed').count()
    pending_reports = WasteReport.objects.filter(status='pending').count()
    in_progress_reports = WasteReport.objects.filter(status='in_progress').count()
    resolution_rate = round((completed_reports / total_reports * 100) if total_reports > 0 else 0)
    
    context = {
        'users': users, 
        'reports': reports, 
        'volunteers': volunteers,
        'crew_members': crew_members,
        'total_reports': total_reports,
        'completed_reports': completed_reports,
        'pending_reports': pending_reports,
        'in_progress_reports': in_progress_reports,
        'resolution_rate': resolution_rate,
    }
    return render(request, 'pages/admin_dashboard_simple.html', context)

def community_management(request):
    return render(request, 'pages/community_management.html')

@csrf_exempt
def accept_report(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_id = data.get('report_id')
            
            report = WasteReport.objects.get(id=report_id, assigned_volunteer=request.user)
            report.status = 'in_progress'
            report.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Report accepted successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def reject_report(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_id = data.get('report_id')
            
            report = WasteReport.objects.get(id=report_id, assigned_volunteer=request.user)
            report.status = 'pending'
            report.assigned_volunteer = None
            report.assigned_at = None
            report.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Report rejected successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def complete_report(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_id = data.get('report_id')
            
            report = WasteReport.objects.get(id=report_id, assigned_volunteer=request.user)
            report.status = 'completed'
            report.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Report marked as completed'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def crew_dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access the crew dashboard.')
        return redirect('login')
    
    try:
        crew_member = CrewMember.objects.get(user=request.user)
    except CrewMember.DoesNotExist:
        messages.error(request, 'Access denied. Crew members only.')
        return redirect('home')
    
    # Get reports assigned to this crew member
    assigned_reports = WasteReport.objects.filter(assigned_volunteer=request.user, status='assigned')
    in_progress_reports = WasteReport.objects.filter(assigned_volunteer=request.user, status='in_progress')
    completed_reports = WasteReport.objects.filter(assigned_volunteer=request.user, status='completed')
    
    # Calculate stats
    total_assigned = assigned_reports.count() + in_progress_reports.count() + completed_reports.count()
    completion_rate = round((completed_reports.count() / total_assigned * 100) if total_assigned > 0 else 0)
    
    context = {
        'crew_member': crew_member,
        'assigned_reports': assigned_reports,
        'in_progress_reports': in_progress_reports,
        'completed_reports': completed_reports,
        'total_assigned': total_assigned,
        'completion_rate': completion_rate,
    }
    return render(request, 'pages/crew_dashboard.html', context)

@csrf_exempt
def crew_update_status(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        crew_member = CrewMember.objects.get(user=request.user)
    except CrewMember.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_id = data.get('report_id')
            new_status = data.get('status')
            
            report = WasteReport.objects.get(id=report_id, assigned_volunteer=request.user)
            report.status = new_status
            report.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Report status updated to {new_status}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def admin_crew(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    crew_members = CrewMember.objects.all().order_by('-created_at')
    
    context = {
        'crew_members': crew_members,
    }
    return render(request, 'pages/admin_crew.html', context)

@csrf_exempt
def admin_crew_add(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            employee_id = data.get('employee_id')
            phone = data.get('phone', '')
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Username already exists'})
            
            # Check if employee ID already exists
            if CrewMember.objects.filter(employee_id=employee_id).exists():
                return JsonResponse({'success': False, 'message': 'Employee ID already exists'})
            
            # Create user
            user = User.objects.create_user(username=username, password=password)
            
            # Create crew member
            crew_member = CrewMember.objects.create(
                user=user,
                employee_id=employee_id,
                phone=phone if phone else None
            )
            
            return JsonResponse({
                'success': True, 
                'message': f'Crew member {username} created successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def admin_crew_edit(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            crew_id = data.get('crew_id')
            username = data.get('username')
            employee_id = data.get('employee_id')
            phone = data.get('phone', '')
            is_active = data.get('is_active', True)
            
            crew_member = CrewMember.objects.get(id=crew_id)
            
            # Check if username is taken by another user
            if User.objects.filter(username=username).exclude(id=crew_member.user.id).exists():
                return JsonResponse({'success': False, 'message': 'Username already exists'})
            
            # Check if employee ID is taken by another crew member
            if CrewMember.objects.filter(employee_id=employee_id).exclude(id=crew_id).exists():
                return JsonResponse({'success': False, 'message': 'Employee ID already exists'})
            
            # Update user
            crew_member.user.username = username
            crew_member.user.save()
            
            # Update crew member
            crew_member.employee_id = employee_id
            crew_member.phone = phone if phone else None
            crew_member.is_active = is_active
            crew_member.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Crew member {username} updated successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def admin_crew_toggle(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            crew_id = data.get('crew_id')
            is_active = data.get('is_active')
            
            crew_member = CrewMember.objects.get(id=crew_id)
            crew_member.is_active = is_active
            crew_member.save()
            
            status_text = 'activated' if is_active else 'deactivated'
            return JsonResponse({
                'success': True, 
                'message': f'Crew member {crew_member.user.username} {status_text} successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def admin_crew_reset_password(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            new_password = data.get('new_password')
            
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Password reset successfully for {user.username}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def join_event(request):
    print(f"join_event called - Method: {request.method}")
    
    if request.method == 'POST':
        try:
            print(f"Request body: {request.body}")
            data = json.loads(request.body)
            event_id = data.get('event_id')
            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            experience = data.get('experience', '')
            availability = data.get('availability', '')
            
            print(f"Parsed data - event_id: {event_id}, name: {name}, email: {email}")
            
            if not event_id or not name or not email or not phone:
                return JsonResponse({'success': False, 'message': 'Missing required fields'})
            
            event = Event.objects.get(id=event_id)
            print(f"Found event: {event}")
            
            # Check if email already registered for this event
            existing = EventParticipation.objects.filter(event=event, email=email).first()
            if existing:
                return JsonResponse({'success': False, 'message': 'This email is already registered for this event'})
            
            # Check if event is full
            current_participants = EventParticipation.objects.filter(event=event, status__in=['pending', 'approved']).count()
            if current_participants >= event.max_participants:
                return JsonResponse({'success': False, 'message': 'Event is full'})
            
            print(f"Creating participation for {name}")
            
            # Create participation request with approved status
            participation = EventParticipation.objects.create(
                event=event,
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                phone=phone,
                experience=experience,
                availability=availability,
                status='approved'
            )
            
            print(f"Participation created: {participation}")
            
            return JsonResponse({
                'success': True, 
                'message': 'Successfully joined the event! You will receive further details soon.'
            })
        except Event.DoesNotExist:
            print(f"Event not found: {event_id}")
            return JsonResponse({'success': False, 'message': 'Event not found'})
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
        except Exception as e:
            print(f"Join event error: {e}")
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    print(f"Invalid method: {request.method}")
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def admin_event_participants(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    participants = EventParticipation.objects.all().order_by('-joined_at')
    events = Event.objects.all().order_by('-date')
    
    context = {
        'participants': participants,
        'events': events,
    }
    return render(request, 'pages/admin_event_participants.html', context)

@csrf_exempt
def get_event_participants(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'GET':
        event_id = request.GET.get('event_id')
        try:
            event = Event.objects.get(id=event_id)
            participants = EventParticipation.objects.filter(event=event, status='approved').order_by('-joined_at')
            
            participants_data = []
            for participant in participants:
                participants_data.append({
                    'name': participant.name,
                    'email': participant.email,
                    'phone': participant.phone,
                    'experience': participant.experience,
                    'availability': participant.availability,
                    'joined_at': participant.joined_at.strftime('%b %d, %Y at %I:%M %p')
                })
            
            return JsonResponse({
                'success': True,
                'participants': participants_data
            })
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def get_event_details(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'GET':
        event_id = request.GET.get('event_id')
        try:
            event = Event.objects.get(id=event_id)
            return JsonResponse({
                'success': True,
                'event': {
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'event_type': event.event_type,
                    'location': event.location,
                    'date': event.date.strftime('%Y-%m-%d'),
                    'time': event.time.strftime('%H:%M'),
                    'max_participants': event.max_participants
                }
            })
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def delete_event(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_id = data.get('event_id')
            event = Event.objects.get(id=event_id)
            event_title = event.title
            event.delete()
            return JsonResponse({'success': True, 'message': f'Event "{event_title}" deleted successfully!'})
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def delete_user(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
            if user.is_superuser:
                return JsonResponse({'success': False, 'message': 'Cannot delete admin users'})
            username = user.username
            user.delete()
            return JsonResponse({'success': True, 'message': f'User "{username}" deleted successfully!'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def delete_crew_member(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            crew_id = data.get('crew_id')
            crew_member = CrewMember.objects.get(id=crew_id)
            username = crew_member.user.username
            crew_member.user.delete()  # This will also delete the crew member due to CASCADE
            return JsonResponse({'success': True, 'message': f'Crew member "{username}" deleted successfully!'})
        except CrewMember.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Crew member not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def delete_participant(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            participant_id = data.get('participant_id')
            participation = EventParticipation.objects.get(id=participant_id)
            name = participation.name
            participation.delete()
            return JsonResponse({'success': True, 'message': f'Participant "{name}" removed successfully!'})
        except EventParticipation.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Participant not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def delete_report(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_id = data.get('report_id')
            report = WasteReport.objects.get(id=report_id)
            report.delete()
            return JsonResponse({'success': True, 'message': 'Report deleted successfully!'})
        except WasteReport.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Report not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def admin_approve_participant(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            participant_id = data.get('participant_id')
            action = data.get('action')  # 'approve' or 'reject'
            
            participation = EventParticipation.objects.get(id=participant_id)
            
            if action == 'approve':
                # Check if event is full
                current_approved = EventParticipation.objects.filter(
                    event=participation.event, 
                    status='approved'
                ).count()
                
                if current_approved >= participation.event.max_participants:
                    return JsonResponse({'success': False, 'message': 'Event is already full'})
                
                participation.status = 'approved'
                message = f'{participation.name} has been approved for {participation.event.title}'
            else:
                participation.status = 'rejected'
                message = f'{participation.name} has been rejected for {participation.event.title}'
            
            participation.save()
            
            return JsonResponse({
                'success': True, 
                'message': message
            })
        except EventParticipation.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Participant not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def system_analytics(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    # Calculate comprehensive analytics
    total_reports = WasteReport.objects.count()
    completed_reports = WasteReport.objects.filter(status='completed').count()
    pending_reports = WasteReport.objects.filter(status='pending').count()
    in_progress_reports = WasteReport.objects.filter(status='in_progress').count()
    assigned_reports = WasteReport.objects.filter(status='assigned').count()
    
    # User analytics
    total_users = User.objects.filter(is_superuser=False).count()
    total_crew = CrewMember.objects.filter(is_active=True).count()
    
    # Event analytics
    total_events = Event.objects.count()
    total_participants = EventParticipation.objects.filter(status='approved').count()
    
    # Calculate rates
    resolution_rate = round((completed_reports / total_reports * 100) if total_reports > 0 else 0)
    
    context = {
        'total_reports': total_reports,
        'completed_reports': completed_reports,
        'pending_reports': pending_reports,
        'in_progress_reports': in_progress_reports,
        'assigned_reports': assigned_reports,
        'total_users': total_users,
        'total_crew': total_crew,
        'total_events': total_events,
        'total_participants': total_participants,
        'resolution_rate': resolution_rate,
    }
    return render(request, 'pages/system_analytics.html', context)

@csrf_exempt
def mark_message_read(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message_id = data.get('message_id')
            message = ContactMessage.objects.get(id=message_id)
            message.is_read = True
            message.save()
            return JsonResponse({'success': True, 'message': 'Message marked as read'})
        except ContactMessage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Message not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def search_reports(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    search_query = request.GET.get('q', '')
    waste_type = request.GET.get('waste_type', '')
    severity = request.GET.get('severity', '')
    status = request.GET.get('status', '')
    
    reports = WasteReport.objects.all().order_by('-created_at')
    
    if search_query:
        from django.db.models import Q
        reports = reports.filter(
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    if waste_type:
        reports = reports.filter(waste_type=waste_type)
    if severity:
        reports = reports.filter(severity=severity)
    if status:
        reports = reports.filter(status=status)
    
    reports_data = []
    for report in reports[:20]:  # Limit to 20 results
        reports_data.append({
            'id': report.id,
            'waste_type': report.get_waste_type_display(),
            'severity': report.get_severity_display(),
            'location': report.location,
            'description': report.description[:50] + '...' if len(report.description) > 50 else report.description,
            'status': report.get_status_display(),
            'user': report.user.username if report.user else 'Anonymous',
            'assigned_volunteer': report.assigned_volunteer.username if report.assigned_volunteer else None,
            'created_at': report.created_at.strftime('%b %d, %Y %I:%M %p'),
            'image': report.image if report.image else None
        })
    
    return JsonResponse({'success': True, 'reports': reports_data})

@csrf_exempt
def search_events(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    search_query = request.GET.get('q', '')
    event_type = request.GET.get('event_type', '')
    date_filter = request.GET.get('date_filter', '')
    
    events = Event.objects.all().order_by('-date')
    
    if search_query:
        from django.db.models import Q
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(organizer__username__icontains=search_query)
        )
    
    if event_type:
        events = events.filter(event_type=event_type)
    
    if date_filter == 'upcoming':
        from datetime import date
        events = events.filter(date__gte=date.today())
    elif date_filter == 'past':
        from datetime import date
        events = events.filter(date__lt=date.today())
    
    events_data = []
    for event in events[:20]:
        participant_count = EventParticipation.objects.filter(event=event, status='approved').count()
        events_data.append({
            'id': event.id,
            'title': event.title,
            'event_type': event.get_event_type_display(),
            'location': event.location,
            'date': event.date.strftime('%b %d, %Y'),
            'time': event.time.strftime('%I:%M %p'),
            'organizer': event.organizer.username,
            'participants': participant_count,
            'max_participants': event.max_participants
        })
    
    return JsonResponse({'success': True, 'events': events_data})

@csrf_exempt
def search_users(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    search_query = request.GET.get('q', '')
    user_type = request.GET.get('user_type', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if search_query:
        from django.db.models import Q
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if user_type == 'admin':
        users = users.filter(is_superuser=True)
    elif user_type == 'crew':
        users = users.filter(crewmember__isnull=False)
    elif user_type == 'regular':
        users = users.filter(is_superuser=False, crewmember__isnull=True)
    
    users_data = []
    for user in users[:20]:
        report_count = WasteReport.objects.filter(user=user).count()
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined.strftime('%b %d, %Y'),
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'report_count': report_count,
            'is_crew': hasattr(user, 'crewmember')
        })
    
    return JsonResponse({'success': True, 'users': users_data})

@csrf_exempt
def search_messages(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    search_query = request.GET.get('q', '')
    read_status = request.GET.get('read_status', '')
    
    messages = ContactMessage.objects.all().order_by('-created_at')
    
    if search_query:
        from django.db.models import Q
        messages = messages.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    if read_status == 'read':
        messages = messages.filter(is_read=True)
    elif read_status == 'unread':
        messages = messages.filter(is_read=False)
    
    messages_data = []
    for msg in messages[:20]:
        messages_data.append({
            'id': msg.id,
            'name': msg.name,
            'email': msg.email,
            'subject': msg.subject,
            'message': msg.message[:100] + '...' if len(msg.message) > 100 else msg.message,
            'created_at': msg.created_at.strftime('%b %d, %Y %I:%M %p'),
            'is_read': msg.is_read
        })
    
    return JsonResponse({'success': True, 'messages': messages_data})

def redeem_points(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access the redeem points page.')
        return redirect('login')
    
    # Calculate user points
    user_reports = WasteReport.objects.filter(user=request.user)
    total_reports = user_reports.count()
    user_points = total_reports * 5  # 5 points per report
    
    context = {
        'user_points': user_points,
    }
    return render(request, 'pages/redeem_points.html', context)


