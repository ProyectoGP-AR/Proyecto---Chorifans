# apps/resenas/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Resena, RespuestaResena
from .forms import ResenaForm, RespuestaResenaForm


class MisResenasView(LoginRequiredMixin, ListView):
    """
    Lista las reseñas del usuario común (mis reseñas).
    """

    model = Resena
    template_name = "resenas/mis_resenas.html"
    context_object_name = "resenas"
    login_url = "accounts:login"

    def get_queryset(self):
        return (
            Resena.objects
            .filter(usuario=self.request.user)
            .select_related("parrilla")
            .order_by("-created_at")
        )


class ValorarResenasListView(LoginRequiredMixin, ListView):
    """
    Lista las reseñas de la parrilla asociada al usuario dueño,
    para que pueda responderlas / editarlas.
    """

    model = Resena
    template_name = "resenas/valorar_resenas.html"
    context_object_name = "resenas"
    login_url = "accounts:login"

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "profile", None)

        # Si no es dueño activo, no tiene nada que valorar
        if not perfil or not getattr(perfil, "es_duenio_activo", False):
            return Resena.objects.none()

        parrilla = perfil.parrilla_asociada
        if not parrilla:
            return Resena.objects.none()

        return (
            Resena.objects
            .filter(parrilla=parrilla)
            .select_related("usuario", "parrilla")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = getattr(self.request.user, "profile", None)
        context["parrilla_duenio"] = getattr(perfil, "parrilla_asociada", None)
        return context


class ResponderResenaView(LoginRequiredMixin, View):
    """
    Crea o edita la respuesta de la parrilla a una reseña concreta.

    - Solo usuarios dueños de una parrilla pueden usarla.
    - Si la reseña ya tiene RespuestaResena → se edita.
    - Si no tiene → se crea una nueva.
    """

    template_name = "resenas/responder_resena.html"
    login_url = "accounts:login"

    def _validar_permisos(self, request, resena):
        """
        Verifica que el usuario logueado sea dueño activo de la
        parrilla asociada A ESA reseña.
        """
        user = request.user
        perfil = getattr(user, "profile", None)

        if not perfil or not getattr(perfil, "es_duenio_activo", False):
            return False

        if not perfil.parrilla_asociada:
            return False

        # Solo puede responder reseñas de su propia parrilla
        return perfil.parrilla_asociada == resena.parrilla

    def get(self, request, pk):
        resena = get_object_or_404(Resena, pk=pk)

        if not self._validar_permisos(request, resena):
            messages.error(
                request,
                "No tenés permisos para responder esta reseña."
            )
            return redirect("resenas:valorar_resenas")

        # Intentar obtener respuesta existente
        try:
            respuesta = resena.respuesta_parrilla
        except RespuestaResena.DoesNotExist:
            respuesta = None

        form = RespuestaResenaForm(instance=respuesta)

        context = {
            "resena": resena,
            "form": form,
            "respuesta": respuesta,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        resena = get_object_or_404(Resena, pk=pk)

        if not self._validar_permisos(request, resena):
            messages.error(
                request,
                "No tenés permisos para responder esta reseña."
            )
            return redirect("resenas:valorar_resenas")

        # ¿Ya hay respuesta?
        try:
            respuesta = resena.respuesta_parrilla
        except RespuestaResena.DoesNotExist:
            respuesta = None

        form = RespuestaResenaForm(request.POST, instance=respuesta)

        if form.is_valid():
            respuesta_obj = form.save(commit=False)
            respuesta_obj.resena = resena
            respuesta_obj.autor = request.user
            respuesta_obj.save()

            messages.success(request, "Respuesta guardada correctamente.")
            return redirect("resenas:valorar_resenas")

        # Si hay errores, volvemos a mostrar la página
        context = {
            "resena": resena,
            "form": form,
            "respuesta": respuesta,
        }
        return render(request, self.template_name, context)
