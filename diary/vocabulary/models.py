from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.functions import Lower

User = get_user_model()

# Create your models here.
class Deck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'user',
                name='unique_deck_per_user',
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.user.name})"

class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='decks')
    front = models.CharField(max_length=50)
    back = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.front} ({self.user.name})"

class Review(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, related_name='decks')

    interval = models.IntegerField(default=1)
    repetition = models.FloatField(default=0)
    ease_factor = models.FloatField(default=2.5)

    next_review = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"review for {self.card.front}"
