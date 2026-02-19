from django.test import TestCase
from django.utils import timezone

from core.models import BlogPost, Event, Service, Testimonial


class ModelTests(TestCase):
    def test_service_str(self):
        service = Service.objects.create(name="PPF", slug="ppf", description="Desc")
        self.assertEqual(str(service), "PPF")

    def test_blog_reading_time(self):
        content = "word " * 440
        post = BlogPost.objects.create(
            title="Articol",
            slug="articol",
            summary="Sumar",
            content=content,
            is_published=True,
            published_at=timezone.now(),
        )
        self.assertEqual(post.reading_time_minutes, 2)

    def test_testimonial_rating_limits(self):
        testimonial = Testimonial.objects.create(author="Client", rating=5, comment="Perfect")
        self.assertIn("5/5", str(testimonial))

    def test_event_string_representation(self):
        event = Event.objects.create(event_type="page_view", page="/")
        self.assertIn("page_view", str(event))
