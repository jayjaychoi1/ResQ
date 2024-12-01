from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.twiml.voice_response import VoiceResponse, Start

from .utils.chat_utils import send
from .utils.twilio_token import create_twilio_access_token
#for vad and stt part
import os
from .utils.vad_utils import is_speech_in_audio
from .utils.stt_utils import transcribe_audio

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
        identity = 'jywon1128@gmail.com'
        token = create_twilio_access_token(identity)
        return JsonResponse({"access_token": token})

    def post(self, request):
        to_number = request.POST.get("To")
        response = VoiceResponse()
        response.start().stream(url="wss://6fab-119-192-238-169.ngrok-free.app/ws/voice/", track="both")
        response.dial(to_number, callerId="+18582076378")
        return HttpResponse(response.to_xml(), content_type='text/xml')

#vad and stt part

@csrf_exempt
def process_audio(request):
    """
    Handles POST requests to process audio files for VAD and STT.
    """
    if request.method == "POST" and "audio_file" in request.FILES:
        audio_file = request.FILES["audio_file"]
        file_path = f"uploaded_audio/{audio_file.name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        try:
            if is_speech_in_audio(file_path):
                transcription = transcribe_audio(file_path)
                return JsonResponse({"transcription": transcription})
            else:
                return JsonResponse({"error": "No speech detected in the audio."})
        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Invalid request"})
