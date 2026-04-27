from django.utils import timezone
from datetime import timedelta
from .models import UserStreak

def update_streak(user):
    streak, created = UserStreak.objects.get_or_create(user=user)
    today = timezone.now().date()
    last_visit_date = streak.last_visit_date.date() if streak.last_visit_date else None

    if last_visit_date == today:
        return

    if last_visit_date == today - timedelta(days=1):
        streak.current_streak += 1

    if last_visit_date < today - timedelta(days=1):
        streak.current_streak = 1

    if streak.current_streak > streak.max_streak:
        streak.max_streak = streak.current_streak

    streak.last_visit_date = timezone.now()
    streak.save()
