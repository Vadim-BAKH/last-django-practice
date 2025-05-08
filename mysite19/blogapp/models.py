"""Модели для блоговой платформы"""

from django.db import models
from django.urls import reverse


class Author(models.Model):
    """Модель автора статьи с именем и биографией."""
    name = models.CharField(max_length=100, null=False, db_index=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=40, null=False, unique=True)
    """Модель категории статьи с уникальным названием."""

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=20, null=False, unique=True, db_index=True
    )
    """Модель тэга статьи с уникальным названием."""

    def __str__(self):
        return self.name

class Article(models.Model):
    """
    Модель статьи.

    С заголовком, содержимым, датой, автором, категорией и тэгами.
    """
    title = models.CharField(max_length=200, null=False, db_index=True)
    content = models.TextField(null=False)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="articles")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='articles')

    def get_absolute_url(self):
        return reverse("blogapp:article_view", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Article (pk={self.pk}, title: {self.title!r})"
