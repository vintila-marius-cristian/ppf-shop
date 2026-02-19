from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BlogPost, Service
from django.contrib.auth import get_user_model


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service = Service.objects.create(
            name="Paint Protection Film",
            slug="ppf",
            description="Descriere",
            short_description="Short",
            category="ppf",
        )
        cls.post = BlogPost.objects.create(
            title="Ghid PPF",
            slug="ghid-ppf",
            summary="Rezumat",
            content="Continut articol",
            is_published=True,
            published_at=timezone.now(),
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Protectie auto")

    def test_service_detail_loads(self):
        response = self.client.get(reverse("core:service_detail", kwargs={"slug": self.service.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.name)

    def test_blog_detail_loads(self):
        response = self.client.get(reverse("core:blog_detail", kwargs={"slug": self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_robots_txt(self):
        response = self.client.get(reverse("core:robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sitemap")

    def test_analytics_dashboard_requires_login(self):
        response = self.client.get(reverse("core:analytics_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("core:owner_login")))

    def test_analytics_dashboard_forbidden_for_non_staff(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="normal", email="normal@example.com", password="test-pass-123")
        self.client.force_login(user)
        response = self.client.get(reverse("core:analytics_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_analytics_dashboard_access_for_staff(self):
        user_model = get_user_model()
        admin_user = user_model.objects.create_superuser(username="admin", email="admin@example.com", password="test-pass-123")
        self.client.force_login(admin_user)
        response = self.client.get(reverse("core:analytics_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_owner_login_page_loads(self):
        response = self.client.get(reverse("core:owner_login"))
        self.assertEqual(response.status_code, 200)
