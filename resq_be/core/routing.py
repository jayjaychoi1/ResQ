from django.urls import path
from . import consumers
from resq_be.consumers import VoiceConsumer


websocket_urlpatterns = [
    path('ws/voice/', consumers.ChatConsumer.as_asgi()),
    path('ws/chat/', consumers.ChatConsumer.as_asgi()),
    path("ws/voice/", VoiceConsumer.as_asgi()),
]
