from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Deck
from django.shortcuts import redirect


# ДОПИСАТЬ ВО ВСЕХ ШАБЛОНАХ ПУТЬ ДО ПАПКИ ПРИЛОЖЕНИЯ


@login_required
def deck_list(request):
    decks = Deck.objects.filter(user=request.user).order_by('-date')

    return render(request, 'deck_list.html', {'decks': decks})

@login_required
def deck_create(request):
    if request.method == "POST":
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = form.save(commit=False)
            deck.user = request.user
            deck.save()

            return redirect('deck_list')
    else:
        form = DeckForm()

    return render(request, 'deck_create.html', {'form': form})

@login_required
def deck_detail(request,deck_slug):
    deck = get_object_or_404(
        Deck,
        slug=deck_slug,
        user=request.user,
    )

    return render(request, 'deck_detail.html', {'deck': deck})

@login_required
def deck_delete(request,deck_slug):
    deck = get_object_or_404(
        Deck,
        slug=deck_slug,
        user=request.user,
    )

    if request.method == "POST":
        deck.delete()

    return redirect('deck_list')

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
        form = CardForm(request.POST or None, user=request.user)

        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user

            if deck:
                card.deck = deck

            card.save()

            if deck:
                return redirect('deck_detail', deck_slug=deck.slug)
            else:
                return redirect('deck_list')
    else:
        form = CardForm()

    return render(request, 'card_create.html', {'form': form})

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
            return redirect('deck_detail', deck_slug=deck.slug)
    else:
        form = CardForm(instance=card)

    return render(request, 'card_edit.html', {'form': form, 'card': card})

@login_required
def card_delete(request, card_slug):
    card = get_object_or_404(
        Card,
        slug=card_slug,
        user=request.user
    )

    deck = card.deck

    if request.method == "POST":
        card.delete()

    return redirect('deck_detail', deck_slug=deck.slug)
