from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Perfil extendido del usuario.
    Guarda datos extra sin modificar el modelo User estándar.
    """

    # Relación 1 a 1 con el usuario de Django
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,      # Si se borra el usuario, se borra el perfil
        related_name="profile",        # Permite hacer user.profile
    )

    # Nickname opcional (apodo visible en la app)
    nickname = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Apodo opcional para mostrar en la app.",
    )

    # Avatar opcional (imagen de perfil)
    avatar = models.ImageField(
        upload_to="avatars/",          # Se guardan en MEDIA_ROOT/avatars/
        blank=True,
        null=True,
    )

    # Breve descripción / bio del usuario (opcional)
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción corta del usuario.",
    )

    # Teléfono opcional
    telefono = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Teléfono de contacto (opcional).",
    )

    # Estado del perfil (activo / inactivo)
    is_active = models.BooleanField(
        default=True,
        help_text="Permite desactivar el perfil sin borrarlo.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # se setea al crear
    updated_at = models.DateTimeField(auto_now=True)      # se actualiza al guardar

    def __str__(self):
        """
        Representación legible del perfil:
        - Si hay nickname, mostramos el nickname.
        - Si no, mostramos el nombre completo o el username del User.
        """
        if self.nickname:
            return self.nickname

        full_name = self.user.get_full_name()
        if full_name:
            return full_name

        return self.user.username


# Create your models here.
