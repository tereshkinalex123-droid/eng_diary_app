from celery import shared_task
from .models import UserStreak, Profile
from django.utils import timezone
from datetime import timedelta
import asyncio
from config import BOT_TOKEN
from aiogram import Bot
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_and_reset_streaks():
    print(f"dsfgsfdfsfd")
    UserStreak.objects.update(is_active_today=False)

    yesterday_start = (timezone.now() - timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    streaks = UserStreak.objects.filter(last_visit_date__lt=yesterday_start)
    streaks.update(current_streak=0)

    streaks_with_profile = streaks.filter(
        user__profile__telegram_id__isnull=False
    ).select_related('user__profile')

    streaks_data = [
        {
            'telegram_id': s.user.profile.telegram_id,
            'username': s.user.username
        }
        for s in streaks_with_profile
    ]

    async def send_streak():
        bot = Bot(token=BOT_TOKEN)
        for p in streaks_data:
            try:
                await bot.send_message(p['telegram_id'], "You lost your streak!")
                logger.info(f"Отправлено {p['username']}")
            except Exception as e:
                logger.error(f"Ошибка {p['username']}: {e}")
        await bot.session.close()

    asyncio.run(send_streak())


@shared_task
def send_streak_reminder():
    print(f"dsfgsfdfsfd")
    # Create timezone-aware datetime for start of today (midnight)
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    inactive_users = UserStreak.objects.filter(
        is_active_today=False,
        last_visit_date__lt=today_start,  # ✅ compare datetime with datetime
        user__profile__telegram_id__isnull=False,
    ).select_related('user__profile')  # ✅ add select_related

    inactive_users_data = [
        {
            'telegram_id': u.user.profile.telegram_id,
            'username': u.user.username
        }
        for u in inactive_users
    ]

    async def send_reminder():
        bot = Bot(token=BOT_TOKEN)
        for p in inactive_users_data:
            try:
                await bot.send_message(p['telegram_id'], "⚠️ You haven't studied today! Streak will reset at midnight!")
                logger.info(f"Sent to {p['username']}")
            except Exception as e:
                logger.error(f"Error {p['username']}: {e}")
        await bot.session.close()

    if inactive_users_data:
        asyncio.run(send_reminder())