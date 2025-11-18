from datetime import date

from django.shortcuts import render

from .models import Promocion


def promociones_lista_view(request):
    """
    Muestra un listado de promociones vigentes de todas las parrillas.
    Solo se muestran:
      - is_active = True
      - fecha_inicio <= hoy
      - fecha_fin >= hoy
    """
    hoy = date.today()

    promociones = (
        Promocion.objects
        .filter(
            is_active=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        )
        .select_related("parrilla")
        .order_by("fecha_fin", "parrilla__nombre")
    )

    contexto = {
        "promociones": promociones,
    }
    return render(request, "promociones/lista.html", contexto)
