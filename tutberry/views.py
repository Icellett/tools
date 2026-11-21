from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health(request):
    return Response({'status': 'ok'})

@api_view(['GET'])
def version(request):
    return Response({'version': settings.APP_VERSION, 'environment': 'development' if settings.DEBUG else 'production'})
