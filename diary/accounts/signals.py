from django.db.models.signals import post_save
from django.dispatch import receiver
from vocabulary.models import CardProgress
from records.models import Record
from .utils import update_streak

@receiver(post_save, sender=CardProgress)
def streak_on_card_review(sender, instance, created, **kwargs):
    if not created:
        update_streak(instance.user)

@receiver(post_save, sender=Record)
def streak_on_record_create(sender, instance, created, **kwargs):
    if created:
        update_streak(instance.user)