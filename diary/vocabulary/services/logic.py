from ..models import CardProgress
from itertools import chain
from django.utils import timezone

def get_review_cards(user, limit, deck=None):
    due_progress = CardProgress.objects.filter(user=user, next_review__lte=timezone.now())

    if deck:
        due_progress = due_progress.filter(card__deck=deck)

    due_progress = due_progress.order_by('next_review')[:limit]

    result = list(due_progress)
    remaining = limit - len(result)

    add_cards_ids = [p.card.id for p in result]

    if remaining > 0:
        extra_cards = CardProgress.objects.filter(user=user, repetitions=0)

        extra_cards = extra_cards.exclude(card_id__in=add_cards_ids)

        if deck:
            extra_cards = extra_cards.filter(card__deck=deck)

        extra_cards = extra_cards.order_by('card__created_at')[:remaining]

        result = list(chain(result, extra_cards))
        remaining = limit - len(result)

    add_cards_ids = [p.card.id for p in result]

    if remaining > 0:

        future_cards = CardProgress.objects.filter(user=user, repetitions__gt=0, next_review__gt=timezone.now())

        future_cards = future_cards.exclude(card_id__in=add_cards_ids)

        if deck:
            future_cards = future_cards.filter(card__deck=deck)

        future_cards= future_cards.order_by('next_review')[:remaining]

        result = list(chain(result, future_cards))

    return result

