from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import BlogPostSitemap, ServiceSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "blog": BlogPostSitemap,
}

urlpatterns = [
    path("", include("core.urls", namespace="core")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
