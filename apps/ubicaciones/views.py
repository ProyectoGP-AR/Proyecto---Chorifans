from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from .models import Ubicacion
from apps.parrillas.models import Parrilla


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
        Ordenamos por ciudad y luego barrio.
        """
        return (
            Ubicacion.objects
            .filter(is_active=True)
            .order_by("nombre_ciudad", "nombre_barrio")
        )


class UbicacionDetailView(DetailView):
    """
    Muestra la información de UNA ubicación y las parrillas que están allí.
    """
    model = Ubicacion
    template_name = "ubicaciones/detalle.html"
    context_object_name = "ubicacion"
    pk_url_kwarg = "pk"                           # Recibe el ID numérico

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

        context["parrillas"] = parrillas           # Se envía al template
        return context
