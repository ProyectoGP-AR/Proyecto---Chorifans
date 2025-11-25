from datetime import date

from django.views.generic import ListView

from .models import Promocion


class PromocionListView(ListView):
    """
    Muestra un listado de promociones vigentes.
    Filtra según fecha de inicio y fecha de fin para mostrar solo las activas.
    """
    model = Promocion
    template_name = "promociones/lista.html"
    context_object_name = "promociones"

    def get_queryset(self):
        """
        Devuelve solo promociones activas y vigentes según la fecha actual.
        """
        hoy = date.today()
        return (
            Promocion.objects
            .filter(
                is_active=True,
                fecha_inicio__lte=hoy,    # La promo ya empezó
                fecha_fin__gte=hoy,       # Todavía no terminó
            )
            .select_related("parrilla")
            .order_by("fecha_fin", "parrilla__nombre")
        )
