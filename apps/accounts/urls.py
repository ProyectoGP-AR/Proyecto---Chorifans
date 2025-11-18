"""
URLs del app 'accounts'.

Acá definimos las rutas para:
- /accounts/login/      -> login_view
- /accounts/logout/     -> logout_view
- /accounts/register/   -> register_view
"""

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
]
