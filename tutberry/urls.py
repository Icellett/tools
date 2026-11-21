from django.urls import path

from tutberry.api_booking import create_booking
from tutberry.views import health, version

urlpatterns = [path('health', health), path('version', version), path('api/bookings', create_booking)]
