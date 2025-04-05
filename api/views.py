from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import TripInputSerializer, TripLogSerializer
from .services.route_planner import RoutePlanner
from .services.hours_of_service import HoursOfService
from .services.edl_generator import ELDGenerator
from .models import TripLog

class GenerateRouteView(APIView):
    """API view to generate route information"""
    
    def post(self, request):
        serializer = TripInputSerializer(data=request.data)
        if serializer.is_valid():
            current_location = serializer.validated_data['current_location']
            pickup_location = serializer.validated_data['pickup_location']
            dropoff_location = serializer.validated_data['dropoff_location']
            
            route_planner = RoutePlanner()
            route_data = route_planner.plan_complete_route(
                current_location, pickup_location, dropoff_location
            )
            
            if route_data:
                return Response(route_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Could not generate route. Please check the locations.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GenerateELDLogsView(APIView):
    """API view to generate ELD logs"""
    
    def post(self, request):
        serializer = TripInputSerializer(data=request.data)
        if serializer.is_valid():
            current_location = serializer.validated_data['current_location']
            pickup_location = serializer.validated_data['pickup_location']
            dropoff_location = serializer.validated_data['dropoff_location']
            current_cycle_hours = serializer.validated_data['current_cycle_hours']
            route_planner = RoutePlanner()
            route_data = route_planner.plan_complete_route(
                current_location, pickup_location, dropoff_location
            )
            
            if not route_data:
                return Response(
                    {'error': 'Could not generate route. Please check the locations.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            hos_calculator = HoursOfService()
            hos_data = hos_calculator.calculate_required_stops(route_data, current_cycle_hours)
            
            eld_generator = ELDGenerator()
            logs = eld_generator.generate_logs(route_data, hos_data, current_cycle_hours)
            
            trip_log = TripLog.objects.create(
                current_location=current_location,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                current_cycle_hours=current_cycle_hours,
                route_data=route_data,
                log_data=logs
            )
            
            response_data = {
                'route': route_data,
                'hos': hos_data,
                'logs': logs,
                'trip_id': trip_log.id
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)