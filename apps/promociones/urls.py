from django.urls import path
from .views import PromocionListView

app_name = "promociones"

urlpatterns = [
    path("", PromocionListView.as_view(), name="lista"),
]
