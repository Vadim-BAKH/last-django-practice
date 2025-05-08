from django.contrib import admin

from .models import Article, Author, Category


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "content", "author", "pub_date", "category",
    )
    list_display_links = (
        "id", "title", "author", "pub_date", "category",
    )
    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    display_tags.short_description = "Tags"

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "bio",)
    list_display_links = ("id", "name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)