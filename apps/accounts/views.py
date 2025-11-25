from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic import View
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect


class UserLoginView(LoginView):
    """
    Vista basada en clases para INICIAR SESIÓN.
    """
    template_name = "accounts/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("home")


class UserRegisterView(FormView):
    """
    Vista basada en clases para REGISTRARSE.
    """
    template_name = "accounts/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class UserLogoutView(View):
    """
    Vista basada en clases para CERRAR SESIÓN.
    Acepta GET (el enlace del header) y luego redirige al home.
    """

    def get(self, request, *args, **kwargs):
        logout(request)               # Cierra la sesión del usuario
        return redirect("home")       # Lo manda a la página de inicio
