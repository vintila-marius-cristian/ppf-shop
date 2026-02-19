from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand
from PIL import Image


class Command(BaseCommand):
    help = "Converts JPEG/PNG assets from MEDIA_ROOT/client to optimized WebP variants."

    def handle(self, *args, **options):
        media_dir = Path(settings.MEDIA_ROOT) / "client"
        if not media_dir.exists():
            self.stdout.write(self.style.WARNING(f"Directory not found: {media_dir}"))
            return

        converted = 0
        for image_path in media_dir.iterdir():
            if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            target = image_path.with_suffix(".webp")
            with Image.open(image_path) as img:
                img.save(target, "WEBP", quality=82, method=6)
            converted += 1

        self.stdout.write(self.style.SUCCESS(f"Converted {converted} image(s) to WebP."))
