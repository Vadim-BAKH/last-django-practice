from django.contrib.sitemaps import Sitemap

from .models import Article


class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5
    def items(self):
        return (Article.objects
                .select_related("author", "category")
                .prefetch_related("tags")
                .defer("content")
                .order_by("-pub_date")[:5])

    def lastmod(self, obj: Article):
        return obj.pub_date
