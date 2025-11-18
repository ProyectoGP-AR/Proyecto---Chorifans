from django.shortcuts import render, get_object_or_404

from .models import Ubicacion
from apps.parrillas.models import Parrilla


def ubicaciones_lista_view(request):
    """
    Muestra un listado de todas las ubicaciones activas.
    """
    ubicaciones = Ubicacion.objects.filter(is_active=True).order_by(
        "nombre_ciudad",
        "nombre_barrio",
    )

    contexto = {
        "ubicaciones": ubicaciones,
    }
    return render(request, "ubicaciones/lista.html", contexto)


def ubicacion_detalle_view(request, pk):
    """
    Muestra los datos de una ubicación y las parrillas que se encuentran ahí.
    Solo se muestran parrillas activas.
    """
    ubicacion = get_object_or_404(
        Ubicacion,
        pk=pk,
        is_active=True,
    )

    parrillas = (
        Parrilla.objects
        .filter(ubicacion=ubicacion, is_active=True)
        .select_related("categoria")
        .order_by("nombre")
    )

    contexto = {
        "ubicacion": ubicacion,
        "parrillas": parrillas,
    }
    return render(request, "ubicaciones/detalle.html", contexto)
