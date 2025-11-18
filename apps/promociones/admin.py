from django.contrib import admin
from .models import Promocion


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Promociones.
    Muestra título, parrilla, rango de fechas y estado.
    Permite buscar, filtrar y administrar fácilmente las promos.
    """

    # columnas visibles en la lista
    list_display = (
        "id",
        "titulo",
        "parrilla",
        "precio_promocional",
        "fecha_inicio",
        "fecha_fin",
        "is_active",
        "created_at",
    )

    # campos por los que se puede buscar
    search_fields = (
        "titulo",
        "descripcion",
        "parrilla__nombre",
    )

    # filtros laterales
    list_filter = (
        "is_active",
        "fecha_inicio",
        "fecha_fin",
        "parrilla",
    )

    # campos de solo lectura
    readonly_fields = ("created_at", "updated_at")
