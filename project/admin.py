from django.contrib import admin
from .models import WasteReport, Event, CrewMember, ContactMessage

@admin.register(WasteReport)
class WasteReportAdmin(admin.ModelAdmin):
    list_display = ['waste_type', 'location', 'severity', 'status', 'assigned_volunteer', 'created_at']
    list_filter = ['status', 'waste_type', 'severity', 'created_at']
    search_fields = ['location', 'description']
    ordering = ['-created_at']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'location', 'date', 'time', 'organizer']
    list_filter = ['event_type', 'date']
    search_fields = ['title', 'location']
    ordering = ['date', 'time']

@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'employee_id', 'phone']
    ordering = ['-created_at']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject']
    ordering = ['-created_at']
