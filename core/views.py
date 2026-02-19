import json
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, FormView, ListView, TemplateView
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ContactForm, OwnerLoginForm
from .models import BlogPost, Event, GalleryItem, Service, Testimonial
from .serializers import BlogPostSerializer, ContactSerializer, EventSerializer


SERVICE_FAQS = {
    "ppf": [
        {"q": "Cat dureaza aplicarea PPF?", "a": "Intre 2 si 5 zile, in functie de suprafata protejata si complexitatea panourilor."},
        {"q": "PPF se ingalbeneste in timp?", "a": "Foliile premium moderne au protectie UV avansata si rezista excelent in climatul din Romania."},
    ],
    "ceramic": [
        {"q": "Ceramic coating inlocuieste spalarea?", "a": "Nu, dar reduce aderenta murdariei si usureaza spalarea periodica."},
        {"q": "Cat rezista tratamentul ceramic?", "a": "In functie de pachet, intre 2 si 5 ani cu intretinere corecta."},
    ],
    "tint": [
        {"q": "Folia de geam este omologata?", "a": "Da, folosim folii conforme si oferim documentatie pentru omologare."},
        {"q": "Ajuta la reducerea temperaturii?", "a": "Da, reduce semnificativ transferul termic si radiatia UV in habitaclu."},
    ],
    "detailing": [
        {"q": "Ce include detailing-ul complet?", "a": "Curatare interior/exterior, corectie de lac, decontaminare si protectie."},
        {"q": "Pot combina detailing cu PPF?", "a": "Da, aceasta combinatie este recomandata pentru rezultate premium pe termen lung."},
    ],
}


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["services"] = Service.objects.filter(is_featured=True)[:4]
        context["testimonials"] = Testimonial.objects.filter(is_featured=True)[:6]
        context["recent_posts"] = BlogPost.objects.filter(is_published=True)[:3]
        context["gallery_highlights"] = GalleryItem.objects.filter(is_featured=True)[:6]
        return context


class ServiceListView(ListView):
    template_name = "core/service_list.html"
    context_object_name = "services"
    queryset = Service.objects.all()


class ServiceDetailView(DetailView):
    template_name = "core/service_detail.html"
    context_object_name = "service"
    queryset = Service.objects.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        service = self.object
        context["faqs"] = SERVICE_FAQS.get(service.slug, SERVICE_FAQS.get(service.category, []))
        context["related_media"] = service.gallery_items.all()[:8]
        return context


class GalleryView(TemplateView):
    template_name = "core/gallery.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        service_slug = self.request.GET.get("service")
        items = GalleryItem.objects.select_related("related_service")
        if service_slug:
            items = items.filter(related_service__slug=service_slug)
        context["services"] = Service.objects.all()
        context["gallery_items"] = items
        context["active_service"] = service_slug
        return context


class AboutView(TemplateView):
    template_name = "core/about.html"


class BlogListView(ListView):
    template_name = "core/blog_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True).prefetch_related("categories", "tags")
        category = self.request.GET.get("category")
        tag = self.request.GET.get("tag")
        if category:
            queryset = queryset.filter(categories__slug=category)
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        return queryset.distinct()


class BlogDetailView(DetailView):
    template_name = "core/blog_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).prefetch_related("categories", "tags")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["related_posts"] = BlogPost.objects.filter(is_published=True).exclude(id=self.object.id)[:3]
        return context


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("core:contact")

    def form_valid(self, form: ContactForm):
        message = form.save()
        send_mail(
            subject=f"[Website] {message.subject}",
            message=(
                f"Nume: {message.name}\n"
                f"Email: {message.email}\n"
                f"Telefon: {message.phone}\n"
                f"Mesaj:\n{message.message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=True,
        )

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "ok", "message": "Mesaj trimis cu succes."}, status=201)

        messages.success(self.request, "Mesajul a fost trimis. Revenim cu un raspuns in cel mai scurt timp.")
        return super().form_valid(form)

    def form_invalid(self, form: ContactForm):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
        return super().form_invalid(form)


class TestimonialListView(ListView):
    template_name = "core/testimonials.html"
    context_object_name = "testimonials"
    queryset = Testimonial.objects.all()


class OwnerLoginView(LoginView):
    template_name = "core/owner_login.html"
    authentication_form = OwnerLoginForm
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse_lazy("core:analytics_dashboard")

    def form_valid(self, form):
        if not form.get_user().is_staff:
            form.add_error(None, "Contul nu are acces la panoul de analytics.")
            return self.form_invalid(form)
        return super().form_valid(form)


class OwnerLogoutView(LogoutView):
    next_page = reverse_lazy("core:owner_login")


class AdminOnlyMixin(LoginRequiredMixin):
    login_url = reverse_lazy("core:owner_login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            return HttpResponseForbidden("Access denied.")
        return super().dispatch(request, *args, **kwargs)


class AnalyticsDashboardView(AdminOnlyMixin, TemplateView):
    template_name = "core/analytics_dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        total_events = Event.objects.count()
        total_page_views = Event.objects.filter(event_type="page_view").count()
        total_contact = Event.objects.filter(event_type="contact_submit").count()

        top_elements_qs = (
            Event.objects.exclude(element="")
            .values("element")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )

        top_pages_qs = (
            Event.objects.exclude(page="")
            .values("page")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )

        timeline_qs = (
            Event.objects.annotate(day=TruncDate("timestamp"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )

        scroll_values = []
        for event in Event.objects.filter(event_type="scroll_depth")[:300]:
            depth = event.additional_data.get("depth")
            if isinstance(depth, (int, float)):
                scroll_values.append(depth)

        context.update(
            {
                "total_events": total_events,
                "total_page_views": total_page_views,
                "total_contact": total_contact,
                "top_elements": list(top_elements_qs),
                "top_pages": list(top_pages_qs),
                "chart_labels": json.dumps([entry["day"].isoformat() for entry in timeline_qs]),
                "chart_values": json.dumps([entry["total"] for entry in timeline_qs]),
                "avg_scroll_depth": round(sum(scroll_values) / len(scroll_values), 2) if scroll_values else 0,
            }
        )
        return context


@require_GET
def robots_txt(_: HttpRequest) -> HttpResponse:
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /owner/",
        f"Sitemap: {settings.SITE_URL.rstrip('/')}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


class TrackEventAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request: HttpRequest) -> Response:
        payload = request.data.copy()
        payload.setdefault("user_agent", request.META.get("HTTP_USER_AGENT", ""))
        serializer = EventSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save(timestamp=timezone.now())
        return Response({"status": "tracked"}, status=status.HTTP_201_CREATED)


class ContactSubmissionAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request: HttpRequest) -> Response:
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        send_mail(
            subject=f"[Website API] {contact.subject}",
            message=(
                f"Nume: {contact.name}\n"
                f"Email: {contact.email}\n"
                f"Telefon: {contact.phone}\n"
                f"Mesaj:\n{contact.message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=True,
        )
        return Response({"status": "ok", "id": contact.id}, status=status.HTTP_201_CREATED)


class PublishedBlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).prefetch_related("categories", "tags")
