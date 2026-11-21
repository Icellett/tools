from django.urls import path
from tutberry.views import health, version
from tutberry.api_booking import create_booking

urlpatterns = [path('health', health), path('version', version), path('api/bookings', create_booking)]
