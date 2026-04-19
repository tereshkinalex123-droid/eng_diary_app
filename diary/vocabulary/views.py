from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Deck, Card
from django.shortcuts import redirect
from .forms import DeckForm
from django.utils import timezone

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

    next = request.POST.get('next')

    if request.method == "POST":
        card.delete()

    return redirect(next)

