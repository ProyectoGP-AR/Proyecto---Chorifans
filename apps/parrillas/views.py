from datetime import date

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg

from apps.resenas.models import Resena
from apps.resenas.forms import ResenaForm
from apps.promociones.models import Promocion
from .models import Parrilla


def parrillas_lista_view(request):
    """
    Muestra un listado de todas las parrillas activas.
    """
    parrillas = (
        Parrilla.objects
        .filter(is_active=True)
        .select_related("ubicacion", "categoria")
        .order_by("nombre")
    )

    contexto = {
        "parrillas": parrillas,
    }
    return render(request, "parrillas/lista.html", contexto)


def parrilla_detalle_view(request, pk):
    """
    Muestra el detalle de una parrilla específica,
    sus reseñas, sus promociones y el formulario para reseñar.
    """

    parrilla = get_object_or_404(
        Parrilla.objects.select_related("ubicacion", "categoria"),
        pk=pk,
        is_active=True,
    )

    # === Reseñas activas ===
    resenas = (
        Resena.objects
        .filter(parrilla=parrilla, is_active=True)
        .select_related("usuario")
    )

    # === Promociones vigentes ===
    hoy = date.today()
    promociones = (
        Promocion.objects
        .filter(
            parrilla=parrilla,
            is_active=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        )
        .order_by("fecha_fin")
    )

    # === Formulario reseña ===
    puede_reseñar = False
    ya_reseño = False
    form = None

    if request.user.is_authenticated:

        # ¿Ya reseñó?
        ya_reseño = Resena.objects.filter(
            usuario=request.user,
            parrilla=parrilla
        ).exists()

        if not ya_reseño:
            puede_reseñar = True

            if request.method == "POST":
                form = ResenaForm(request.POST)
                if form.is_valid():
                    nueva = form.save(commit=False)
                    nueva.usuario = request.user
                    nueva.parrilla = parrilla
                    nueva.save()

                    # Actualizar promedio
                    avg = Resena.objects.filter(
                        parrilla=parrilla,
                        is_active=True
                    ).aggregate(Avg("puntaje"))["puntaje__avg"]

                    parrilla.promedio_puntaje = avg
                    parrilla.save()

                    messages.success(request, "¡Gracias por tu reseña!")
                    return redirect("parrillas:detalle", pk=parrilla.id)
            else:
                form = ResenaForm()

    contexto = {
        "parrilla": parrilla,
        "resenas": resenas,
        "promociones": promociones,
        "form": form,
        "puede_reseñar": puede_reseñar,
        "ya_reseño": ya_reseño,
    }

    return render(request, "parrillas/detalle.html", contexto)

