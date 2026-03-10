from cards.models import Review
from cards.services.sm2_algorithm import update_review

def answer_card(session_card, rating):

    session = session_card.session
    review = session_card.card.review

    session_card.rating = rating
    session_card.answered = True
    session_card.save()

    if rating.lower() == 'again':
        session.incorrect_answers += 1
    else:
        session.correct_answers += 1

    session.save()

    update_review(review, rating)

def finish_session(session):

    session.completed = True
    session.completed_at = timezone.now()
    session.save()

def get_session_stats(session):

    return {
        "total": session.total_cards,
        "correct": session.correct_answers,
        "incorrect": session.incorrect_answers
    }