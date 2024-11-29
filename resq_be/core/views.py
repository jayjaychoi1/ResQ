import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from twilio.twiml.voice_response import VoiceResponse, Start
from .utils.stt_utils import transcribe_audio_vosk
from .utils.twilio_token import create_twilio_access_token
from .utils.vad_utils import process_vad

def home(request):
    return render(request, 'main.html')

@csrf_exempt
@api_view(['POST'])
def yes_no_response(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "chat",
        {
            "type": "chat_message",
            "message": request.data['response'],
            "user": 1,
        }
    )

class TwilioAPIView(APIView):
    def get(self, request):
        """
        Create access token and return it (ref. core/utils/create_access_token)
        """
        identity = 'user'
        token = create_twilio_access_token(identity)
        return JsonResponse({"access_token": token})

    def post(self, request):
        response = VoiceResponse()
        response.dial("+821063461851")
        response_start = Start()
        response_start.stream(url="ws://localhost:8000/ws/voice/")
        response.append(response_start)
        return HttpResponse(response.to_xml(), content_type='text/xml')

#VAD
def process_audio(request):
    """
    Detects voiced segments in an audio file using VAD.
    """
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        filepath = f'/tmp/{audio_file.name}'  # Temporary storage

        with open(filepath, 'wb') as f:
            f.write(audio_file.read())

        try:
            vad_segments = process_vad(filepath)
            return JsonResponse({'vad_result': vad_segments})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


#STT
def process_audio_vosk(request):
    """
    Transcribes audio to text using Vosk.
    """
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        filepath = f'/tmp/{audio_file.name}'  # Temporary storage

        with open(filepath, 'wb') as f:
            f.write(audio_file.read())

        try:
            transcription = transcribe_audio_vosk(filepath)
            return JsonResponse({'transcription': transcription})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
