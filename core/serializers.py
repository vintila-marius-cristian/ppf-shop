from rest_framework import serializers

from .models import BlogPost, ContactMessage, Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["event_type", "element", "page", "user_agent", "session_id", "additional_data"]

    def validate_event_type(self, value: str) -> str:
        if len(value.strip()) < 2:
            raise serializers.ValidationError("event_type must contain at least 2 characters.")
        return value.strip()


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]

    def validate_message(self, value: str) -> str:
        if len(value.strip()) < 15:
            raise serializers.ValidationError("Message must contain at least 15 characters.")
        return value.strip()


class BlogPostSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = BlogPost
        fields = [
            "title",
            "slug",
            "author",
            "summary",
            "content",
            "published_at",
            "categories",
            "tags",
            "reading_time_minutes",
        ]
