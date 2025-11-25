# apps/resenas/urls.py

from django.urls import path
from .views import MisResenasView, ValorarResenasListView, ResponderResenaView

app_name = "resenas"

urlpatterns = [
    # Panel del usuario común: ver sus propias reseñas
    path(
        "mis-resenas/",
        MisResenasView.as_view(),
        name="mis_resenas",
    ),

    # Panel del dueño de parrilla: ver reseñas de su parrilla
    path(
        "valorar/",
        ValorarResenasListView.as_view(),
        name="valorar_resenas",
    ),

    # Dueño responde / edita una reseña concreta (pk = id de la reseña)
    path(
        "valorar/<int:pk>/",
        ResponderResenaView.as_view(),
        name="responder_resena",
    ),
]
