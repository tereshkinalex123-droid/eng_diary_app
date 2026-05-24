from django.db.models.signals import post_save
from django.dispatch import receiver
from vocabulary.models import CardProgress
from records.models import Record
from accounts.models import UserStreak
from django.contrib.auth.models import User
from .utils import update_streak

@receiver(post_save, sender=CardProgress)
@receiver(post_save, sender=Record)
def streak_on_record_create(sender, instance, created, **kwargs):
    if created:
        update_streak(instance.user)

@receiver(post_save, sender=User)
def create_user_streak(sender, instance, created, **kwargs):
    if created:
        UserStreak.objects.create(user=instance)