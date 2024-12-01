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
        identity = 'jywon1128@gmail.com'
        token = create_twilio_access_token(identity)
        return JsonResponse({"access_token": token})

    def post(self, request):
        to_number = request.POST.get("To")
        response = VoiceResponse()
        response.start().stream(url="wss://6fab-119-192-238-169.ngrok-free.app/ws/voice/", track="both")
        response.dial(to_number, callerId="+18582076378")
        return HttpResponse(response.to_xml(), content_type='text/xml')

# #VAD
# def process_audio(request):
#     """
#     Detects voiced segments in an audio file using VAD.
#     """
#     if request.method == 'POST' and request.FILES.get('audio_file'):
#         audio_file = request.FILES['audio_file']
#         filepath = f'/tmp/{audio_file.name}'  # Temporary storage
#
#         with open(filepath, 'wb') as f:
#             f.write(audio_file.read())
#
#         try:
#             vad_segments = process_vad(filepath)
#             return JsonResponse({'vad_result': vad_segments})
#
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'error': 'Invalid request'}, status=400)
#
#
# #STT
# def process_audio_vosk(request):
#     """
#     Transcribes audio to text using Vosk.
#     """
#     if request.method == 'POST' and request.FILES.get('audio_file'):
#         audio_file = request.FILES['audio_file']
#         filepath = f'/tmp/{audio_file.name}'  # Temporary storage
#
#         with open(filepath, 'wb') as f:
#             f.write(audio_file.read())
#
#         try:
#             transcription = transcribe_audio_vosk(filepath)
#             return JsonResponse({'transcription': transcription})
#
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'error': 'Invalid request'}, status=400)
