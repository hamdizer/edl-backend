import math
from datetime import datetime, timedelta

class HoursOfService:
    """Service to calculate Hours of Service (HOS) requirements"""
    
    def __init__(self):
        self.PROPERTY_CARRYING_LIMITS = {
            'driving_window': 14, 
            'max_driving': 11,     
            'required_break': 0.5,  
            'min_off_duty': 10,
            'cycle_limit': 70,   
        }
        self.AVERAGE_SPEED = 55    
    
    def calculate_driving_time(self, distance):
        """Calculate driving time based on distance and average speed"""
        return distance / self.AVERAGE_SPEED
    
    def calculate_required_stops(self, route_data, current_cycle_hours):
        """Calculate required rest stops based on HOS regulations"""
        total_distance = route_data['total_distance']
        total_duration = route_data['total_duration']
        
        available_cycle_hours = 70 - current_cycle_hours
        
        driving_time = self.calculate_driving_time(total_distance)
        
        days_required = math.ceil(driving_time / self.PROPERTY_CARRYING_LIMITS['max_driving'])
        
        rest_stops = []
        
        remaining_distance = total_distance
        current_distance = 0
        current_time = datetime.now()
        
        for day in range(days_required):
            day_start_time = current_time
            
            max_driving_today = min(
                self.PROPERTY_CARRYING_LIMITS['max_driving'],
                available_cycle_hours,
                self.PROPERTY_CARRYING_LIMITS['driving_window'] - 1  
            )
            
            distance_today = min(remaining_distance, max_driving_today * self.AVERAGE_SPEED)
            
            if max_driving_today > 8:
                break_distance = 8 * self.AVERAGE_SPEED
                break_time = day_start_time + timedelta(hours=8)
                
                break_coordinates = self._find_coordinates_at_distance(route_data, current_distance + break_distance)
                
                rest_stops.append({
                    'type': 'break',
                    'duration': 0.5,  
                    'distance_from_start': current_distance + break_distance,
                    'time': break_time.strftime('%Y-%m-%d %H:%M'),
                    'coordinates': break_coordinates
                })
            
            current_distance += distance_today
            remaining_distance -= distance_today
            
            if day < days_required - 1:  
                off_duty_time = day_start_time + timedelta(hours=max_driving_today + 1)  
                
                off_duty_coordinates = self._find_coordinates_at_distance(route_data, current_distance)
                
                rest_stops.append({
                    'type': 'off_duty',
                    'duration': self.PROPERTY_CARRYING_LIMITS['min_off_duty'],
                    'distance_from_start': current_distance,
                    'time': off_duty_time.strftime('%Y-%m-%d %H:%M'),
                    'coordinates': off_duty_coordinates
                })
                
                current_time = off_duty_time + timedelta(hours=self.PROPERTY_CARRYING_LIMITS['min_off_duty'])
                
                available_cycle_hours -= (max_driving_today + 1)  
            
        return {
            'days_required': days_required,
            'rest_stops': rest_stops,
            'total_driving_time': driving_time
        }
    
    def _find_coordinates_at_distance(self, route_data, target_distance):
        """Find coordinates at a specific distance along the route"""
        accumulated_distance = 0
        coordinates = []
        
        for leg in route_data['legs']:
            for route in leg['routes']:
                if 'geometry' in route and 'coordinates' in route['geometry']:
                    leg_coords = route['geometry']['coordinates']
                    coordinates.extend(leg_coords)
                    accumulated_distance += route['summary']['distance']
        
        if coordinates:
            total_distance = route_data['total_distance']
            if target_distance > total_distance:
                target_distance = total_distance
            percentage = target_distance / total_distance
            point_index = int(len(coordinates) * percentage)
            return coordinates[min(point_index, len(coordinates) - 1)]
        
        return None
