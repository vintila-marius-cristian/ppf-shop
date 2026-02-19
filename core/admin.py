from django.contrib import admin

from .models import BlogCategory, BlogPost, BlogTag, ContactMessage, Event, GalleryItem, Service, Testimonial


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_range", "is_featured", "display_order")
    list_filter = ("category", "is_featured")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description", "short_description")


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ("title", "related_service", "is_featured", "created_at")
    list_filter = ("related_service", "is_featured")
    search_fields = ("title", "caption", "description")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_published")
    list_filter = ("is_published", "categories", "tags")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "content")
    filter_horizontal = ("categories", "tags")


admin.site.register(BlogCategory)
admin.site.register(BlogTag)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author", "rating", "source", "date", "is_featured")
    list_filter = ("rating", "source", "is_featured")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_processed")
    list_filter = ("is_processed", "created_at")
    search_fields = ("name", "email", "subject", "message")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "element", "page", "timestamp")
    list_filter = ("event_type", "timestamp")
    search_fields = ("event_type", "element", "page", "session_id")
    readonly_fields = ("timestamp",)
