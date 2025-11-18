from django.db import models


class Categoria(models.Model):
    """
    Tipos de parrilla: barrio, gourmet, feria, foodtruck, etc.
    """

    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre de la categoría. Ej: Gourmet, Barrio, Feria.",
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Identificador único corto para URLs y filtros. Ej: gourmet",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción opcional de la categoría.",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
