from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Deck, Card, ReviewSession
from django.shortcuts import redirect
from .forms import DeckForm, CardForm, StartReviewForm
from django.utils import timezone
from .services.session_service import get_next_card
from .services.review_service import finish_session, answer_card

# ДОПИСАТЬ ВО ВСЕХ ШАБЛОНАХ ПУТЬ ДО ПАПКИ ПРИЛОЖЕНИЯ
# -------- Deck Views --------
@login_required
def deck_list(request):
    decks = Deck.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "vocabulary/deck_list.html", {'decks': decks})

@login_required
def deck_create(request):
    if request.method == "POST":
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = form.save(commit=False)
            deck.user = request.user
            deck.save()

            return redirect('vocabulary:deck_list')
    else:
        form = DeckForm()

    return render(request, 'vocabulary/deck_create.html', {'form': form})

@login_required
def deck_detail(request, deck_slug):

    deck = get_object_or_404(
        Deck,
        slug=deck_slug,
        user=request.user,
    )

    cards = deck.cards.all()

    return render(request, 'vocabulary/deck_detail.html', {'deck': deck, 'cards': cards})

@login_required
def deck_delete(request,deck_slug):
    deck = get_object_or_404(
        Deck,
        slug=deck_slug,
        user=request.user,
    )

    if request.method == "POST":
        deck.delete()

    return redirect('vocabulary:deck_list')

@login_required
def card_list(request):
    cards = Card.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'vocabulary/card_list.html', {'cards': cards})

# # -------- Card Views --------

@login_required
def card_create(request, deck_slug=None):

    deck = None

    if deck_slug:
        deck = get_object_or_404(
            Deck,
            user=request.user,
            slug=deck_slug,
        )

    if request.method == "POST":
        form = CardForm(request.POST, user=request.user)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user

            if deck:
                card.deck = deck
                print(deck.name)

            card.save()

            if deck:
                return redirect('vocabulary:deck_detail', deck_slug=deck.slug)
            else:
                return redirect('vocabulary:common_deck')
    else:
        form = CardForm(user=request.user, deck=deck)

    if deck:
        return render(request, 'vocabulary/card_create.html', {'form': form, 'deck': deck.name})
    else:
        return render(request, 'vocabulary/card_create.html', {'form': form,})



@login_required
def card_edit(request, card_slug):
    card = get_object_or_404(
        Card,
        user=request.user,
        slug=card_slug,
    )

    if request.method == 'POST':
        form = CardForm(request.POST or None, user=request.user, instance=card)
        if form.is_valid():
            card = form.save()
            deck = card.deck
            return redirect('vocabulary:deck_detail', deck_slug=deck.slug)
    else:
        form = CardForm(instance=card)

    return render(request, 'vocabulary/card_edit.html', {'form': form, 'card': card})

@login_required
def card_delete(request, card_slug):
    card = get_object_or_404(
        Card,
        slug=card_slug,
        user=request.user
    )

    previous_url = request.META.get('HTTP_REFERER')

    deck = card.deck

    if request.method == "POST":
        card.delete()

    if previous_url:
        return redirect(previous_url)
    else:
        return redirect('vocabulary:common_deck')

@login_required
def review(request, deck_slug=None):

    deck = None

    if deck_slug:
        deck = get_object_or_404(
            Deck,
            slug=deck_slug,
            user=request.user,
        )

    if request.method == "POST":
        form = StartReviewForm(request.POST)

        if form.is_valid():

            total_cards = form.cleaned_data['total_cards']

            return redirect('vocabulary:deck_list')
    else:
        form = StartReviewForm()


    return render(request, 'vocabulary/review_start.html', {'form': form, 'deck': deck})

@login_required
def review_session(request, session_id):
    session = get_object_or_404(
        ReviewSession,
        id=session_id,
        user=request.user,
    )

    session_card = get_next_card(session)

    if not session_card:
        finish_session(session)
        return redirect('vocabulary:end_session', session_id=session_id)

    if request.method == "POST":

        rating = request.POST.get('rating')

        answer_card(session_card, rating)

        return redirect('vocabulary:review_session', session_id=session_id)

    return render(request, 'vocabulary/review_card.html', {'session': session, 'session_card': session_card, 'card': session_card.card})

@login_required
def end_session(request, session_id):

    session = get_object_or_404(
        ReviewSession,
        id=session_id,
        user=request.user,
    )

    if request.method == "POST":
        finish_session(session)
        return redirect('vocabulary:review_session', session_id=session.id)

    if not session.completed:
        return redirect('vocabulary:review_session', session_id=session.id)

    return render(request, 'vocabulary/end_session.html', {'session': session})