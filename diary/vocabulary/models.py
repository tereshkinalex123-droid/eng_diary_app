from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.functions import Lower
from django.utils.text import slugify

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
                Lower('name'),
                'user',
                name='unique_deck_per_user',
            ),
            models.UniqueConstraint(
                'user',
                'slug',
                name='unique_deck_slug_per_user'
            )
        ]

    def __str__(self):
        return f"{self.user.username}: {self.name}"

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.front)
            slug = base_slug
            counter = 1

            while Deck.objects.filter(slug=slug,user=self.user).exists():
                slug = f"{base_slug}-{counter}"
                counter +=1

            self.slug = slug
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


class Review(models.Model):
    card = models.OneToOneField(
        Card,
        on_delete=models.CASCADE,
        related_name='review'
    )

    interval = models.IntegerField(default=1)
    repetitions = models.IntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)

    next_review = models.DateTimeField(default=timezone.now)
    last_review = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Review for {self.card.front}"

class ReviewSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_sessions'
    )

    deck = models.ForeignKey(
        Deck,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_cards = models.IntegerField()
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"ReviewSession({self.user.username})"

class ReviewSessionCard(models.Model):

    session = models.ForeignKey(
        ReviewSession,
        on_delete=models.CASCADE,
        related_name='session_cards'
    )

    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
    )

    order = models.IntegerField()

    answered = models.BooleanField(default=False)

    RATING_CHOICES = [
        ("again", "Again"),
        ("hard", "Hard"),
        ("good", "Good"),
        ("easy", "Easy"),
    ]

    rating = models.CharField(
        max_length=10,
        choices=RATING_CHOICES,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['order']
        unique_together = ('session', 'card')