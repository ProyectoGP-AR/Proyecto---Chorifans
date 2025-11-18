from django.db import models
from django.contrib.auth.models import User


class Resena(models.Model):
    """
    Reseña de un usuario sobre una parrilla.
    Puntaje de 1 a 5 choripanes + comentario.
    Solo se permite UNA reseña por usuario y parrilla.
    """

    # Opciones de puntaje con choripanes (1 = peor, 5 = mejor)
    PUNTAJE_CHOICES = [
        (1, "🌭 1 choripán (muy mala experiencia)"),
        (2, "🌭🌭 2 choripanes (floja)"),
        (3, "🌭🌭🌭 3 choripanes (zafa)"),
        (4, "🌭🌭🌭🌭 4 choripanes (muy buena)"),
        (5, "🌭🌭🌭🌭🌭 5 choripanes (excelente)"),
    ]

    # Usuario que deja la reseña
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,         # Si se borra el usuario, se borran sus reseñas
        related_name="resenas",           # user.resenas.all()
    )

    # Parrilla reseñada
    parrilla = models.ForeignKey(
        "parrillas.Parrilla",
        on_delete=models.CASCADE,         # Si se borra la parrilla, se borran sus reseñas
        related_name="resenas",           # parrilla.resenas.all()
    )

    # Puntaje de 1 a 5 choripanes
    puntaje = models.IntegerField(
        choices=PUNTAJE_CHOICES,
        help_text="Elegí de 1 a 5 choripanes (1 = peor, 5 = mejor).",
    )

    # Comentario de la reseña
    comentario = models.TextField(
        help_text="Comentario del usuario sobre la parrilla.",
    )

    # Estado de la reseña (para moderar sin borrar)
    is_active = models.BooleanField(
        default=True,
        help_text="Permite ocultar la reseña sin borrarla.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # fecha de creación
    updated_at = models.DateTimeField(auto_now=True)      # fecha de última edición

    class Meta:
        # Restringe a UNA reseña por usuario y parrilla
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "parrilla"],
                name="unique_resena_usuario_parrilla",
            )
        ]
        ordering = ["-created_at"]  # reseñas más nuevas primero

    def __str__(self):
        """
        Ejemplo de salida:
        'diex - El Chori de Caballito (4/5)'
        """
        return f"{self.usuario.username} - {self.parrilla.nombre} ({self.puntaje}/5)"
