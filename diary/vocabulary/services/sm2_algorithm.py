from django.utils import timezone
from datetime import timedelta

def update_review(review, rating):

    interval = review.interval
    ease_factor = review.ease_factor
    repetitions = review.repetitions

    if rating.lower() == 'again':
        interval = 1
        repetitions = 0
    else:
        repetitions += 1

        if rating == "hard":
            ease_factor -= 0.15
        elif rating == "easy":
            ease_factor += 0.15
        elif rating == "good":
            pass

        if ease_factor < 1.3:
            ease_factor = 1.3

        if repetitions == 1:
            interval = 1
        elif repetitions == 2:
            interval = 3
        else:
            interval = round(interval * ease_factor)

    last_review = timezone.now()
    next_review = last_review + timedelta(days=interval)

    review.interval = interval
    review.ease_factor = ease_factor
    review.repetitions = repetitions
    review.next_review = next_review
    review.last_review = last_review

    review.save()

