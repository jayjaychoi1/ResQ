from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/test/', consumers.MyConsumer.as_asgi()),
]
