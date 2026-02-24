from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Word(models.Model):
    user = models.ForeignKey( #юзер
        User,
        on_delete=models.CASCADE,
        related_name="words",
    )

    original = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    example = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)

    ef = models.FloatField(default=2.5)
    interval = models.IntegerField(default=0)
    repetitions = models.IntegerField(default=0)
    next_review = models.DateTimeField(default=timezone.now)
    last_reviewed = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'original'] #чтобы не было дублей одного слова
        ordering = ['next_review'] #сначала те, что нужно повторіть скорее

    def __str__(self):
        return f"{self.original} - {self.translation}"