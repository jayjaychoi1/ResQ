from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

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

