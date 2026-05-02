from django.db import models


class Ubicacion(models.Model):
    """
    Representa una ubicación para las parrillas: ciudad, barrio,
    zona AMBA y opcionalmente coordenadas y un link directo a Google Maps.
    """

    ZONA_CHOICES = [
        ("CABA", "CABA"),
        ("GBA_NORTE", "GBA Norte"),
        ("GBA_OESTE", "GBA Oeste"),
        ("GBA_SUR", "GBA Sur"),
    ]

    nombre_ciudad = models.CharField(
        max_length=100,
        help_text="Ciudad donde se encuentra la parrilla. Ej: Buenos Aires.",
    )

    nombre_barrio = models.CharField(
        max_length=100,
        help_text="Barrio o zona. Ej: Caballito, Palermo, Avellaneda.",
    )

    zona = models.CharField(
        max_length=20,
        choices=ZONA_CHOICES,
        blank=True,
        null=True,
        help_text="Zona general para filtros del sitio. Ej: CABA, GBA Norte, GBA Oeste, GBA Sur.",
    )

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

    google_maps_url = models.URLField(
        blank=True,
        null=True,
        help_text="Enlace pegado a mano de Google Maps (opcional).",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def zona_label(self):
        return dict(self.ZONA_CHOICES).get(self.zona, "")

    def __str__(self):
        if self.zona:
            return f"{self.nombre_barrio} - {self.zona_label}"
        return f"{self.nombre_barrio} - {self.nombre_ciudad}"