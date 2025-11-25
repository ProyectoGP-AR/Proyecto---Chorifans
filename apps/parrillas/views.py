# apps/parrillas/views.py

from datetime import date

# Atajos de Django para redirecciones
from django.shortcuts import redirect

# Vistas basadas en clases
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin, FormView

# Utilidades de Django
from django.urls import reverse
from django.db.models import Avg, Q     # Q para búsquedas complejas (OR / AND)
from django.contrib import messages

# Modelos del proyecto
from apps.resenas.models import Resena               # Modelo de reseñas de usuarios
from apps.resenas.forms import ResenaForm           # Formulario para crear reseñas
from apps.promociones.models import Promocion       # Modelo de promociones
from .models import Parrilla                        # Modelo principal de la app parrillas
from .forms import BuscarParrillaForm               # Formulario de búsqueda de parrillas


# ============================================================
#   LISTA DE PARRILLAS
# ============================================================

class ParrillaListView(ListView):
    """
    Vista basada en clases para listar parrillas.

    - Hereda de ListView.
    - Muestra todas las parrillas activas.
    - Usa select_related para optimizar consultas de FK (ubicación y categoría).
    """

    model = Parrilla
    template_name = "parrillas/lista.html"
    context_object_name = "parrillas"
    paginate_by = 3   # Muestra solo 3 cards por página

    def get_queryset(self):
        """
        Devuelve todas las parrillas activas ordenadas por nombre.
        """
        return (
            Parrilla.objects
            .filter(is_active=True)
            .select_related("ubicacion", "categoria")
            .order_by("nombre")
        )


# ============================================================
#   DETALLE DE PARRILLA + FORMULARIO DE RESEÑA
# ============================================================

