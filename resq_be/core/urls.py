from django.urls import path
from . import views
from .views import GetTwimlView

urlpatterns = [
    path('', views.home, name='home'),
    path('start_call/', views.start_call, name='start_call'),
    path('yes_no_response/<int:call_id>/', views.yes_no_response, name='yes_no_response'),
    path('get_twiml/', GetTwimlView.as_view(), name='get_twiml'),
    path('get_access_token/', views.get_access_token, name='get_access_token'),
    path('process-audio/', views.process_audio, name='process_audio'),  #VAD
    path('process-audio-vosk/', views.process_audio_vosk, name='process_audio_vosk'),  #STT
]

