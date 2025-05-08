from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.syndication.views import Feed
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .forms import ArticleForm, AuthorForm
from .models import Article, Author, Category, Tag


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return (Article.objects
                .select_related("author", "category")
                .prefetch_related("tags")
                .defer("content")
                .order_by("-pub_date")[:5])

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:15]



class ArticleListView(
    LoginRequiredMixin, ListView
):
    model = Article
    template_name = "blogapp/article_list.html"
    context_object_name = "articles"

    def get_queryset(self):
        queryset = super().get_queryset()
        return ((queryset
                .select_related("author", "category")
                .prefetch_related("tags"))
                .defer("content")
                .order_by("-pub_date"))


class CreateArticleView(
    LoginRequiredMixin, CreateView
):
    model = Article
    form_class = ArticleForm
    template_name = "blogapp/create_article.html"
    success_url = reverse_lazy("blogapp:articles")

    def form_valid(self, form):
        article = form.save(commit=False)

        art_category_name = form.cleaned_data.get("new_category").strip()
        article.category  = Category.objects.create(name=art_category_name)
        article.save()
        tags_str = form.cleaned_data.get("new_tags", "")
        tag_names = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name__iexact=tag_name,
                defaults={"name": tag_name}
            )
            article.tags.add(tag)
        return super().form_valid(form)


class ArticleView(LoginRequiredMixin, DetailView):
    template_name = "blogapp/article_view.html"
    context_object_name = "article"
    queryset = Article.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy("blogapp:articles"))


class CreateAuthorView(LoginRequiredMixin, CreateView):

    template_name = "blogapp/create_author.html"
    form_class = AuthorForm

    def get_success_url(self):
        return reverse_lazy("blogapp:author_view", kwargs={"pk": self.object.pk})


class AuthorView(LoginRequiredMixin, DetailView):

    template_name = "blogapp/author_view.html"
    context_object_name = "author"
    queryset = Author.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy("blogapp:create_author"))
