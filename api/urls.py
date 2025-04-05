from django.urls import path
from .views import GenerateRouteView, GenerateELDLogsView

urlpatterns = [
    path('generate-route/', GenerateRouteView.as_view(), name='generate-route'),
    path('generate-eld-logs/', GenerateELDLogsView.as_view(), name='generate-eld-logs'),
]