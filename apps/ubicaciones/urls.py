from django.urls import path
from . import views

app_name = "ubicaciones"

urlpatterns = [
    path("", views.ubicaciones_lista_view, name="lista"),
    path("<int:pk>/", views.ubicacion_detalle_view, name="detalle"),
]
