import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from twilio.twiml.voice_response import VoiceResponse, Start
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
    # add start tag
    response_start = Start()
    # add stream tag, url: websocket server
    response_start.stream(url="")
    # response/start
    response.append(response_start)
    return HttpResponse(response.to_xml(), content_type='text/xml')

@csrf_exempt
def get_access_token(request):
    identity = 'user'
    # create access token (ref. core/utils/twilio_token.py)
    token = create_twilio_access_token(identity)
    # JWToken as Json
    return JsonResponse({"access_token": token})


