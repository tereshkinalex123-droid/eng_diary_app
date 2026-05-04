from ..models import CardProgress
from django.utils import timezone

def get_review_cards(user, limit, deck=None):
    due_progress = CardProgress.objects.filter(user=user, next_review__lte=timezone.now().date())

    if deck:
        due_progress = due_progress.filter(card__deck=deck)

    due_progress = due_progress.order_by('next_review')[:limit]

    result = list(due_progress)

    return result