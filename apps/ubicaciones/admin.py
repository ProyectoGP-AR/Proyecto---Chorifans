from django.contrib import admin
from .models import Ubicacion


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre_barrio",
        "zona",
        "nombre_ciudad",
        "latitud",
        "longitud",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "nombre_ciudad",
        "nombre_barrio",
        "zona",
        "google_maps_url",
    )

    list_filter = (
        "is_active",
        "zona",
        "nombre_ciudad",
    )

    ordering = (
        "zona",
        "nombre_barrio",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_editable = (
        "zona",
        "is_active",
    )

    list_per_page = 50

    fieldsets = (
        (
            "Datos principales",
            {
                "fields": (
                    "nombre_ciudad",
                    "nombre_barrio",
                    "zona",
                    "is_active",
                )
            },
        ),
        (
            "Geolocalización",
            {
                "fields": (
                    "latitud",
                    "longitud",
                    "google_maps_url",
                ),
                "description": (
                    "Completá latitud y longitud para que Chori Bot pueda calcular "
                    "distancias aproximadas entre ubicaciones y parrillas."
                ),
            },
        ),
        (
            "Trazabilidad",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )