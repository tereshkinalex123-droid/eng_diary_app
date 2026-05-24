from django.utils import timezone
from datetime import timedelta
from .models import UserStreak
from django.db import transaction
from django.db.models import F

def update_streak(user):
    today = timezone.now().date()

    with transaction.atomic():
        streak, created = UserStreak.objects.select_for_update().get_or_create(user=user)
        last_visit_date = streak.last_visit_date.date() if streak.last_visit_date else None

        if last_visit_date == today:
            return

        streak.is_active_today = True

        UserStreak.objects.filter(user=user).update(current_streak=F('current_streak') + 1)

        if streak.current_streak > streak.max_streak:
            streak.max_streak = streak.current_streak

        streak.last_visit_date = timezone.now().date()
        streak.save(update_fields=['current_streak', 'last_visit_date', 'max_streak'])
