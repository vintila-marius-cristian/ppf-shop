from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Service(models.Model):
    CATEGORY_CHOICES = [
        ("ppf", "Paint Protection Film"),
        ("ceramic", "Ceramic Coating"),
        ("tint", "Window Tinting"),
        ("detailing", "Detailing"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=220, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to="services/images/", blank=True, null=True)
    video = models.FileField(upload_to="services/videos/", blank=True, null=True)
    price_range = models.CharField(max_length=120, blank=True)
    category = models.CharField(max_length=24, choices=CATEGORY_CHOICES, default="ppf")
    is_featured = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("core:service_detail", kwargs={"slug": self.slug})


class GalleryItem(models.Model):
    title = models.CharField(max_length=160)
    image = models.ImageField(upload_to="gallery/images/", blank=True, null=True)
    video = models.FileField(upload_to="gallery/videos/", blank=True, null=True)
    related_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name="gallery_items")
    description = models.TextField(blank=True)
    caption = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return self.title


class BlogCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Blog categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class BlogTag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.CharField(max_length=120, default="Echipa Premiere Aesthetics")
    content = models.TextField()
    summary = models.TextField()
    featured_image = models.ImageField(upload_to="blog/images/", blank=True, null=True)
    featured_video = models.FileField(upload_to="blog/videos/", blank=True, null=True)
    categories = models.ManyToManyField(BlogCategory, blank=True, related_name="posts")
    tags = models.ManyToManyField(BlogTag, blank=True, related_name="posts")
    published_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("core:blog_detail", kwargs={"slug": self.slug})

    @property
    def reading_time_minutes(self) -> int:
        word_count = len(self.content.split())
        return max(1, round(word_count / 220))


class Testimonial(models.Model):
    author = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    date = models.DateField(default=timezone.localdate)
    source = models.CharField(max_length=80, default="Google")
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.author} ({self.rating}/5)"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    subject = models.CharField(max_length=160)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.subject}"


class Event(models.Model):
    event_type = models.CharField(max_length=100)
    element = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    page = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=128, blank=True, db_index=True)
    additional_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["event_type", "timestamp"]),
            models.Index(fields=["page", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.page}"
