from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BlogPost, Service


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

    def test_django_admin_not_exposed(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 404)
