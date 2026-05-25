from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class UserStreak(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streak')
    last_visit_date = models.DateTimeField(auto_now_add=True)
    current_streak = models.IntegerField(default=1)
    max_streak = models.IntegerField(default=1)
    is_active_today = models.BooleanField(default=False)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    connection_token = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"