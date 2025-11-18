from django.urls import path
from . import views

app_name = "parrillas"

urlpatterns = [
    path("<int:pk>/", views.parrilla_detalle_view, name="detalle"),
    path("", views.parrillas_lista_view, name="lista"), 
]
