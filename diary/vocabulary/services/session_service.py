import random
from django.utils import timezone

from ..models import Card, ReviewSession, ReviewSessionCard

def start_review_session(user, deck=None, limit=None):

    cards = Card.objects.filter(user=user)

    if deck:
        cards = cards.filter(deck=deck)

    cards = cards.filter(review__next_review__lte=timezone.now())

    due_cards = list(cards)

    if limit and len(due_cards) >= limit:
        cards = due_cards[:limit]
    else:
        cards = due_cards

        if limit:
            remaining = limit - len(cards)

            extra_cards = Card.objects.filter(user=user)

            if deck:
                extra_cards = extra_cards.filter(deck=deck)

            extra_cards = extra_cards.exclude(
                id__in=[c.id for c in cards]
            )

            extra_cards = list(extra_cards)

            random.shuffle(extra_cards)

            cards += extra_cards[:remaining]


    if not cards:
        return None

    random.shuffle(cards)


    session = ReviewSession.objects.create(
        user=user,
        deck=deck,
        total_cards=len(cards)
    )

    session_cards = []

    for index, card in enumerate(cards):
        session_cards.append(
            ReviewSessionCard(
                session=session,
                card=card,
                order=index
            )
        )

    ReviewSessionCard.objects.bulk_create(session_cards)

    return session

def get_next_card(session):

    session_card = session.session_cards.filter(answered=False).first()

    if not session_card:
        return None

    return session_card