class ParrillaDetailView(FormMixin, DetailView):
    """
    Vista que combina:
    - DetailView → muestra la información de una parrilla puntual.
    - FormMixin  → agrega el formulario para dejar una reseña.

    GET  → muestra detalle + lista de reseñas + promociones + formulario.
    POST → procesa el envío del formulario de reseña.
    """

    model = Parrilla
    template_name = "parrillas/detalle.html"
    context_object_name = "parrilla"
    form_class = ResenaForm  # Formulario que se incluye en la página

    def get_success_url(self):
        """
        URL a la que redirigimos luego de procesar correctamente la reseña.

        En este caso, volvemos al mismo detalle de la parrilla.
        """
        return reverse("parrillas:detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        """
        Agrega datos extra al contexto del template:

        - Reseñas asociadas a la parrilla.
        - Promociones vigentes (según la fecha actual).
        - Flags para indicar:
          · si el usuario ya dejó reseña en esta parrilla.
          · si el usuario puede dejar reseña.
          · si el usuario es dueño de una parrilla (para bloquear reseñas).
        """
        context = super().get_context_data(**kwargs)
        parrilla = self.object
        hoy = date.today()

        # ==========================
        # Reseñas de la parrilla
        # ==========================
        context["resenas"] = (
            Resena.objects
            .filter(parrilla=parrilla)
            .select_related("usuario")
            .order_by("-created_at")      # Más nuevas primero
        )

        # ==========================
        # Promociones vigentes hoy
        # ==========================
        context["promociones"] = (
            Promocion.objects.filter(
                parrilla=parrilla,
                is_active=True,
                fecha_inicio__lte=hoy,
                fecha_fin__gte=hoy,
            ).order_by("fecha_fin")
        )

        # ==========================
        # Lógica de permisos de reseñas
        # ==========================
        user = self.request.user
        es_duenio_parrilla = False

        # Verificamos si el usuario tiene perfil y si es marcado como dueño de parrilla
        if user.is_authenticated:
            profile = getattr(user, "profile", None)
            if profile:
                # Si existe una property es_duenio_activo, la usamos (mejor encapsulado)
                if hasattr(profile, "es_duenio_activo"):
                    es_duenio_parrilla = profile.es_duenio_activo
                else:
                    # Fallback: leemos el booleano directamente
                    es_duenio_parrilla = bool(
                        getattr(profile, "es_duenio_parrilla", False)
                    )

        # ¿Ya dejó reseña el usuario en ESTA parrilla?
        ya_reseño = (
            user.is_authenticated
            and Resena.objects.filter(parrilla=parrilla, usuario=user).exists()
        )

        # Puede reseñar solo si:
        # - está logueado
        # - NO es dueño de parrilla
        # - NO dejó reseña antes en esta parrilla
        puede_reseñar = (
            user.is_authenticated
            and not ya_reseño
            and not es_duenio_parrilla
        )

        # Enviamos estos flags al template
        context["es_duenio_parrilla"] = es_duenio_parrilla
        context["ya_reseño"] = ya_reseño
        context["puede_reseñar"] = puede_reseñar

        # Agregamos el formulario al contexto si aún no está presente
        if "form" not in context:
            context["form"] = self.get_form()

        return context

    def post(self, request, *args, **kwargs):
        """
        Procesa el formulario enviado (POST) para crear una reseña.

        Reglas de negocio:
        - El usuario debe estar autenticado.
        - Los usuarios dueños de una parrilla NO pueden dejar reseñas.
        - No se permiten reseñas duplicadas (1 por usuario y parrilla).
        - Si todo es válido, se guarda la reseña y se recalcula el promedio.
        """

        # Obtenemos la instancia de parrilla del detalle
        self.object = self.get_object()

        # 1️⃣ Si el usuario NO está logueado → lo enviamos a la página de login
        if not request.user.is_authenticated:
            messages.error(request, "Debés iniciar sesión para dejar una reseña.")
            return redirect("accounts:login")

        # 2️⃣ Bloquear a usuarios que son dueños de parrilla
        profile = getattr(request.user, "profile", None)
        if profile:
            if hasattr(profile, "es_duenio_activo"):
                es_duenio_parrilla = profile.es_duenio_activo
            else:
                es_duenio_parrilla = bool(
                    getattr(profile, "es_duenio_parrilla", False)
                )

            if es_duenio_parrilla:
                messages.error(
                    request,
                    "Los usuarios dueños de una parrilla no pueden dejar reseñas."
                )
                return redirect(self.get_success_url())

        # 3️⃣ Obtenemos el formulario con los datos de la request
        form = self.get_form()

        if form.is_valid():
            # 4️⃣ Evitar reseñas duplicadas para la misma parrilla y usuario
            if Resena.objects.filter(parrilla=self.object, usuario=request.user).exists():
                messages.warning(request, "Ya dejaste una reseña para esta parrilla.")
                return redirect(self.get_success_url())

            # 5️⃣ Crear la reseña en memoria (sin guardar todavía)
            resena = form.save(commit=False)
            resena.parrilla = self.object
            resena.usuario = request.user
            resena.save()  # Ahora sí, guardamos en la base

            # 6️⃣ Recalcular el puntaje promedio de la parrilla
            promedio = (
                Resena.objects.filter(parrilla=self.object)
                .aggregate(Avg("puntaje"))["puntaje__avg"] or 0
            )
            self.object.promedio_puntaje = promedio
            self.object.save(update_fields=["promedio_puntaje"])

            messages.success(request, "¡Gracias por tu reseña!")
            return redirect(self.get_success_url())

        # Si el formulario es inválido → se renderiza el template con errores
        return self.form_invalid(form)


# ============================================================
#   BUSCADOR DE PARRILLAS
# ============================================================

class ParrillaBuscarView(FormView):
    """
    Vista de búsqueda de parrillas.

    - Muestra un formulario simple (no basado en un modelo).
    - En POST valida el término y devuelve resultados en el mismo template.

    El término de búsqueda se aplica sobre:
    - nombre de la parrilla
    - barrio
    - ciudad
    - nombre de la categoría
    """

    template_name = "parrillas/buscar.html"
    form_class = BuscarParrillaForm

    def form_valid(self, form):
        """
        Si el formulario es válido:

        - Tomamos el término ingresado.
        - Buscamos parrillas activas cuyo:
          · nombre contenga el término, o
          · barrio contenga el término, o
          · ciudad contenga el término, o
          · categoría contenga el término.
        - Renderizamos la misma pantalla con los resultados.
        """
        termino = form.cleaned_data["termino"]

        resultados = (
            Parrilla.objects
            .filter(
                Q(nombre__icontains=termino) |
                Q(ubicacion__nombre_barrio__icontains=termino) |
                Q(ubicacion__nombre_ciudad__icontains=termino) |
                Q(categoria__nombre__icontains=termino),
                is_active=True,
            )
            .select_related("ubicacion", "categoria")
            .order_by("nombre")
        )

        return self.render_to_response(
            self.get_context_data(form=form, resultados=resultados)
        )

    def form_invalid(self, form):
        """
        Si el formulario no es válido:
        - Volvemos a mostrar el template con el formulario
          y sin resultados (None).
        """
        return self.render_to_response(
            self.get_context_data(form=form, resultados=None)
        )
