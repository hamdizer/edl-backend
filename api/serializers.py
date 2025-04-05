from rest_framework import serializers
from .models import TripLog

class TripInputSerializer(serializers.Serializer):
    """Serializer for trip input data"""
    current_location = serializers.CharField(max_length=255)
    pickup_location = serializers.CharField(max_length=255)
    dropoff_location = serializers.CharField(max_length=255)
    current_cycle_hours = serializers.FloatField(min_value=0, max_value=70)

class TripLogSerializer(serializers.ModelSerializer):
    """Serializer for TripLog model"""
    start_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')  
    class Meta:
        model = TripLog
        fields = '__all__'
    
    def to_representation(self, instance):
        """Override to_representation to handle datetime serialization"""
        representation = super().to_representation(instance)
        
        if 'start_time' in representation:
            representation['start_time'] = instance.start_time.isoformat() 
        
        return representation