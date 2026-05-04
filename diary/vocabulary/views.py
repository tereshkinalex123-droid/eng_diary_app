from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Deck, Card, CardProgress, ReviewSession
from django.shortcuts import redirect
from .forms import DeckForm, CardForm, ReviewSessionForm
from django.utils import timezone
from .services.logic import get_review_cards
from django.http import JsonResponse
import json
import traceback
from django.http import JsonResponse, HttpResponse
from django.urls import reverse

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
        form = CardForm(request.POST, user=request.user, deck=deck)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user

            if deck:
                card.deck = deck

            card.save()

            CardProgress.objects.create(
                card=card,
                user=request.user,
                next_review=timezone.now().date()
            )

            print(f"{card.front} {card.card_progress.next_review}")

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
def card_edit(request, card_id):
    card = get_object_or_404(
        Card,
        user=request.user,
        id=card_id,
    )

    if request.method == 'POST':
        form = CardForm(request.POST or None, user=request.user, instance=card)
        if form.is_valid():
            card = form.save()
            deck = card.deck
            if deck:
                return redirect('vocabulary:deck_detail', deck_slug=deck.slug)
            else:
                return redirect('vocabulary:common_deck')
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

    next = request.POST.get('next')

    if request.method == "POST":
        card.delete()

    return redirect(next)

@login_required
def start_review_setup(request, deck_slug=None):
    if request.method == "POST":
        form=ReviewSessionForm(request.POST)
        if form.is_valid():
            card_limit = form.cleaned_data['card_limit']
            request.session['review_limit'] = card_limit
            if deck_slug:
                return redirect('vocabulary:review_card', deck_slug=deck_slug)
            else:
                return redirect('vocabulary:common_review_card')
    else:
        form = ReviewSessionForm()

    return render(request, 'vocabulary/review_setup.html', {'form': form})


@login_required
def review_card(request, deck_slug=None):


    review_limit = request.session.get('review_limit')
    if not review_limit:
        if deck_slug:
            return redirect('vocabulary:review_setup', deck_slug=deck_slug)
        return redirect('vocabulary:common_review_setup')

    deck = None
    if deck_slug:
        deck = get_object_or_404(Deck, slug=deck_slug, user=request.user)

    if request.method == "GET":
        card_ids = request.session.get('card_ids')

        if not card_ids:
            cards = get_review_cards(request.user, review_limit, deck)

            if not cards:
                return render(request, 'vocabulary/review_done.html')

            if len(cards) < review_limit and not request.session.get('confirmed'):
                return render(request, 'vocabulary/review_confirm.html', {
                    'cards_count': len(cards),
                    'limit': review_limit,
                    'deck_slug': deck_slug
                })

            if request.session.get('confirmed'):
                request.session['confirmed'] = False

            request.session['card_ids'] = [c.id for c in cards]
            request.session['current_index'] = 0

            session = ReviewSession.objects.create(
                user=request.user,
                total_cards=len(cards),
                correct_answers=0
            )
            request.session['session_id'] = session.id

            card_ids = [c.id for c in cards]
            current_index = 0
            session_id = session.id
        else:
            current_index = request.session.get('current_index', 0)
            session_id = request.session.get('session_id')

        current_card_id = card_ids[current_index]
        card_progress = get_object_or_404(CardProgress, id=current_card_id, user=request.user)

        return render(request, 'vocabulary/review_card.html', {
            'card': card_progress.card,
            'current': current_index + 1,
            'total': len(card_ids),
            'session_id': session_id,
            'deck_slug': deck_slug,
        })

    elif request.method == "POST":

        card_ids = request.session.get('card_ids')
        session_id = request.session.get('session_id')
        current_index = request.session.get('current_index', 0)

        if not card_ids or not session_id:
            if deck:
                return redirect('vocabulary:review_setup', deck_slug=deck_slug)
            else:
                return redirect('vocabulary:common_review_setup')


        if not card_ids or not session_id:
            return JsonResponse({'error': 'Session expired'}, status=400)

        quality = int(request.POST.get('quality', 0))

        try:
            current_card_id = card_ids[current_index]

            card_progress = get_object_or_404(CardProgress, id=current_card_id, user=request.user)
            card_progress.update_after_review(quality)

            session = get_object_or_404(ReviewSession, id=session_id, user=request.user)
            if quality >= 3:
                session.correct_answers += 1
            session.save()

            current_index += 1
            request.session['current_index'] = current_index

            if current_index < len(card_ids):
                next_card_id = card_ids[current_index]
                next_card_progress = get_object_or_404(CardProgress, id=next_card_id, user=request.user)
                next_card = next_card_progress.card

                return JsonResponse({
                    'has_next': True,
                    'front': next_card.front,
                    'back': next_card.back,
                    'hint': next_card.hint or '',
                    'current': current_index + 1,
                    'total': len(card_ids),
                })

            session.ended_at = timezone.now()
            session.save()

            request.session.pop('review_limit', None)
            request.session.pop('card_ids', None)
            request.session.pop('current_index', None)
            request.session.pop('session_id', None)

            return JsonResponse({
                'has_next': False,
                'redirect_url': reverse('vocabulary:session_results', args=[session.id])
            })

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def session_results(request, session_id):
    session = ReviewSession.objects.get(id=session_id, user=request.user)
    return render(request, 'vocabulary/session_results.html', {'session':session, 'wrong_answers': session.total_cards - session.correct_answers })

@login_required
def end_review(request, session_id):
    if request.method == "POST":
        session = get_object_or_404(
            ReviewSession,
            id=session_id,
            user=request.user
        )

        session.ended_at = timezone.now()
        session.save()

        request.session.pop('review_limit', None)
        request.session.pop('card_ids', None)
        request.session.pop('current_index', None)
        request.session.pop('session_id', None)

        return render(request, 'vocabulary/session_results.html',
                      {'session': session, 'wrong_answers': session.total_cards - session.correct_answers})

@login_required
def confirm_review(request, deck_slug=None):
    if request.method == "POST":
        if request.POST.get('choice') == 'yes':
            request.session['confirmed'] = True

        if deck_slug:
            return redirect('vocabulary:review_card', deck_slug=deck_slug)
        else:
            return redirect('vocabulary:common_review_card')