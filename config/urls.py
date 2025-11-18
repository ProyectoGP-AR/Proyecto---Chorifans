from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importamos la API de Django Ninja
from apps.api.api import api

# Importamos la vista de inicio
from config.views import home_view

# ============================================================
# URLS PRINCIPALES DEL PROYECTO CHORIFANS
# ============================================================

urlpatterns = [
    # Panel de administración de Django
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("parrillas/", include("apps.parrillas.urls", namespace="parrillas")),
    path("promociones/", include("apps.promociones.urls", namespace="promociones")),
    path("categorias/", include("apps.categorias.urls", namespace="categorias")),
    path("ubicaciones/", include("apps.ubicaciones.urls", namespace="ubicaciones")),



    # Endpoints de la API (Django Ninja)
    path("api/", api.urls),

    # Página de inicio (ruta vacía "/")
    path("", home_view, name="home"),
   

]

# Servir archivos de MEDIA en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
