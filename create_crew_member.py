#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastemanagement.settings')
django.setup()

from django.contrib.auth.models import User
from project.models import CrewMember

def create_crew_member():
    # Create a test crew member
    username = input("Enter username for crew member: ")
    password = input("Enter password: ")
    employee_id = input("Enter employee ID: ")
    phone = input("Enter phone number (optional): ")
    
    try:
        # Create user
        user = User.objects.create_user(username=username, password=password)
        
        # Create crew member profile
        crew_member = CrewMember.objects.create(
            user=user,
            employee_id=employee_id,
            phone=phone
        )
        
        print(f"Crew member {username} created successfully with ID: {employee_id}")
        
    except Exception as e:
        print(f"Error creating crew member: {e}")

if __name__ == "__main__":
    create_crew_member()