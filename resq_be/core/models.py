from django.db import models

class EmergencyCall(models.Model):
    user_location = models.CharField(max_length=255, blank=True, null=True)
    call_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('active', 'Active'), ('completed', 'Completed')], default='pending')
    recorded_audio = models.FileField(upload_to='recordings/', blank=True, null=True)
    responses = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Call {self.id} - {self.call_status}'

