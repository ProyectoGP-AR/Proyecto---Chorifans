from django.shortcuts import render, get_object_or_404

from .models import Categoria
from apps.parrillas.models import Parrilla


def categorias_lista_view(request):
    """
    Muestra un listado de todas las categorías activas.
    """
    categorias = Categoria.objects.filter(is_active=True).order_by("nombre")

    contexto = {
        "categorias": categorias,
    }
    return render(request, "categorias/lista.html", contexto)


def categoria_detalle_view(request, slug):
    """
    Muestra los datos de una categoría y las parrillas que pertenecen a esa categoría.
    Solo se muestran parrillas activas.
    """
    categoria = get_object_or_404(
        Categoria,
        slug=slug,
        is_active=True,
    )

    parrillas = (
        Parrilla.objects
        .filter(categoria=categoria, is_active=True)
        .select_related("ubicacion")
        .order_by("nombre")
    )

    contexto = {
        "categoria": categoria,
        "parrillas": parrillas,
    }
    return render(request, "categorias/detalle.html", contexto)
