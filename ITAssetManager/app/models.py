from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Model representing equipment information
class Equipment(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('broken', 'Broken'),
    ]
    
    # Equipment usage status options
    USAGE_STATUS_CHOICES = [
        ('free', 'Free'),
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('in_repair', 'In Repair'), 
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)  # Nullable and blankable
    purchased_date = models.DateField(default=date.today)  # Default to current day
    serial_number = models.CharField(max_length=100, unique=True)
    assigned_users = models.ManyToManyField(User, blank=True) 
    condition_status = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new')
    usage_status = models.CharField(max_length=15, choices=USAGE_STATUS_CHOICES, default='free')
    stock = models.PositiveIntegerField(default=0)  

    def __str__(self):
        return self.name # Display equipment name in admin or debug views

class Employee(models.Model):
    POSITION_CHOICES = [
        ('manager', 'Manager'),
        ('technician', 'Technician'),
        ('intern', 'Intern'),
        ('engineer', 'Engineer'),
        ('contractor', 'Contractor'),
        ('receptionist', 'Receptionist'),
        ('hr manager', 'Hr Manager'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Nullable and blankable
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='intern')
    hire_date = models.DateField(default=date.today)  # Default to current day
    equipment = models.ManyToManyField(Equipment, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ErrorLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    error_message = models.TextField()
    severity = models.CharField(max_length=10, choices=[
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ], default='error')  # Default severity level
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"Error by {user_str} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {self.error_message[:50]}..."  # Display a snippet of the message

    class Meta:
        ordering = ['-timestamp']  # Order by timestamp, newest first