from django.db import models
from django.contrib.auth.models import User

class CrewMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"

class WasteReport(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    WASTE_TYPE_CHOICES = [
        ('plastic', 'Plastic Waste'),
        ('organic', 'Organic Waste'),
        ('electronic', 'Electronic Waste'),
        ('hazardous', 'Hazardous Waste'),
        ('construction', 'Construction Debris'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=500)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    description = models.TextField()
    image = models.TextField(blank=True)  # Base64 image data
    photo_timestamp = models.CharField(max_length=50, blank=True, null=True)  # When photo was taken
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_volunteer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_reports')
    assigned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.waste_type} - {self.location} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('cleanup', 'Cleanup Drive'),
        ('awareness', 'Awareness Campaign'),
        ('workshop', 'Workshop'),
        ('tree_planting', 'Tree Planting'),
        ('recycling', 'Recycling Drive'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    location = models.CharField(max_length=500)
    date = models.DateField()
    time = models.TimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    max_participants = models.IntegerField(default=50)
    participants = models.ManyToManyField(User, related_name='joined_events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'time']
    
    def __str__(self):
        return f"{self.title} - {self.date}"

class EventParticipation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    experience = models.TextField(blank=True)
    availability = models.CharField(max_length=200)
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ['event', 'email']  # Prevent duplicate emails per event
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.name} - {self.event.title}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
