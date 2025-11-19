# core/urls.py

from django.contrib import admin
from django.urls import path, include  # <-- Asegúrate de tener 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea es la clave:
    path('', include('bartender_app.urls')),
]