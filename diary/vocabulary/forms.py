from django import forms
from .models import Card, Deck


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ('front', 'back', 'examples', 'deck')
        widgets = {
            'front': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введи переднюю сторону карточки',
            }),
            'back': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введи заднюю сторону карточки',
            }),
            'examples': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введи примеры',
            }),
            'deck': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, user=None, deck=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['deck'].queryset = Deck.objects.filter(user=user)
        if deck:
            self.fields['deck'].initial = deck


class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введи название колоды',
            })}

class ReviewSessionForm(forms.Form):
    card_limit = forms.IntegerField(
        min_value=5,
        max_value=20,
        initial=10,
        label='Количество карточек дял повторения',
        widget=forms.NumberInput(attrs={
            'class': 'form_control',
            'placeholder': '5-20 карточек',
        })
    )