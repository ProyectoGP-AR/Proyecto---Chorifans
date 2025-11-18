from django.db import models


class Promocion(models.Model):
    """
    Promociones y eventos especiales de una parrilla.
    Ej: 2x1 en choripán, menú del mediodía, etc.
    """

    # Parrilla a la que pertenece la promo
    parrilla = models.ForeignKey(
        "parrillas.Parrilla",
        on_delete=models.CASCADE,        # Si se borra la parrilla, se borran sus promos
        related_name="promociones",      # parrilla.promociones.all()
    )

    # Título corto de la promoción
    titulo = models.CharField(
        max_length=150,
        help_text="Título de la promo. Ej: '2x1 en choripán'.",
    )

    # Descripción más detallada de la promoción
    descripcion = models.TextField(
        help_text="Descripción completa de la promoción o evento.",
    )

    # Precio promocional opcional (por ejemplo, precio del menú)
    precio_promocional = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Precio promocional (opcional). Ej: 2500.00",
    )

    # Fechas de vigencia de la promoción
    fecha_inicio = models.DateField(
        help_text="Fecha desde la cual la promo está vigente.",
    )

    fecha_fin = models.DateField(
        help_text="Fecha hasta la cual la promo está vigente.",
    )

    # Marca si la promo está activa o no (además de las fechas)
    is_active = models.BooleanField(
        default=True,
        help_text="Permite desactivar la promo sin borrarla.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # se setea al crear
    updated_at = models.DateTimeField(auto_now=True)      # se actualiza al guardar

    def __str__(self):
        """
        Ejemplo:
        '2x1 en choripán - El Chori de Caballito'
        """
        return f"{self.titulo} - {self.parrilla.nombre}"
