# bartender_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Esta ruta vacía ('') es la que responde cuando accedes a http://127.0.0.1:8000/
    path('', views.bartender_interface, name='bartender_interface'),
    path('api/dialogue/', views.dialogue_api, name='dialogue_api'),
]