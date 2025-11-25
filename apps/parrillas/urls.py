from django.urls import path
from .views import ParrillaListView, ParrillaDetailView, ParrillaBuscarView

app_name = "parrillas"

urlpatterns = [
    # Lista de parrillas
    path("", ParrillaListView.as_view(), name="lista"),

    # Buscador de parrillas (FormView)
    path("buscar/", ParrillaBuscarView.as_view(), name="buscar"),

    # Detalle de una parrilla
    path("<int:pk>/", ParrillaDetailView.as_view(), name="detalle"),
]
