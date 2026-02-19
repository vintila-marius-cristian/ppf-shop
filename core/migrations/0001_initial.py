# Generated manually for initial project bootstrap.
from django.core import validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BlogCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(unique=True)),
            ],
            options={
                "verbose_name_plural": "Blog categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="BlogTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("subject", models.CharField(max_length=160)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_processed", models.BooleanField(default=False)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(max_length=100)),
                ("element", models.CharField(blank=True, max_length=255)),
                ("timestamp", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("page", models.CharField(blank=True, max_length=255)),
                ("user_agent", models.TextField(blank=True)),
                ("session_id", models.CharField(blank=True, db_index=True, max_length=128)),
                ("additional_data", models.JSONField(blank=True, default=dict)),
            ],
            options={"ordering": ["-timestamp"]},
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(unique=True)),
                ("short_description", models.CharField(blank=True, max_length=220)),
                ("description", models.TextField()),
                ("image", models.ImageField(blank=True, null=True, upload_to="services/images/")),
                ("video", models.FileField(blank=True, null=True, upload_to="services/videos/")),
                ("price_range", models.CharField(blank=True, max_length=120)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("ppf", "Paint Protection Film"),
                            ("ceramic", "Ceramic Coating"),
                            ("tint", "Window Tinting"),
                            ("detailing", "Detailing"),
                        ],
                        default="ppf",
                        max_length=24,
                    ),
                ),
                ("is_featured", models.BooleanField(default=True)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
                ("seo_title", models.CharField(blank=True, max_length=160)),
                ("seo_description", models.CharField(blank=True, max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["display_order", "name"]},
        ),
        migrations.CreateModel(
            name="Testimonial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("author", models.CharField(max_length=120)),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(5)]
                    ),
                ),
                ("comment", models.TextField()),
                ("date", models.DateField(default=django.utils.timezone.localdate)),
                ("source", models.CharField(default="Google", max_length=80)),
                ("is_featured", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-date", "-created_at"]},
        ),
        migrations.CreateModel(
            name="BlogPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(unique=True)),
                ("author", models.CharField(default="Echipa Premiere Aesthetics", max_length=120)),
                ("content", models.TextField()),
                ("summary", models.TextField()),
                ("featured_image", models.ImageField(blank=True, null=True, upload_to="blog/images/")),
                ("featured_video", models.FileField(blank=True, null=True, upload_to="blog/videos/")),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("is_published", models.BooleanField(default=False)),
                ("seo_title", models.CharField(blank=True, max_length=160)),
                ("seo_description", models.CharField(blank=True, max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("categories", models.ManyToManyField(blank=True, related_name="posts", to="core.blogcategory")),
                ("tags", models.ManyToManyField(blank=True, related_name="posts", to="core.blogtag")),
            ],
            options={"ordering": ["-published_at", "-created_at"]},
        ),
        migrations.CreateModel(
            name="GalleryItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("image", models.ImageField(blank=True, null=True, upload_to="gallery/images/")),
                ("video", models.FileField(blank=True, null=True, upload_to="gallery/videos/")),
                ("description", models.TextField(blank=True)),
                ("caption", models.CharField(blank=True, max_length=255)),
                ("is_featured", models.BooleanField(default=False)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "related_service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="gallery_items",
                        to="core.service",
                    ),
                ),
            ],
            options={"ordering": ["sort_order", "-created_at"]},
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["event_type", "timestamp"], name="core_event_event_ty_1763ff_idx"),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["page", "timestamp"], name="core_event_page_30d268_idx"),
        ),
    ]
