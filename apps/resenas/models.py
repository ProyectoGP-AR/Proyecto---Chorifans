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


class RespuestaResena(models.Model):
    """
    Respuesta oficial de la parrilla a una reseña.

    - Solo puede haber UNA respuesta por reseña (OneToOneField).
    - La respuesta la hace un usuario especial (dueño de la parrilla).
    - Incluye una valoración tipo carita feliz/triste sobre el comentario.
    """

    VALORACION_CHOICES = [
        ("happy", "😊"),
        ("sad", "☹️"),
    ]

    # Reseña a la que se responde (1 respuesta por reseña)
    resena = models.OneToOneField(
        Resena,
        on_delete=models.CASCADE,
        related_name="respuesta_parrilla",   # 👉 r.respuesta_parrilla en templates
        help_text="Reseña del usuario a la que responde la parrilla.",
    )

    # Usuario que responde (debería ser el dueño de la parrilla asociada)
    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="respuestas_resenas",
        help_text=(
            "Usuario dueño de la parrilla que responde a la reseña. "
            "A nivel de lógica, vamos a validar que coincida con la parrilla."
        ),
    )

    # Texto de la respuesta de la parrilla
    texto = models.TextField(
        help_text="Respuesta pública de la parrilla a la reseña.",
    )

    # Carita feliz / triste
    valoracion = models.CharField(
        max_length=10,
        choices=VALORACION_CHOICES,
        help_text="Valoración de la reseña (carita feliz o triste).",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # fecha de creación
    updated_at = models.DateTimeField(auto_now=True)      # última edición

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Respuesta a reseña"
        verbose_name_plural = "Respuestas a reseñas"

    def __str__(self):
        """
        Ejemplo:
        'Respuesta de usuarioX a reseña #15'
        (después en templates vamos a mostrar el nombre de la parrilla, no el username)
        """
        return f"Respuesta de {self.autor.username} a reseña #{self.resena.id}"
