from django.conf import settings
from django.db import models

class UserStreak(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streak')
    last_visit_date = models.DateTimeField(auto_now_add=True)
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)