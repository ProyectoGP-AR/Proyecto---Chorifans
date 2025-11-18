from django.urls import path
from . import views

app_name = "categorias"

urlpatterns = [
    path("", views.categorias_lista_view, name="lista"),
    path("<slug:slug>/", views.categoria_detalle_view, name="detalle"),
]
