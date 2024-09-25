from django.urls import path

from .views import translate_view

urlpatterns = [
    path('', translate_view, name='translate'),  # Empty path points to the translate_view
    #path('translate/', include('translations.urls')),
]