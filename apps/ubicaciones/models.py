from django.db import models


class Ubicacion(models.Model):
    """
    Representa una ubicación para las parrillas: ciudad, barrio,
    y opcionalmente coordenadas y un link directo a Google Maps.
    """

    nombre_ciudad = models.CharField(
        max_length=100,
        help_text="Ciudad donde se encuentra la parrilla. Ej: Buenos Aires.",
    )

    nombre_barrio = models.CharField(
        max_length=100,
        help_text="Barrio o zona. Ej: Caballito, Palermo, Centro.",
    )

    # Opcional: coordenadas geográficas
    latitud = models.FloatField(
        blank=True,
        null=True,
        help_text="Latitud opcional. Usada para mapas.",
    )

    longitud = models.FloatField(
        blank=True,
        null=True,
        help_text="Longitud opcional. Usada para mapas.",
    )

    # Link opcional directo a Google Maps
    google_maps_url = models.URLField(
        blank=True,
        null=True,
        help_text="Enlace pegado a mano de Google Maps (opcional).",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre_barrio} - {self.nombre_ciudad}"
