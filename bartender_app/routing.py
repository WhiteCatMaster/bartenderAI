# bartender_app/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Mapea la URL 'ws/robot/' al RobotConsumer
    re_path(r'ws/robot/$', consumers.RobotConsumer.as_asgi()),
]