from django.contrib import admin
from django.utils.html import mark_safe

from .models import Parrilla


@admin.register(Parrilla)
class ParrillaAdmin(admin.ModelAdmin):
    """
    Configuración de la parrilla en el panel de administración.
    Incluye búsqueda, filtros y preview de la foto principal.
    """

    list_display = (
        "id",
        "nombre",
        "categoria",
        "ubicacion",
        "is_active",
        "promedio_puntaje",
        "foto_preview",
        "created_at",
    )

    search_fields = (
        "nombre",
        "descripcion",
        "direccion",
        "telefono",
        "sitio_web",
        "ubicacion__nombre_ciudad",
        "ubicacion__nombre_barrio",
        "categoria__nombre",
    )

    list_filter = (
        "is_active",
        "categoria",
        "ubicacion__nombre_ciudad",
        "ubicacion__nombre_barrio",
    )

    readonly_fields = ("created_at", "updated_at", "foto_preview")

    def foto_preview(self, obj):
        """
        Muestra una miniatura cuadrada de la foto principal.
        """
        if obj.foto_principal:
            return mark_safe(
                f'<img src="{obj.foto_principal.url}" width="60" height="60" style="object-fit: cover; border-radius: 8px;" />'
            )
        return "Sin foto"

    foto_preview.short_description = "Foto"
