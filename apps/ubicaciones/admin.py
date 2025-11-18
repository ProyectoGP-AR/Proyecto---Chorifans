from django.contrib import admin
from .models import Ubicacion


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre_ciudad",
        "nombre_barrio",
        "is_active",
        "created_at",
    )

    search_fields = (
        "nombre_ciudad",
        "nombre_barrio",
        "google_maps_url",
    )

    list_filter = ("is_active", "nombre_ciudad")
    readonly_fields = ("created_at", "updated_at")
