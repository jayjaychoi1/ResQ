from django.urls import path
from . import views
from .views import TwilioAPIView

urlpatterns = [
    path('', views.home, name='home'),
    path('twilio/', TwilioAPIView.as_view(), name='twilio'),
]

