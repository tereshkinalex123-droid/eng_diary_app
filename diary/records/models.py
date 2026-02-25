from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Record(models.Model):
    user = models.ForeignKey( #юзер
        User,
        on_delete=models.CASCADE,
        related_name="records",
    )

    title = models.CharField(max_length=100) #заголовок
    slug = models.SlugField(max_length=100, unique = True, blank=True) #слаг
    content = models.TextField() #мессэдж
    date = models.DateTimeField(auto_now_add = True) #дата создания
    tags = models.ManyToManyField(Tag, blank=True, related_name='records')

    def word_count(self):
        return len(self.content.split())

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.date:
                self.slug = slugify(f"{self.title}-{self.date.strftime('%Y%m%d')}")
            else:
                self.slug = slugify(f"{self.title}-{timezone.now().strftime('%Y%m%d')}")
        super().save(*args, **kwargs)


class Correction(models.Model):
    record = models.ForeignKey(
        Record,
        on_delete=models.CASCADE,
        related_name='corrections',
    )
    original_text = models.TextField()
    corrected_text = models.TextField()
    explanation = models.TextField(blank=True)
    error_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Expression(models.Model):
    record = models.ForeignKey(
        Record,
        on_delete=models.CASCADE,
        related_name='expressions',
        null=True,
        blank=True,
    )
    text = models.CharField(max_length=255)
    translation = models.CharField(max_length=255, blank=True)
    example = models.TextField(blank=True)
    type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class UserExpressionProgress(models.Model):
    class Meta:
        unique_together = ('user', 'expression')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    expression = models.ForeignKey(
        Expression,
        on_delete=models.CASCADE,
    )

    status = models.CharField(max_length=20, default='new')
    next_review = models.DateField(null=True, blank=True) #ТОЛЬКО ПРМЕРНО, НУЖНО РАЗОБРАТЬСЯ В ІНТЕРВАЛЬНОМ ПОВТОРЕНИИ
    times_reviewed = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)