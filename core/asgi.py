# core/asgi.py

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from bartender_app import routing
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup() # Necesario para asegurar que Django cargue su configuración

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Define dónde debe ir el tráfico WebSocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})