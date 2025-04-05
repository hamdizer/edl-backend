import math
from datetime import datetime, timedelta

class ELDGenerator:
    """Service to generate Electronic Logging Device (ELD) logs"""
    
    def __init__(self):
        self.DRIVING_STATUS = 3     
        self.ON_DUTY_STATUS = 1    
        self.OFF_DUTY_STATUS = 4   
        self.SLEEPER_BERTH_STATUS = 2 
    
    def generate_logs(self, route_data, hours_of_service_data, current_cycle_hours):
        """Generate ELD logs based on route and HOS data"""
        total_distance = route_data['total_distance']
        days_required = hours_of_service_data['days_required']
        rest_stops = hours_of_service_data['rest_stops']
        
        logs = []
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time().replace(minute=0, second=0, microsecond=0)  # Round to hour
        
        current_location = route_data['current_location']
        pickup_location = route_data['pickup_location']
        dropoff_location = route_data['dropoff_location']
        
        for day in range(days_required):
            log_sheet = self._create_empty_log_sheet(current_date)
            log_sheet['total_miles'] = 0
            
            if day == 0:
                self._add_log_entry(
                    log_sheet=log_sheet,
                    status=self.ON_DUTY_STATUS,
                    start_time=current_time,
                    duration_hours=0.25,
                    location=current_location,
                    remark="Pre-trip inspection",
                    start_datetime=datetime.combine(current_date, current_time)
                )
                current_time = self._add_hours(current_time, 0.25)
            
            if day == 0:
                pickup_distance = route_data['legs'][0]['routes'][0]['summary']['distance']
                pickup_time = pickup_distance / 55  
                
                self._add_log_entry(
                    log_sheet=log_sheet,
                    status=self.DRIVING_STATUS,
                    start_time=current_time,
                    duration_hours=pickup_time,
                    location=current_location,
                    remark=f"Driving to pickup at {pickup_location}",
                    start_datetime=datetime.combine(current_date, current_time)
                )
                current_time = self._add_hours(current_time, pickup_time)
                current_location = pickup_location
                log_sheet['total_miles'] += pickup_distance
                
                self._add_log_entry(
                    log_sheet=log_sheet,
                    status=self.ON_DUTY_STATUS,
                    start_time=current_time,
                    duration_hours=1,
                    location=current_location,
                    remark="Loading at pickup",
                    start_datetime=datetime.combine(current_date, current_time)
                )
                current_time = self._add_hours(current_time, 1)
            
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = day_start + timedelta(days=1)
            
            day_rest_stops = []
            for stop in rest_stops:
                try:
                    stop_time = datetime.strptime(stop['time'].split('.')[0], '%Y-%m-%d %H:%M')
                    if day_start <= stop_time < day_end:
                        day_rest_stops.append(stop)
                except ValueError:
                    try:
                        stop_time = datetime.strptime(stop['time'], '%Y-%m-%d %H:%M')
                        if day_start <= stop_time < day_end:
                            day_rest_stops.append(stop)
                    except ValueError:
                        continue
            
            remaining_distance = min(11 * 55, total_distance - log_sheet['total_miles'])  
            
            for stop in day_rest_stops:
                distance_to_stop = stop['distance_from_start'] - log_sheet['total_miles']
                if distance_to_stop > 0:
                    driving_time = distance_to_stop / 55  
                    self._add_log_entry(
                        log_sheet=log_sheet,
                        status=self.DRIVING_STATUS,
                        start_time=current_time,
                        duration_hours=driving_time,
                        location=current_location,
                        remark="Driving",
                        start_datetime=datetime.combine(current_date, current_time)
                    )
                    current_time = self._add_hours(current_time, driving_time)
                    log_sheet['total_miles'] += distance_to_stop
                
                stop_time_str = stop['time'].split('.')[0]  # Remove fractional seconds
                try:
                    stop_datetime = datetime.strptime(stop_time_str, '%Y-%m-%d %H:%M')
                except ValueError:
                    stop_datetime = datetime.combine(current_date, current_time)
                
                if stop['type'] == 'break':
                    self._add_log_entry(
                        log_sheet=log_sheet,
                        status=self.OFF_DUTY_STATUS,
                        start_time=current_time,
                        duration_hours=stop['duration'],
                        location=str(stop['coordinates']),
                        remark="30-minute break",
                        start_datetime=stop_datetime
                    )
                elif stop['type'] == 'off_duty':
                    self._add_log_entry(
                        log_sheet=log_sheet,
                        status=self.SLEEPER_BERTH_STATUS,
                        start_time=current_time,
                        duration_hours=stop['duration'],
                        location=str(stop['coordinates']),
                        remark="10-hour rest period",
                        start_datetime=stop_datetime
                    )
                
                current_time = self._add_hours(current_time, stop['duration'])
            
            if day == days_required - 1:
                dropoff_distance = total_distance - log_sheet['total_miles']
                if dropoff_distance > 0:
                    dropoff_time = dropoff_distance / 55 
                    
                    self._add_log_entry(
                        log_sheet=log_sheet,
                        status=self.DRIVING_STATUS,
                        start_time=current_time,
                        duration_hours=dropoff_time,
                        location=current_location,
                        remark=f"Driving to dropoff at {dropoff_location}",
                        start_datetime=datetime.combine(current_date, current_time)
                    )
                    current_time = self._add_hours(current_time, dropoff_time)
                    current_location = dropoff_location
                    log_sheet['total_miles'] += dropoff_distance
                
                self._add_log_entry(
                    log_sheet=log_sheet,
                    status=self.ON_DUTY_STATUS,
                    start_time=current_time,
                    duration_hours=1,
                    location=current_location,
                    remark="Unloading at dropoff",
                    start_datetime=datetime.combine(current_date, current_time)
                )
                current_time = self._add_hours(current_time, 1)
                
                self._add_log_entry(
                    log_sheet=log_sheet,
                    status=self.ON_DUTY_STATUS,
                    start_time=current_time,
                    duration_hours=0.25,
                    location=current_location,
                    remark="Post-trip inspection",
                    start_datetime=datetime.combine(current_date, current_time)
                )
                current_time = self._add_hours(current_time, 0.25)
            
            self._fill_log_grid(log_sheet)
            logs.append(log_sheet)
            
            current_date += timedelta(days=1)
            current_time = datetime.min.time()  
        
        return self._prepare_for_json(logs)  
    
    def _prepare_for_json(self, logs):
        """Convert datetime objects to ISO format strings for JSON serialization"""
        serializable_logs = []
        
        for log in logs:
            serializable_log = dict(log)  
            serializable_entries = []
            
            for entry in log['entries']:
                serializable_entry = dict(entry)  
                if 'start_datetime' in serializable_entry:
                    serializable_entry['start_datetime'] = serializable_entry['start_datetime'].isoformat()
                if 'end_datetime' in serializable_entry:
                    serializable_entry['end_datetime'] = serializable_entry['end_datetime'].isoformat()
                serializable_entries.append(serializable_entry)
            
            serializable_log['entries'] = serializable_entries
            serializable_logs.append(serializable_log)
        
        return serializable_logs
    
    def _create_empty_log_sheet(self, date):
        """Create an empty log sheet for a given date"""
        return {
            'date': date.strftime('%Y-%m-%d'),
            'entries': [],
            'grid': [0] * 24 * 4, 
            'total_miles': 0,
            'from': '',
            'to': '',
            'carrier': 'ELD Logger',
            'driver': 'Test Driver',
            'truck_number': 'TEST123',
            'remarks': []
        }
    
    def _add_log_entry(self, log_sheet, status, start_time, duration_hours, location, remark, start_datetime):
        """Add a log entry to the log sheet with proper datetime handling"""
        end_time = self._add_hours(start_time, duration_hours)
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        
        log_sheet['entries'].append({
            'status': status,
            'start_time': start_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
            'duration': duration_hours,
            'location': location,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'remark': remark
        })
        
        log_sheet['remarks'].append(f"{start_time.strftime('%H:%M')} - {remark}")
        
        if not log_sheet['from']:
            log_sheet['from'] = location
        log_sheet['to'] = location
    
    def _add_hours(self, time, hours):
        """Add hours to a time object, handling day overflow"""
        datetime_obj = datetime.combine(datetime.now().date(), time)
        new_datetime = datetime_obj + timedelta(hours=hours)
        return new_datetime.time()
    
    def _fill_log_grid(self, log_sheet):
        """Fill the log grid for visualization"""
        grid = [0] * (24 * 4)  
        
        for entry in log_sheet['entries']:
            start_time = entry['start_datetime']
            end_time = entry['end_datetime']
            
            start_idx = (start_time.hour * 4) + (start_time.minute // 15)
            end_idx = (end_time.hour * 4) + (end_time.minute // 15)
            
            if end_idx <= start_idx:
                end_idx += 24 * 4  
            
            for i in range(start_idx, end_idx):
                grid[i % (24 * 4)] = entry['status']
        
        log_sheet['grid'] = grid
