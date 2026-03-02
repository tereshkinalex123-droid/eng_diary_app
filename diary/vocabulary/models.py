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
    slug = models.SlugField(max_length=50, unique=True)
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
        return f"({self.user.name}){self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"({self.user.name}){self.name}")
        super().save(*args, **kwargs)

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='decks')
    slug = models.SlugField(max_length=50, unique=True)
    front = models.CharField(max_length=50)
    back = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"({self.user.name}){self.front}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'slug',
                'user',
                name='unique_deck_per_user',
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"({self.user.name}){self.front}")
            slug = base_slug
            counter = 1

            while Card.objects.filter(slug=slug,user=self.user).exists():
                slug = f"{base_slug}-{counter}"
                counter +=1

            self.slug = slug

class Review(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, related_name='decks')

    interval = models.IntegerField(default=1)
    repetition = models.FloatField(default=0)
    ease_factor = models.FloatField(default=2.5)

    next_review = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"review for {self.card.front}"
