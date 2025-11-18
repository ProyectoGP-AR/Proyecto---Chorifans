from django.contrib import admin
from .models import Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "slug",
        "is_active",
        "created_at",
    )

    search_fields = ("nombre", "slug")
    list_filter = ("is_active", "created_at")

    readonly_fields = ("created_at", "updated_at")
