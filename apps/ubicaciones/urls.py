from django.urls import path
from .views import UbicacionListView, UbicacionDetailView

app_name = "ubicaciones"

urlpatterns = [
    path("", UbicacionListView.as_view(), name="lista"),
    path("<int:pk>/", UbicacionDetailView.as_view(), name="detalle"),
]
