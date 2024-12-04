from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.twiml.voice_response import VoiceResponse

from .config import conf_caller_identity, conf_voice_websocket_url, conf_caller_number
from .utils.chat_utils import send
from .utils.twilio_token import create_twilio_access_token
# from .utils.stt_utils import transcribe_audio_vosk
# from .utils.vad_utils import process_vad

def home(request):
    return render(request, 'main.html')

@csrf_exempt
@api_view(['POST'])
def yes_no_response(request):
    send("user", request.data['response'])
    return Response({ "message": "sent!"}, status.HTTP_200_OK)

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

