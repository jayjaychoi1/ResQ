from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
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

@api_view(['POST'])
def voice_toggle(request):
    flag = request.data['flag']
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "flag_socket",
        {
            "type": "toggle_flag",
            "flag": flag
        }
    )
    return Response({"flag": flag}, status.HTTP_200_OK)

def toggle_flag(request):
    # 요청에 따라 Boolean 값을 결정
    new_flag_value = request.GET.get('flag', 'true') == 'true'

    # WebSocket 그룹으로 메시지 전송
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "flag_group",  # WebSocket 그룹 이름
        {
            "type": "toggle_flag",  # Consumer에서 처리할 이벤트 타입
            "flag": new_flag_value,  # 전달할 Boolean 값
        }
    )

    return JsonResponse({"success": True, "flag": new_flag_value})