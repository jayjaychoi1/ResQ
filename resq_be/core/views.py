import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from twilio.twiml.voice_response import VoiceResponse, Start
from twilio.rest import Client
from .utils.twilio_token import create_twilio_access_token
# STT
# As mentor said, we have to parse with full sentence.
# real-time translation is not real-time
# cause its PREDICTION, not translation.

# TODO
# Audio Recording Storage: Save recorded audio files securely on the server and link them to each call entry in the database.
# Database Improvements: Add a model to store call recordings, locations, timestamps, and call statuses, including fields for audio file paths and Yes/No responses.
# Real-Time Location Updates: Continuously update and store the user's location during the call. -> GeolocationAPI, watchPosition in frontend

def home(request):
    return render(request, 'main.html')

@csrf_exempt
def start_call(request):
    if request.method == 'POST':
        # Simulate saving the call and return a call ID
        # Creating an EmergencyCall object in the database
        call_id = 1  # We gotta replace this with the actual id of the created call
        return JsonResponse({'message': 'Emergency call started', 'call_id': call_id})

@csrf_exempt
def yes_no_response(request, call_id):
    if request.method == 'POST':
        # Paring the request body for the response
        data = json.loads(request.body)
        response = data.get('response')
        if response in ['yes', 'no']:
            return JsonResponse({'message': f'Response "{response}" recorded'})
        return JsonResponse({'error': 'Invalid response'}, status=400)

@csrf_exempt
def get_twiml_view(request):
    # add response tag
    response = VoiceResponse()
    response.dial("")  # 고정된 전화번호로 연결
    # # add start tag
    # response_start = Start()
    # # add stream tag, url: websocket server
    # response_start.stream(url="")
    # response/start
    # response.append(response_start)
    return HttpResponse(response.to_xml(), content_type='text/xml')

@csrf_exempt
def get_access_token(request):
    identity = 'user'
    # create access token (ref. core/utils/twilio_token.py)
    token = create_twilio_access_token(identity)
    print(token)
    # JWToken as Json
    return JsonResponse({"access_token": token})

# problems on secure
# anyone can access to urls -> wasted token occurs

# Download the helper library from https://www.twilio.com/docs/python/install
# import os
# from twilio.rest import Client
# @csrf_exempt
# def demo(request):
#     # Find your Account SID and Auth Token at twilio.com/console
#     # and set the environment variables. See http://twil.io/secure
#     account_sid = ""
#     auth_token = ""
#     client = Client(account_sid, auth_token)
#
#     call = client.calls.create(
#         from_="",
#         to="",
#         url="",
#     )
#
#     print(call.sid)


from twilio.rest import Client
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def demo(request):
    if request.method == "POST":
        account_sid = ""  # 올바른 Account SID
        auth_token = ""      # 올바른 Auth Token
        client = Client(account_sid, auth_token)             # Client 초기화 시 정확한 인수 사용

        try:
            call = client.calls.create(
                from_="",
                to="",
                url=""
            )
            return JsonResponse({"status": "success", "call_sid": call.sid})
        except Exception as e:
            return JsonResponse({"status": "failed", "error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
