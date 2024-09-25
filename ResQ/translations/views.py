from django.http import JsonResponse
from django.shortcuts import render

from .utils import translate_en_to_ko


def translate_view(request):
    if request.method == 'POST':
        original_text = request.POST.get('text')
        translated_text = translate_en_to_ko(original_text)
        return JsonResponse({'translated_text': translated_text})