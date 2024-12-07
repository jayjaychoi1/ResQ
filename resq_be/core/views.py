from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from twilio.twiml.voice_response import VoiceResponse

from .config import conf_caller_identity, conf_voice_websocket_url, conf_caller_number
from .utils.twilio_token import create_twilio_access_token

def home(request):
    return render(request, 'main.html')

class TwilioAPIView(APIView):
    def get(self, request):
        """
        Create access token and return it (ref. core/utils/create_access_token)
        """
        identity = conf_caller_identity
        token = create_twilio_access_token(identity)
        return JsonResponse({"access_token": token})

    def post(self, request):
        to_number = request.POST.get("To")
        response = VoiceResponse()
        response.start().stream(url=conf_voice_websocket_url, track="both")
        response.dial(to_number, callerId=conf_caller_number)
        return HttpResponse(response.to_xml(), content_type='text/xml')


