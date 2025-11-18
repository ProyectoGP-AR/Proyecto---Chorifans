
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Vista para INICIAR SESIÓN.

    - Si el método es POST: valida el formulario e intenta autenticar al usuario.
    - Si el método es GET: muestra el formulario de login.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            # Si el formulario es válido, obtenemos el usuario
            user = form.get_user()
            # Iniciamos sesión
            login(request, user)
            # Después de loguearse, lo mandamos al home
            return redirect("home")  # 'home' es el nombre de nuestra vista principal
    else:
        # Si es GET, mostramos el formulario vacío
        form = AuthenticationForm(request)

    contexto = {
        "form": form,
        "titulo_pagina": "Iniciar sesión - ChoriFans",
    }
    return render(request, "accounts/login.html", contexto)


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Vista para CERRAR SESIÓN.

    - Cierra la sesión actual (si hay usuario logueado).
    - Redirige al home.
    """
    logout(request)
    return redirect("home")


def register_view(request: HttpRequest) -> HttpResponse:
    """
    Vista para REGISTRAR un nuevo usuario.

    - Si el método es POST: valida y crea un nuevo usuario.
    - Si el método es GET: muestra el formulario de registro.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # Creamos el usuario
            user = form.save()
            # Lo logueamos automáticamente después de registrarse
            login(request, user)
            # Redirigimos al home
            return redirect("home")
    else:
        # Si es GET, mostramos el formulario vacío
        form = UserCreationForm()

    contexto = {
        "form": form,
        "titulo_pagina": "Registrarse - ChoriFans",
    }
    return render(request, "accounts/register.html", contexto)

def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Vista para CERRAR sesión.

    - Cierra la sesión del usuario actual.
    - Redirige al home.
    """
    logout(request)
    return redirect("home")
