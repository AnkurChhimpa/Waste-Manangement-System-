"""
URL configuration for wastemanagement project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('project.urls')),
    path('chatbot/', include('chatbot.urls')),
]
