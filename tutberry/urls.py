from django.urls import path
from tutberry.views import health, version

urlpatterns = [path('health', health), path('version', version)]
