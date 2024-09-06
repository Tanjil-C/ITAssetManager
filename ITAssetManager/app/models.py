from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Model to represent categories of IT assets.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    """
    Model to represent IT assets.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=255)
    purchase_date = models.DateField()
    asset_id = models.CharField(max_length=100, unique=True)
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.name} ({self.asset_id})"
