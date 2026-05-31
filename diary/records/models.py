from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model
from unidecode import unidecode

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey( #юзер
        User,
        on_delete=models.CASCADE,
        related_name="tags",
    )
    def __str__(self):
        return self.name

class Record(models.Model):
    user = models.ForeignKey( #юзер
        User,
        on_delete=models.CASCADE,
        related_name="records",
    )

    title = models.CharField(max_length=100) #заголовок
    slug = models.SlugField(max_length=100, blank=True) #слаг
    content = models.TextField() #мессэдж
    date = models.DateTimeField(auto_now_add = True) #дата создания
    tags = models.ManyToManyField(Tag, blank=True)

    def word_count(self):
        return len(self.content.split())

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            date = self.date or timezone.now()
            title_slug = slugify(unidecode(self.title))
            slug = f"{title_slug}-{date.strftime('%Y%m%d')}"
            counter = 1
            while Record.objects.filter(slug=slug,user=self.user).exists():
                slug = f"{slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)