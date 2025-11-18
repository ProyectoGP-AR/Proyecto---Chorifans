from django.contrib import admin
from .models import Resena


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    """
    Configuración de las reseñas en el panel de administración.
    Permite ver quién reseñó qué parrilla, con cuántos choripanes
    y filtrar/buscar fácilmente.
    """

    # Columnas que se ven en el listado
    list_display = (
        "id",
        "usuario",
        "parrilla",
        "puntaje",
        "puntaje_emoji",
        "is_active",
        "created_at",
    )

    # Campos por los que se puede buscar
    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "parrilla__nombre",
        "comentario",
    )

    # Filtros laterales
    list_filter = (
        "is_active",
        "puntaje",
        "created_at",
    )

    # Campos de solo lectura
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    def puntaje_emoji(self, obj):
        """
        Muestra choripanes según el puntaje.
        Ej:
        - 1 -> 🌭 (1/5)
        - 3 -> 🌭🌭🌭 (3/5)
        - 5 -> 🌭🌭🌭🌭🌭 (5/5)
        """
        return f"{'🌭' * obj.puntaje} ({obj.puntaje}/5)"

    puntaje_emoji.short_description = "Puntaje (choripanes)"
