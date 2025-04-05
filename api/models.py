from django.db import models
from django.utils import timezone


class TripLog(models.Model):
    """Model to store trip information and generated logs"""
    created_at = models.DateTimeField(auto_now_add=True)
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_hours = models.FloatField()
    route_data = models.JSONField()
    driver = models.CharField(max_length=100)
    start_time = models.DateTimeField(null=True, blank=True,default=timezone.now)  
    end_time = models.DateTimeField(null=True, blank=True,default=timezone.now)
    log_data = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.current_location} to {self.dropoff_location}"