from datetime import datetime

from django.conf import settings


def global_settings(request):
    return {
        "site_url": settings.SITE_URL,
        "analytics": settings.ANALYTICS,
        "social_links": settings.SOCIAL_LINKS,
        "business": settings.BUSINESS,
        "current_year": datetime.now().year,
    }
