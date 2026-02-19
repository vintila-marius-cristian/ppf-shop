import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BlogPost, ContactMessage, Event


class ApiTests(TestCase):
    def test_track_event_api(self):
        response = self.client.post(
            reverse("core:api_track"),
            data=json.dumps(
                {
                    "event_type": "cta_click",
                    "element": "hero_contact",
                    "page": "/",
                    "session_id": "test-session",
                    "additional_data": {"source": "unit-test"},
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 1)

    def test_contact_api(self):
        response = self.client.post(
            reverse("core:api_contact"),
            data=json.dumps(
                {
                    "name": "Client Test",
                    "email": "client@test.ro",
                    "phone": "+40740111223",
                    "subject": "Programare",
                    "message": "As dori o programare pentru ceramic coating.",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_blog_api_lists_published_posts(self):
        BlogPost.objects.create(
            title="Ghid test",
            slug="ghid-test",
            summary="S",
            content="C",
            is_published=True,
            published_at=timezone.now(),
        )
        response = self.client.get("/api/blog/posts/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
