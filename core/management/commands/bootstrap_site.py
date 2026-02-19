import shutil
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from core.models import BlogPost, GalleryItem, Service, Testimonial


class Command(BaseCommand):
    help = "Copies client media into MEDIA_ROOT/client and seeds baseline content records."

    def handle(self, *args, **options):
        source = Path(settings.CLIENT_MEDIA_DIR)
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

        if not source.exists():
            local_source = Path(settings.BASE_DIR) / "media" / "client"
            if local_source.exists():
                source = local_source
            else:
                legacy_source = Path(settings.BASE_DIR) / "premiere aestethics content"
                if legacy_source.exists():
                    source = legacy_source

        if source.exists():
            if source.resolve() == target.resolve():
                self.stdout.write(self.style.WARNING("Client media source and target are identical; skipping copy phase."))
            else:
                for file in source.iterdir():
                    if file.is_file():
                        shutil.copy2(file, target / file.name)
                self.stdout.write(self.style.SUCCESS(f"Media copied from {source} to {target}"))
        else:
            self.stdout.write(self.style.WARNING(f"Client media directory not found: {source}"))

        # Keep a deterministic hero video path for templates and prefer the biggest root-level source.
        root_videos = sorted(
            [path for path in Path(settings.BASE_DIR).glob("*.mp4") if path.is_file()],
            key=lambda path: path.stat().st_size,
            reverse=True,
        )
        if root_videos:
            hero_target = target / "hero-fullres.mp4"
            shutil.copy2(root_videos[0], hero_target)
            self.stdout.write(self.style.SUCCESS(f"Hero video synced: {hero_target.name}"))
        else:
            self.stdout.write(self.style.WARNING("No root-level .mp4 video found for hero-fullres.mp4 sync."))

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
