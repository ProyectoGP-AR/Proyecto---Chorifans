from django.contrib import admin
from django.utils.html import mark_safe

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Configuración del modelo Profile en el panel de administración.
    Muestra datos básicos del usuario, nickname y un preview del avatar.
    """

    # Columnas que se ven en la lista
    list_display = (
        "id",
        "user",
        "nickname",
        "email_usuario",
        "is_active",
        "avatar_preview",
        "created_at",
    )

    # Campos por los que se puede buscar
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "nickname",
    )

    # Filtros laterales
    list_filter = ("is_active", "created_at", "updated_at")

    # Campos de solo lectura (no editables desde admin)
    readonly_fields = ("created_at", "updated_at", "avatar_preview")

    def email_usuario(self, obj):
        """
        Devuelve el email del usuario asociado.
        """
        return obj.user.email

    email_usuario.short_description = "Email"

    def avatar_preview(self, obj):
        """
        Muestra una miniatura del avatar en el admin.
        Si no hay avatar, devuelve un texto.
        """
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />'
            )
        return "Sin avatar"

    avatar_preview.short_description = "Avatar"
