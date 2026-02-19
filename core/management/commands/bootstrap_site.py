import shutil
import re
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from core.models import BlogPost, GalleryItem, Service, Testimonial


class Command(BaseCommand):
    help = "Copies client media into MEDIA_ROOT/client and seeds baseline content records."

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".bmp", ".gif"}
    VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".m4v", ".mkv", ".avi"}
    SERVICE_KEYWORDS = (
        ("ppf", "ppf"),
        ("folie", "ppf"),
        ("paint", "ppf"),
        ("clearbra", "ppf"),
        ("ceramic", "ceramic"),
        ("coating", "ceramic"),
        ("tint", "tint"),
        ("geam", "tint"),
        ("window", "tint"),
        ("detail", "detailing"),
        ("interior", "detailing"),
        ("exterior", "detailing"),
    )

    def _resolve_media_source(self) -> Path | None:
        source = Path(settings.CLIENT_MEDIA_DIR)
        if source.exists():
            return source

        local_source = Path(settings.BASE_DIR) / "media" / "client"
        if local_source.exists():
            return local_source

        legacy_source = Path(settings.BASE_DIR) / "premiere aestethics content"
        if legacy_source.exists():
            return legacy_source

        return None

    def _copy_media_tree(self, source: Path, target: Path) -> int:
        copied_count = 0
        for file_path in source.rglob("*"):
            if not file_path.is_file():
                continue
            relative = file_path.relative_to(source)
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                source_stat = file_path.stat()
                destination_stat = destination.stat()
                if (
                    source_stat.st_size == destination_stat.st_size
                    and int(source_stat.st_mtime) == int(destination_stat.st_mtime)
                ):
                    continue
            shutil.copy2(file_path, destination)
            copied_count += 1
        return copied_count

    def _sync_hero_video(self, target: Path, source: Path | None) -> None:
        candidates = [path for path in Path(settings.BASE_DIR).glob("*.mp4") if path.is_file()]
        if source and source.exists():
            candidates.extend([path for path in source.rglob("*") if path.is_file() and path.suffix.lower() in self.VIDEO_EXTENSIONS])
        candidates.extend([path for path in target.rglob("*") if path.is_file() and path.suffix.lower() in self.VIDEO_EXTENSIONS])

        if not candidates:
            self.stdout.write(self.style.WARNING("No video found to sync hero-fullres.mp4."))
            return

        best_video = max(candidates, key=lambda path: path.stat().st_size)
        hero_target = target / "hero-fullres.mp4"
        if best_video.resolve() != hero_target.resolve():
            shutil.copy2(best_video, hero_target)
            self.stdout.write(self.style.SUCCESS(f"Hero video synced from {best_video.name} to {hero_target.name}"))
        else:
            self.stdout.write(self.style.SUCCESS("Hero video already up to date."))

    def _humanize_title(self, path: Path) -> str:
        cleaned = re.sub(r"[_-]+", " ", path.stem)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned.title() or "Proiect"

    def _guess_service(self, relative_path: str, services_by_category: dict[str, Service]) -> Service | None:
        lower = relative_path.lower()
        for keyword, category in self.SERVICE_KEYWORDS:
            if keyword in lower and category in services_by_category:
                return services_by_category[category]
        return services_by_category.get("ppf")

    def _sync_gallery_items(self, target: Path, services_by_category: dict[str, Service]) -> int:
        existing_images = {value for value in GalleryItem.objects.values_list("image", flat=True) if value}
        existing_videos = {value for value in GalleryItem.objects.values_list("video", flat=True) if value}
        featured_slots = max(0, 12 - GalleryItem.objects.filter(is_featured=True).count())
        created_count = 0

        media_files = sorted(
            [
                path
                for path in target.rglob("*")
                if path.is_file() and path.suffix.lower() in (self.IMAGE_EXTENSIONS | self.VIDEO_EXTENSIONS)
            ],
            key=lambda item: item.name.lower(),
        )

        for media_path in media_files:
            if media_path.name.lower() == "hero-fullres.mp4":
                continue

            relative = f"client/{media_path.relative_to(target).as_posix()}"
            suffix = media_path.suffix.lower()
            service = self._guess_service(relative, services_by_category)
            should_feature = featured_slots > 0
            title = self._humanize_title(media_path)
            caption = "Lucrare reala din atelier Premiere Aesthetics."

            if suffix in self.IMAGE_EXTENSIONS:
                if relative in existing_images:
                    continue
                GalleryItem.objects.create(
                    title=title,
                    image=relative,
                    related_service=service,
                    caption=caption,
                    description=f"Material importat automat din {relative}.",
                    is_featured=should_feature,
                    sort_order=500 + created_count,
                )
                existing_images.add(relative)
            else:
                if relative in existing_videos:
                    continue
                GalleryItem.objects.create(
                    title=title,
                    video=relative,
                    related_service=service,
                    caption=caption,
                    description=f"Material video importat automat din {relative}.",
                    is_featured=should_feature,
                    sort_order=500 + created_count,
                )
                existing_videos.add(relative)

            created_count += 1
            if should_feature:
                featured_slots -= 1

        return created_count

    def handle(self, *args, **options):
        source = self._resolve_media_source()
        target = Path(settings.MEDIA_ROOT) / "client"
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError:
            fallback_root = Path(settings.BASE_DIR) / "media"
            target = fallback_root / "client"
            target.mkdir(parents=True, exist_ok=True)
            self.stdout.write(
                self.style.WARNING(
                    f"MEDIA_ROOT path is not writable ({settings.MEDIA_ROOT}). "
                    f"Using local fallback: {target.parent}"
                )
            )

        if source and source.exists():
            if source.resolve() == target.resolve():
                self.stdout.write(self.style.WARNING("Client media source and target are identical; skipping copy phase."))
            else:
                copied_count = self._copy_media_tree(source, target)
                self.stdout.write(self.style.SUCCESS(f"Media synced from {source} to {target} ({copied_count} files copied)."))
        else:
            self.stdout.write(self.style.WARNING("Client media directory not found. Continuing with existing media volume content."))

        self._sync_hero_video(target, source)

        services = [
            {
                "name": "Paint Protection Film",
                "slug": "ppf",
                "category": "ppf",
                "short_description": "Protectie invizibila premium impotriva loviturilor de pietre si zgarieturilor.",
                "description": "Aplicam folii PPF premium pe zone partiale sau integrale, cu finisaj optic clar si proprietati self-healing.",
                "image": "client/image-1.jpeg",
                "video": "client/video-1.mp4",
                "price_range": "de la 450 EUR",
                "seo_title": "PPF Pitesti | Protectie premium pentru vopsea",
                "seo_description": "Folie PPF premium in Pitesti, montaj profesionist si garantie pentru protectie pe termen lung.",
                "display_order": 1,
            },
            {
                "name": "Ceramic Coating",
                "slug": "ceramic-coating",
                "category": "ceramic",
                "short_description": "Strat hidrofob avansat pentru luciu si intretinere simplificata.",
                "description": "Pachete de ceramic coating pentru caroserie, jante si suprafete sensibile.",
                "image": "client/image-2.jpeg",
                "video": "client/video-2.mp4",
                "price_range": "de la 300 EUR",
                "seo_title": "Ceramic Coating Pitesti | Luciu si protectie",
                "seo_description": "Tratament ceramic profesional pentru protectie UV, hidrofobie si aspect premium.",
                "display_order": 2,
            },
            {
                "name": "Window Tinting",
                "slug": "window-tinting",
                "category": "tint",
                "short_description": "Confort termic, intimitate si protectie UV cu folii omologate.",
                "description": "Montaj de folii auto pentru geamuri, optimizate pentru reducerea caldurii si protectie UV.",
                "image": "client/image-3.jpeg",
                "video": "client/video-3.mp4",
                "price_range": "de la 180 EUR",
                "seo_title": "Folie geamuri auto Pitesti | Window Tinting",
                "seo_description": "Folie auto omologata pentru geamuri, montaj profesionist si performanta termica in Pitesti.",
                "display_order": 3,
            },
            {
                "name": "Detailing Complet",
                "slug": "detailing",
                "category": "detailing",
                "short_description": "Refacere estetica interior/exterior pentru masini premium.",
                "description": "Detailing complet cu corectie de lac, decontaminare si finisaje de showroom.",
                "image": "client/image-4.jpeg",
                "price_range": "de la 250 EUR",
                "seo_title": "Auto Detailing Pitesti | Finisaj showroom",
                "seo_description": "Servicii complete de auto detailing in Pitesti pentru interior si exterior.",
                "display_order": 4,
            },
        ]

        for payload in services:
            Service.objects.update_or_create(slug=payload["slug"], defaults=payload)

        services_by_category = {service.category: service for service in Service.objects.all()}
        synced_gallery_items = self._sync_gallery_items(target, services_by_category)
        if synced_gallery_items:
            self.stdout.write(self.style.SUCCESS(f"Gallery synced: {synced_gallery_items} media item(s) imported."))

        if not Testimonial.objects.exists():
            Testimonial.objects.bulk_create(
                [
                    Testimonial(author="Andrei M.", rating=5, comment="Atentie la detalii impecabila. PPF-ul arata perfect.", source="Google"),
                    Testimonial(author="Cristina V.", rating=5, comment="Ceramic coating aplicat excelent, masina ramane curata mai mult.", source="Facebook"),
                    Testimonial(author="Mihai P.", rating=5, comment="Echipa profesionista, comunicare clara si rezultat premium.", source="Instagram"),
                ]
            )

        blog_posts = [
            {
                "title": "Cum alegi corect PPF pentru masina ta in Pitesti",
                "slug": "cum-alegi-corect-ppf",
                "summary": (
                    "Ghid complet pentru alegerea foliei PPF: evaluare initiala, selectie material, "
                    "estimare de cost si reguli de mentenanta."
                ),
                "content": """
SECTIUNEA 1 - Analiza masinii inainte de montaj
Primul pas este inspectia completa a caroseriei in lumina rece, pentru a identifica zgarieturi fine, zone revopsite si eventuale defecte de lac. Daca suprafata are contaminanti, decontaminarea si o corectie usoara sunt obligatorii inainte de aplicarea foliei. Fara aceasta etapa, folia poate sigila imperfectiuni care vor ramane vizibile in timp. O pregatire corecta reduce riscul de margini ridicate si creste durata de viata a montajului. In atelierul nostru documentam fiecare panou si discutam transparent ce este necesar inainte de montaj.

SECTIUNEA 2 - Alegerea tipului de folie PPF
Nu toate foliile PPF ofera acelasi nivel de claritate, elasticitate sau rezistenta la pete. Pentru utilizare urbana intensa recomandam o folie cu self-healing rapid si protectie UV stabila pe termen lung. Pentru masini expuse frecvent la drum lung, are sens sa cresti acoperirea pe zonele cu impact ridicat, precum bara, capota si oglinzile. Diferenta dintre un pachet partial si unul complet trebuie evaluata in functie de stilul tau de condus si de nivelul estetic dorit. O selectie buna inseamna mai putine interventii cosmetice pe termen mediu.

SECTIUNEA 3 - Buget, garantie si mentenanta
Costul final trebuie evaluat impreuna cu garantia materialului si experienta echipei de montaj. Un pret aparent mai mic poate ascunde folii cu rezistenta slaba la pete sau ingalbenire prematura. Dupa montaj, spalarea manuala si produsele cu pH neutru ajuta la mentinerea claritatii foliei. Verificarea periodica a muchiilor si a zonelor critice previne degradarea in timp. Cu o mentenanta corecta, PPF-ul ramane o investitie predictibila si eficienta.
                """.strip(),
                "seo_title": "PPF Pitesti: cum alegi folia potrivita",
                "seo_description": "Afla cum sa alegi folia PPF potrivita pentru masina ta, cu sfaturi detaliate de la specialisti din Pitesti.",
                "featured_image": "client/image-1.jpeg",
            },
            {
                "title": "Ceramic coating vs. sealant: ce alegi pentru masina ta",
                "slug": "ceramic-coating-vs-sealant",
                "summary": (
                    "Comparatie practica intre coating ceramic si sealant: protectie reala, durata, cost total "
                    "si scenarii in care merita fiecare varianta."
                ),
                "content": """
SECTIUNEA 1 - Diferenta de protectie in utilizarea zilnica
Sealant-ul clasic ofera un luciu bun pe termen scurt si un efect hidrofob decent, dar performanta lui scade mai rapid in conditii dure. Coating-ul ceramic creeaza un strat mai rezistent la chimicale usoare, oxidare si contaminare urbana. In trafic aglomerat, unde masina este expusa la praf abraziv si spalari dese, aceasta diferenta devine evidenta dupa primele luni. Coating-ul nu elimina necesitatea spalarii, dar reduce aderenta murdariei si usureaza intretinerea. Practic, economisesti timp la fiecare spalare si mentii mai usor un aspect premium.

SECTIUNEA 2 - Durata, cost si predictibilitate
Sealant-ul este mai accesibil initial, dar necesita reaplicari periodice pentru a mentine protectia. Coating-ul are un cost initial mai mare, insa durata de exploatare este considerabil mai buna atunci cand este intretinut corect. Daca analizezi costul pe 2-3 ani, diferenta se echilibreaza in multe cazuri. O alegere buna depinde de cat timp vrei sa pastrezi masina si de cat de mult conteaza consistenta aspectului. Important este sa compari pachete care includ pregatirea suprafetei, nu doar aplicarea produsului.

SECTIUNEA 3 - Cand merita combinatia cu PPF
Pentru panourile cu risc ridicat de impact, PPF ramane prima linie de aparare impotriva ciupiturilor si zgarieturilor. Coating-ul ceramic poate fi aplicat peste zonele protejate pentru hidrofobie suplimentara si curatare mai usoara. Aceasta combinatie este utila mai ales pe masini noi sau recent reconditionate, unde vrei sa conservi finisajul cat mai mult. Strategia corecta este sa definesti zonele critice pentru PPF, apoi sa completezi restul suprafetelor cu coating. Rezultatul este un pachet echilibrat intre protectie mecanica si intretinere simplificata.
                """.strip(),
                "seo_title": "Ceramic Coating vs Sealant",
                "seo_description": "Comparatie clara intre ceramic coating si sealant pentru protectia caroseriei si costul total pe termen mediu.",
                "featured_image": "client/image-2.jpeg",
            },
            {
                "title": "Plan de intretinere dupa PPF si coating: primele 90 de zile",
                "slug": "plan-intretinere-ppf-coating-90-zile",
                "summary": (
                    "Plan simplu, pe etape, pentru intretinerea masinii dupa aplicarea PPF si ceramic coating, "
                    "cu reguli clare pentru spalare si verificari periodice."
                ),
                "content": """
SECTIUNEA 1 - Primele 7 zile dupa aplicare
In prima saptamana evita spalarea agresiva si nu folosi jetul foarte aproape de muchiile foliei. Adezivul are nevoie de timp pentru stabilizare, iar interventiile premature pot afecta aderenta. Este normal sa observi mici urme de umiditate in anumite zone, acestea dispar pe masura ce materialul se stabilizeaza. Parcarea in zone curate si evitarea contaminarii intense ajuta mult in aceasta etapa. Daca apar intrebari, un control rapid in atelier previne corectii costisitoare mai tarziu.

SECTIUNEA 2 - Rutina de spalare intre 2 si 6 saptamani
Spalarea manuala cu manusa moale si sampon pH neutru este cea mai sigura varianta pentru PPF si coating. Evita periile dure si produsele foarte alcaline, deoarece pot reduce performanta hidrofoba in timp. Clatirea corecta si uscarea cu prosop de microfibra curat limiteaza aparitia petelor minerale. Pentru jante si zone foarte murdare foloseste solutii dedicate, testate pe suprafete protejate. O rutina constanta este mai eficienta decat interventii rare, dar agresive.

SECTIUNEA 3 - Verificari lunare si corectii preventive
La fiecare 30 de zile verifica vizual muchiile foliei, capota, bara si oglinzile, unde uzura este de obicei mai mare. Daca observi depuneri persistente, indeparteaza-le cu produse sigure pentru PPF, nu cu abrazivi. Un refresh hidrofob aplicat la intervale regulate mentine comportamentul de respingere a apei. In cazul masinilor folosite zilnic pe drumuri aglomerate, o inspectie profesionala trimestriala este recomandata. Prevenirea este intotdeauna mai ieftina decat refacerea unor panouri deteriorate.
                """.strip(),
                "seo_title": "Intretinere PPF si coating in primele 90 de zile",
                "seo_description": "Ghid practic de intretinere pentru PPF si ceramic coating, cu pasi clari pentru primele 90 de zile.",
                "featured_image": "client/image-3.jpeg",
            },
        ]

        for index, payload in enumerate(blog_posts):
            publish_date = timezone.now() - timedelta(days=index)
            defaults = {
                "title": payload["title"],
                "author": "Echipa Premiere Aesthetics",
                "summary": payload["summary"],
                "content": payload["content"],
                "featured_image": payload["featured_image"],
                "is_published": True,
                "published_at": publish_date,
                "seo_title": payload["seo_title"],
                "seo_description": payload["seo_description"],
            }
            post, created = BlogPost.objects.get_or_create(slug=payload["slug"], defaults=defaults)
            if not created:
                for field, value in defaults.items():
                    setattr(post, field, value)
                post.save()

        if not GalleryItem.objects.exists():
            ppf_service = Service.objects.filter(slug="ppf").first()
            GalleryItem.objects.create(
                title="PPF Full Front",
                related_service=ppf_service,
                caption="Protectie front complet pentru un sedan premium.",
                description="Montaj full-front realizat in conditii controlate.",
                image="client/image-1.jpeg",
                is_featured=True,
            )

        self.stdout.write(self.style.SUCCESS("Baseline content created."))
