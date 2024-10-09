import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resq_be.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Defining WebSocket URL routing
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # CAn add websocket routes here
        ])
    ),
})

