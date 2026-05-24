import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diary.settings')

app = Celery('diary')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-entries-every-6-hours": {
        "task": "records.tasks.check_entries_every_6_hours",
        "schedule": 3600*6,
    },
}

app.conf.beat_schedule = {
    "reset-daily-streaks": {
        "task": "accounts.tasks.check_and_reset_streaks",
        "schedule": crontab(hour=0, minute=0),
    },
}

app.conf.beat_schedule = {
    "reminder-6pm": {
        "task": "accounts.tasks.send_streak_reminder",
        "schedule": crontab(hour=18, minute=0),
    },
    "reminder-9pm": {
        "task": "accounts.tasks.send_streak_reminder",
        "schedule": crontab(hour=21, minute=0),
    },
    "reminder-1130pm": {
        "task": "accounts.tasks.send_streak_reminder",
        "schedule": crontab(hour=23, minute=30),
    },
}