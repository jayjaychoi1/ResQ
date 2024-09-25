from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .utils import translate_en_to_ko


def translate_view(request):
    translated_text = ""
    if request.method == 'POST':
        original_text = request.POST.get('text')
        translated_text = translate_en_to_ko(original_text) if original_text else "Please enter some text."
    
    return render(request, 'translations/translate.html', {'translated_text': translated_text})

def home_view(request):
    return HttpResponse("Welcome to the Emergency Translation App!")