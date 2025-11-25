# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.api.api import api
from config.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("apps.accounts.urls")),
    path("parrillas/", include("apps.parrillas.urls")),
    path("categorias/", include("apps.categorias.urls")),
    path("ubicaciones/", include("apps.ubicaciones.urls")),
    path("promociones/", include("apps.promociones.urls")),
    path("resenas/", include("apps.resenas.urls")),

    path("api/", api.urls),

    path("", HomeView.as_view(), name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
