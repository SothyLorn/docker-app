from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.db import connection
import socket
import os

def home(request):
    # Test database connection
    db_status = 'connected'
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return JsonResponse({
        'message': 'Hello from Django!',
        'hostname': socket.gethostname(),
        'environment': os.getenv('APP_ENV', 'development'),
        'database': db_status
    })

def health(request):
    return JsonResponse({'status': 'healthy'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('health/', health),
]
