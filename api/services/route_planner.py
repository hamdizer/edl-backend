import requests

class RoutePlanner:
    def __init__(self):
        self.geocode_url = "https://api.openrouteservice.org/geocode/search"
        self.directions_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        self.api_key = "5b3ce3597851110001cf6248f6083129c02d4805b29e8f82e8a23494"  # Replace with your key

    def geocode_location(self, location):
        """Geocode a location (convert address to coordinates)"""
        params = {
            'api_key': self.api_key,
            'text': location,
            'size': 1
        }
        try:
            response = requests.get(self.geocode_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('features'):
                coords = data['features'][0]['geometry']['coordinates']  
                place_name = data['features'][0]['properties']['label']
                return {'coordinates': coords, 'place_name': place_name}
            return None
        except requests.exceptions.RequestException as e:
            print(f"Geocoding error for '{location}': {e}")
            return None

    def get_route(self, start_coords, end_coords):
        """Get route between two coordinates"""
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        body = {
            "coordinates": [start_coords, end_coords],
            "instructions": "false"
        }
        try:
            response = requests.post(self.directions_url, json=body, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Routing error: {e}")
            return None

    def plan_complete_route(self, current_loc, pickup_loc, dropoff_loc):
        """Plan full route with current → pickup → dropoff"""
        current = self.geocode_location(current_loc)
        pickup = self.geocode_location(pickup_loc)
        dropoff = self.geocode_location(dropoff_loc)

        if not all([current, pickup, dropoff]):
            print("Error: Could not geocode all locations")
            return None

        leg1 = self.get_route(current['coordinates'], pickup['coordinates'])
        leg2 = self.get_route(pickup['coordinates'], dropoff['coordinates'])

        if not all([leg1, leg2]):
            print("Error: Could not generate route legs")
            return None

        return {
            'waypoints': {
                'start': current['place_name'],
                'pickup': pickup['place_name'],
                'end': dropoff['place_name']
            },
            'routes': [leg1, leg2],
            'total_distance': sum(route['routes'][0]['summary']['distance'] for route in [leg1, leg2]),
            'total_duration': sum(route['routes'][0]['summary']['duration'] for route in [leg1, leg2])
        }
        """Geocode a location (convert address to coordinates) using OpenRouteService."""
        params = {
            'q': location,
            'api_key': self.api_key
        }
        try:
            response = requests.get(self.geocode_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('features'):
                coords = data['features'][0]['geometry']['coordinates']  # [lng, lat]
                place_name = data['features'][0]['properties']['label']
                return {'coordinates': coords, 'place_name': place_name}
            return None
        except requests.exceptions.RequestException as e:
            print(f"Geocoding error for '{location}': {e}")
            return None

    def get_route(self, start_coords, end_coords):
        """Get route between two coordinates using OpenRouteService Directions API."""
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        body = {
            "coordinates": [start_coords, end_coords],
            "instructions": "true"
        }
        try:
            response = requests.post(self.directions_url, json=body, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Routing error: {e}")
            return None

    def plan_complete_route(self, current_loc, pickup_loc, dropoff_loc):
        """Plan a full route with three legs: current → pickup → dropoff."""
        current = self.geocode_location(current_loc)  
        pickup = self.geocode_location(pickup_loc)    
        dropoff = self.geocode_location(dropoff_loc)  

        if not all([current, pickup, dropoff]):
            print("Error: Could not geocode one or more locations.")
            return None

        leg1 = self.get_route(current['coordinates'], pickup['coordinates'])
        leg2 = self.get_route(pickup['coordinates'], dropoff['coordinates'])

        if not all([leg1, leg2]):
            print("Error: Could not generate route legs.")
            return None

        total_distance = leg1['routes'][0]['summary']['distance'] + leg2['routes'][0]['summary']['distance']
        total_duration = leg1['routes'][0]['summary']['duration'] + leg2['routes'][0]['summary']['duration']

        return {
            'current_location': current['place_name'],
            'pickup_location': pickup['place_name'],
            'dropoff_location': dropoff['place_name'],
            'legs': [leg1, leg2],
            'total_distance': total_distance,  
            'total_duration': total_duration 
        }


    
    def _interpolate_point(self, coordinates, percentage):
        """Find a point along a polyline at a given percentage of the total distance"""
        if percentage <= 0:
            return coordinates[0]
        if percentage >= 1:
            return coordinates[-1]
            
        total_segments = len(coordinates) - 1
        target_segment = int(total_segments * percentage)
        
        return coordinates[target_segment]
