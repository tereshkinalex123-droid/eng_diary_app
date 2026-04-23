from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.functions import Lower
from django.utils.text import slugify
import math

User = get_user_model()

# Create your models here.
class Deck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'user',
                Lower('name'),
                name="unique_deck_per_user"
            ),
            models.UniqueConstraint(
                'user',
                'slug',
                name="unique_deck_slug_per_user"
            )
        ]

    def __str__(self):
        return f"{self.user.username}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            original_name = self.name
            base_name = original_name
            counter = 1
            while Deck.objects.filter(user=self.user, name__iexact=base_name).exists():
                base_name = f"{original_name} {counter}"
                counter +=1
            self.name = base_name
            self.slug = slugify(base_name)
        super().save(*args, **kwargs)

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    deck = models.ForeignKey(Deck, on_delete=models.SET_NULL, null=True, blank=True, related_name='cards')
    slug = models.SlugField(max_length=50, null=True, blank=True)
    front = models.CharField(max_length=50)
    back = models.CharField(max_length=50)
    examples = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hint = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.front}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'slug',
                'user',
                name='unique_card_slug_per_user',
            )
        ]

    def save(self, *args, **kwargs):

        if not self.hint and len(self.front) > 3:
            hint = list(self.front)
            for i in range(1, len(hint) - 1):
                hint[i] = "_"
            self.hint = "".join(hint)

        if not self.slug:
            base_slug = slugify(self.front)
            slug = base_slug
            counter = 1

            while Card.objects.filter(slug=slug,user=self.user).exists():
                slug = f"{base_slug}-{counter}"
                counter +=1

            self.slug = slug
        super().save(*args, **kwargs)


class CardProgress(models.Model):
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='card_progress'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='card_progresses'
    )

    ease_factor = models.FloatField(default=2.5)
    repetitions  = models.IntegerField(default=0)
    interval  = models.PositiveIntegerField(default=0)

    next_review = models.DateTimeField(default=timezone.now)
    last_review = models.DateTimeField(blank=True, null=True)

    def update_after_review(self, quality):
        self.last_reviewed = timezone.now()

        if quality < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            self.repetitions += 1

            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = int(math.ceil(self.interval * self.ease_factor))

            self.ease_factor = self.ease_factor + (0.1 - (5 - quality) * 0.08)

            if self.ease_factor < 1.3:
                self.ease_factor = 1.3


        self.next_review = timezone.now() + timedelta(days=self.interval)

        self.save()

class ReviewSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_sessions'
    )

    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name='review_sessions',
        null=True,
        blank=True
    )

    total_cards = models.PositiveIntegerField(default=0)
    correct_answers  = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
