from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/voice/', consumers.VoiceConsumer.as_asgi()),
    path('ws/chat/', consumers.ChatConsumer.as_asgi()),
]
