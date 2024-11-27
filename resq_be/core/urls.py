from django.urls import path
from . import views
from .views import TwilioAPIView

urlpatterns = [
    path('', views.home, name='home'),
    path('start_call/', views.start_call, name='start_call'),
    path('yes_no_response/<int:call_id>/', views.yes_no_response, name='yes_no_response'),
    path('twilio/', TwilioAPIView.as_view(), name='twilio'),
    path('process-audio/', views.process_audio, name='process_audio'),  #VAD
    path('process-audio-vosk/', views.process_audio_vosk, name='process_audio_vosk'),  #STT
]

