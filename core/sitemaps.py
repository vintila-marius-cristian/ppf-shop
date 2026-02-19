from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import BlogPost, Service


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return ["core:home", "core:service_list", "core:gallery", "core:about", "core:blog_list", "core:contact", "core:testimonials"]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return Service.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class BlogPostSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
