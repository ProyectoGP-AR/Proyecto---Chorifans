from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from apps.parrillas.models import Parrilla
from .models import Ubicacion


class UbicacionListView(ListView):
    """
    Muestra un listado de todas las ubicaciones activas.
    Permite navegar parrillas por zona.
    """
    model = Ubicacion
    template_name = "ubicaciones/lista.html"
    context_object_name = "ubicaciones"

    def get_queryset(self):
        """
        Devuelve solo ubicaciones activas.
        Ahora ordenamos por zona y luego por barrio.
        """
        return (
            Ubicacion.objects
            .filter(is_active=True)
            .order_by("zona", "nombre_barrio")
        )

    def get_context_data(self, **kwargs):
        """
        Enviamos las zonas disponibles para usarlas en el filtro del template.
        """
        context = super().get_context_data(**kwargs)
        context["zonas_disponibles"] = [
            {"value": "CABA", "label": "CABA"},
            {"value": "GBA_NORTE", "label": "GBA Norte"},
            {"value": "GBA_OESTE", "label": "GBA Oeste"},
            {"value": "GBA_SUR", "label": "GBA Sur"},
        ]
        return context


class UbicacionDetailView(DetailView):
    """
    Muestra la información de UNA ubicación y las parrillas que están allí.
    """
    model = Ubicacion
    template_name = "ubicaciones/detalle.html"
    context_object_name = "ubicacion"
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        """
        Valida que la ubicación exista y esté activa.
        """
        return get_object_or_404(
            Ubicacion,
            pk=self.kwargs.get(self.pk_url_kwarg),
            is_active=True,
        )

    def get_context_data(self, **kwargs):
        """
        Agregamos todas las parrillas asociadas a esa ubicación.
        """
        context = super().get_context_data(**kwargs)
        ubicacion = self.object

        parrillas = (
            Parrilla.objects
            .filter(ubicacion=ubicacion, is_active=True)
            .select_related("categoria")
            .order_by("nombre")
        )

        context["parrillas"] = parrillas
        return context