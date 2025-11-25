from django.urls import path
from .views import CategoriaListView, CategoriaDetailView

app_name = "categorias"

urlpatterns = [
    path("", CategoriaListView.as_view(), name="lista"),
    path("<slug:slug>/", CategoriaDetailView.as_view(), name="detalle"),
]
