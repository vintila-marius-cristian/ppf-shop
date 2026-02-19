from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .views import (
    AboutView,
    AnalyticsDashboardView,
    BlogDetailView,
    BlogListView,
    ContactSubmissionAPIView,
    ContactView,
    GalleryView,
    HomeView,
    OwnerLoginView,
    OwnerLogoutView,
    PublishedBlogPostViewSet,
    ServiceDetailView,
    ServiceListView,
    TestimonialListView,
    TrackEventAPIView,
    robots_txt,
)

app_name = "core"

router = DefaultRouter()
router.register("blog/posts", PublishedBlogPostViewSet, basename="blog-post")

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("services/", ServiceListView.as_view(), name="service_list"),
    path("services/<slug:slug>/", ServiceDetailView.as_view(), name="service_detail"),
    path("gallery/", GalleryView.as_view(), name="gallery"),
    path("about/", AboutView.as_view(), name="about"),
    path("blog/", BlogListView.as_view(), name="blog_list"),
    path("blog/<slug:slug>/", BlogDetailView.as_view(), name="blog_detail"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("testimonials/", TestimonialListView.as_view(), name="testimonials"),
    path("owner/login/", OwnerLoginView.as_view(), name="owner_login"),
    path("owner/logout/", OwnerLogoutView.as_view(), name="owner_logout"),
    path("owner/analytics/", AnalyticsDashboardView.as_view(), name="analytics_dashboard"),
    path("privacy/", TemplateView.as_view(template_name="core/privacy.html"), name="privacy"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("api/track/", TrackEventAPIView.as_view(), name="api_track"),
    path("api/contact/", ContactSubmissionAPIView.as_view(), name="api_contact"),
    path("api/", include(router.urls)),
]
