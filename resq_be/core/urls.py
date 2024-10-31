from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('start_call/', views.start_call, name='start_call'),
    path('yes_no_response/<int:call_id>/', views.yes_no_response, name='yes_no_response'),
    path('getTwiML/', views.getTwiMLView, name='getTwiML'),
    path('getAccessToken/', views.get_access_token, name='getAccessToken'),
]

