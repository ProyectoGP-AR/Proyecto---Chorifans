from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from .models import Categoria
from apps.parrillas.models import Parrilla


class CategoriaListView(ListView):
    """
    Muestra un listado de todas las categorías activas.
    Ideal para páginas donde se muestran categorías para navegar el sitio.
    """
    model = Categoria
    template_name = "categorias/lista.html"       # Template de la lista
    context_object_name = "categorias"            # Nombre de la variable en el template

    def get_queryset(self):
        """
        Devuelve solo categorías activas, ordenadas alfabéticamente.
        """
        return (
            Categoria.objects
            .filter(is_active=True)
            .order_by("nombre")
        )


class CategoriaDetailView(DetailView):
    """
    Muestra la información de UNA categoría.
    Además, carga todas las parrillas asociadas a dicha categoría.
    """
    model = Categoria
    template_name = "categorias/detalle.html"
    context_object_name = "categoria"
    slug_field = "slug"                           # Campo que usa para buscar
    slug_url_kwarg = "slug"                       # Parametro capturado de la URL

    def get_object(self, queryset=None):
        """
        Sobreescribimos esto para asegurarnos de que la categoría esté activa.
        """
        return get_object_or_404(
            Categoria,
            slug=self.kwargs.get(self.slug_url_kwarg),
            is_active=True,
        )

    def get_context_data(self, **kwargs):
        """
        Agregamos al contexto todas las parrillas que pertenecen a esta categoría.
        """
        context = super().get_context_data(**kwargs)
        categoria = self.object

        parrillas = (
            Parrilla.objects
            .filter(categoria=categoria, is_active=True)
            .select_related("ubicacion")
            .order_by("nombre")
        )

        context["parrillas"] = parrillas           # Se envía al template
        return context
