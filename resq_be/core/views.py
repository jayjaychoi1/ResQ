import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from twilio.twiml.voice_response import VoiceResponse, Start
from .utils.twilio_token import create_twilio_access_token
# TODO
# Audio Recording Storage: Save recorded audio files securely on the server and link them to each call entry in the database.
# Database Improvements: Add a model to store call recordings, locations, timestamps, and call statuses, including fields for audio file paths and Yes/No responses.
# Real-Time Location Updates: Continuously update and store the user's location during the call. -> GeolocationAPI, watchPosition in frontend

def home(request):
    return render(request, 'main.html')

@csrf_exempt
@api_view(['POST'])
def start_call(request):
    # Simulate saving the call and return a call ID
    # Creating an EmergencyCall object in the database
    call_id = 1  # We have to replace this with the actual id of the created call
    return JsonResponse({'message': 'Emergency call started', 'call_id': call_id})

@csrf_exempt
@api_view(['POST'])
def yes_no_response(request, call_id):
    # Paring the request body for the response
    data = json.loads(request.body)
    response = data.get('response')
    if response in ['yes', 'no']:
        return JsonResponse({'message': f'Response "{response}" recorded'})
    return JsonResponse({'error': 'Invalid response'}, status=400)

class GetTwimlView(APIView):
    """
    Twilio server access this view to get our own TwiML
    """
    def post(self, request):
        response = VoiceResponse()
        response.dial("+821063461851")
        #response_start = Start()
        #response_start.stream(url="")
        #response.append(response_start)
        return HttpResponse(response.to_xml(), content_type='text/xml')

@csrf_exempt
@api_view(['GET'])
def get_access_token(request):
    """
    Create access token and return it (ref. core/utils/create_access_token)
    """
    identity = 'user'
    token = create_twilio_access_token(identity)
    return JsonResponse({"access_token": token})

