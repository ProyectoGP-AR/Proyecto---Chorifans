from django.db import models


class Parrilla(models.Model):
    """
    Modelo principal del sistema.
    Representa una parrilla (local) con sus datos básicos
    y relaciones a categoría y ubicación.
    """

    # Nombre visible de la parrilla
    nombre = models.CharField(
        max_length=150,
        help_text="Nombre de la parrilla. Ej: 'El Chori de Caballito'.",
    )

    # Descripción breve (opcional)
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción de la parrilla, tipo de comida, estilo, etc.",
    )

    # Dirección física
    direccion = models.CharField(
        max_length=200,
        help_text="Dirección completa. Ej: 'Av. Rivadavia 1234'.",
    )

    # Teléfono opcional
    telefono = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Teléfono de la parrilla (opcional).",
    )

    # Sitio web o redes sociales (opcional)
    sitio_web = models.URLField(
        blank=True,
        null=True,
        help_text="Sitio web o enlace a redes sociales (opcional).",
    )

    # Relación con Ubicacion (ciudad + barrio)
    # Usamos el nombre de la app y del modelo como string para evitar imports circulares
    ubicacion = models.ForeignKey(
        "ubicaciones.Ubicacion",
        on_delete=models.PROTECT,   # No permitir borrar ubicación si tiene parrillas
        related_name="parrillas",   # Permite hacer ubicacion.parrillas.all()
    )

    # Relación con Categoria (barrio, gourmet, feria, etc.)
    categoria = models.ForeignKey(
        "categorias.Categoria",
        on_delete=models.PROTECT,   # No permitir borrar categoría si tiene parrillas
        related_name="parrillas",   # categoria.parrillas.all()
    )

    # Foto principal opcional de la parrilla
    foto_principal = models.ImageField(
        upload_to="parrillas/",     # Se guarda en MEDIA_ROOT/parrillas/
        blank=True,
        null=True,
    )

    # Puntaje promedio (lo podemos calcular más adelante a partir de las reseñas)
    promedio_puntaje = models.FloatField(
        blank=True,
        null=True,
        help_text="Puntaje promedio basado en reseñas (1 a 5 choripanes).",
    )

    # Estado de la parrilla (activa o dada de baja)
    is_active = models.BooleanField(
        default=True,
        help_text="Permite desactivar la parrilla sin borrarla.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # se setea al crear
    updated_at = models.DateTimeField(auto_now=True)      # se actualiza al guardar

    def __str__(self):
        """
        Representación legible: mostramos el nombre y el barrio/ciudad.
        """
        ubicacion_str = (
            f" - {self.ubicacion.nombre_barrio}, {self.ubicacion.nombre_ciudad}"
            if self.ubicacion
            else ""
        )
        return f"{self.nombre}{ubicacion_str}"
