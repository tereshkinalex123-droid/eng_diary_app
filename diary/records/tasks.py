from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from aiogram import Bot
from accounts.models import Profile
from .models import Record
from config import BOT_TOKEN
import asyncio

import logging

logger = logging.getLogger(__name__)

@shared_task
def check_entries_every_6_hours():
    six_hours_ago = timezone.now() - timedelta(hours=6)
    count = Record.objects.filter(date__gte=six_hours_ago).count()

    if count == 0:
        return

    profiles_data = []
    profiles = Profile.objects.filter(telegram_id__isnull=False).select_related('user')

    for profile in profiles:
        profiles_data.append({
            'telegram_id': profile.telegram_id,
            'username': profile.user.username
        })

    async def send():
        bot = Bot(token=BOT_TOKEN)
        for p in profiles_data:
            try:
                await bot.send_message(p['telegram_id'], f"📝 {count} new entries in the last 6 hours!")
                logger.info(f"Отправлено {p['username']}")
            except Exception as e:
                logger.error(f"Ошибка {p['username']}: {e}")
        await bot.session.close()

    asyncio.run(send())
