from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Perfil extendido del usuario.
    Guarda datos extra sin modificar el modelo User estándar.

    Además, puede marcarse como dueño oficial de una parrilla del sitio,
    para poder responder y valorar reseñas de ese local.
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

    # ==============================
    # CAMPOS PARA DUEÑO DE PARRILLA
    # ==============================

    es_duenio_parrilla = models.BooleanField(
        default=False,
        help_text=(
            "Indica si este usuario actúa como dueño oficial de una parrilla "
            "dentro del sitio."
        ),
    )

    parrilla_asociada = models.OneToOneField(
        "parrillas.Parrilla",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owner_profile",
        help_text=(
            "Parrilla de la cual este usuario es dueño. "
            "Solo se usa si es_duenio_parrilla es True."
        ),
    )

    # Estado del perfil (activo / inactivo)
    is_active = models.BooleanField(
        default=True,
        help_text="Permite desactivar el perfil sin borrarlo.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # se setea al crear
    updated_at = models.DateTimeField(auto_now=True)      # se actualiza al guardar

    # ==============================
    # HELPERS
    # ==============================

    @property
    def es_duenio_activo(self) -> bool:
        """
        Devuelve True solo si:
        - está marcado como dueño, y
        - tiene una parrilla asociada.

        Útil para chequear permisos en vistas / templates.
        """
        return self.es_duenio_parrilla and self.parrilla_asociada is not None

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
