from django.urls import path

from .views import (ArticleListView, ArticleView, AuthorView,
                    CreateArticleView, CreateAuthorView, LatestArticlesFeed)

app_name = "blogapp"

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/<int:pk>", ArticleView.as_view(), name="article_view"),
    path("articles/create/", CreateArticleView.as_view(), name="create_article"),
    path("articles/latest/feed/", LatestArticlesFeed(), name="articles_feed"),
    path("author/<int:pk>/", AuthorView.as_view(), name="author_view"),
    path("author/create/", CreateAuthorView.as_view(), name="create_author"),
]