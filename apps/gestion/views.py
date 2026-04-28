from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

from apps.parrillas.models import Parrilla
from apps.parrillas.forms import ParrillaGestionForm

from apps.promociones.models import Promocion
from apps.promociones.forms import PromocionGestionForm

from apps.categorias.models import Categoria
from apps.categorias.forms import CategoriaGestionForm

from apps.ubicaciones.models import Ubicacion
from apps.ubicaciones.forms import UbicacionGestionForm

from apps.resenas.models import Resena
from apps.resenas.forms import ResenaGestionForm

from django.contrib.auth.models import User
from apps.accounts.forms import UsuarioGestionForm

from django.db.models import Q
from django.utils import timezone
from apps.accounts.models import Profile

class GestionRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "accounts:login"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class GestionDashboardView(GestionRequiredMixin, TemplateView):
    template_name = "gestion/dashboard.html"


class GestionParrillaListView(GestionRequiredMixin, ListView):
    model = Parrilla
    template_name = "gestion/parrillas/lista.html"
    context_object_name = "parrillas"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            Parrilla.objects
            .select_related("categoria", "ubicacion")
            .order_by("-created_at")
        )

        busqueda = self.request.GET.get("q", "").strip()
        estado = self.request.GET.get("estado", "").strip()
        categoria = self.request.GET.get("categoria", "").strip()
        ubicacion = self.request.GET.get("ubicacion", "").strip()

        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda)
                | Q(descripcion__icontains=busqueda)
                | Q(direccion__icontains=busqueda)
            )

        if estado == "activas":
            queryset = queryset.filter(is_active=True)
        elif estado == "inactivas":
            queryset = queryset.filter(is_active=False)

        if categoria:
            queryset = queryset.filter(categoria_id=categoria)

        if ubicacion:
            queryset = queryset.filter(ubicacion_id=ubicacion)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["estado"] = self.request.GET.get("estado", "").strip()
        context["categoria_actual"] = self.request.GET.get("categoria", "").strip()
        context["ubicacion_actual"] = self.request.GET.get("ubicacion", "").strip()
        context["categorias"] = Categoria.objects.filter(is_active=True).order_by("nombre")
        context["ubicaciones"] = Ubicacion.objects.filter(is_active=True).order_by("nombre_ciudad", "nombre_barrio")
        return context


class GestionParrillaCreateView(GestionRequiredMixin, CreateView):
    model = Parrilla
    form_class = ParrillaGestionForm
    template_name = "gestion/parrillas/form.html"
    success_url = reverse_lazy("gestion:parrillas_lista")


class GestionParrillaUpdateView(GestionRequiredMixin, UpdateView):
    model = Parrilla
    form_class = ParrillaGestionForm
    template_name = "gestion/parrillas/form.html"
    success_url = reverse_lazy("gestion:parrillas_lista")


class GestionParrillaDeleteView(GestionRequiredMixin, DeleteView):
    model = Parrilla
    template_name = "gestion/parrillas/confirm_delete.html"
    success_url = reverse_lazy("gestion:parrillas_lista")
    

class GestionPromocionListView(GestionRequiredMixin, ListView):
    model = Promocion
    template_name = "gestion/promociones/lista.html"
    context_object_name = "promociones"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            Promocion.objects
            .select_related("parrilla")
            .order_by("-created_at")
        )

        busqueda = self.request.GET.get("q", "").strip()
        estado = self.request.GET.get("estado", "").strip()
        vigencia = self.request.GET.get("vigencia", "").strip()
        parrilla = self.request.GET.get("parrilla", "").strip()

        hoy = timezone.now().date()

        if busqueda:
            queryset = queryset.filter(
                Q(titulo__icontains=busqueda)
                | Q(descripcion__icontains=busqueda)
                | Q(parrilla__nombre__icontains=busqueda)
            )

        if estado == "activas":
            queryset = queryset.filter(is_active=True)
        elif estado == "inactivas":
            queryset = queryset.filter(is_active=False)

        if vigencia == "vigentes":
            queryset = queryset.filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy)
        elif vigencia == "vencidas":
            queryset = queryset.filter(fecha_fin__lt=hoy)
        elif vigencia == "futuras":
            queryset = queryset.filter(fecha_inicio__gt=hoy)

        if parrilla:
            queryset = queryset.filter(parrilla_id=parrilla)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["estado"] = self.request.GET.get("estado", "").strip()
        context["vigencia"] = self.request.GET.get("vigencia", "").strip()
        context["parrilla_actual"] = self.request.GET.get("parrilla", "").strip()
        context["parrillas_filtro"] = Parrilla.objects.filter(is_active=True).order_by("nombre")
        return context


class GestionPromocionCreateView(GestionRequiredMixin, CreateView):
    model = Promocion
    form_class = PromocionGestionForm
    template_name = "gestion/promociones/form.html"
    success_url = reverse_lazy("gestion:promociones_lista")


class GestionPromocionUpdateView(GestionRequiredMixin, UpdateView):
    model = Promocion
    form_class = PromocionGestionForm
    template_name = "gestion/promociones/form.html"
    success_url = reverse_lazy("gestion:promociones_lista")


class GestionPromocionDeleteView(GestionRequiredMixin, DeleteView):
    model = Promocion
    template_name = "gestion/promociones/confirm_delete.html"
    success_url = reverse_lazy("gestion:promociones_lista")


class GestionCategoriaListView(GestionRequiredMixin, ListView):
    model = Categoria
    template_name = "gestion/categorias/lista.html"
    context_object_name = "categorias"
    ordering = ["nombre"]


class GestionCategoriaCreateView(GestionRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaGestionForm
    template_name = "gestion/categorias/form.html"
    success_url = reverse_lazy("gestion:categorias_lista")


class GestionCategoriaUpdateView(GestionRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaGestionForm
    template_name = "gestion/categorias/form.html"
    success_url = reverse_lazy("gestion:categorias_lista")


class GestionCategoriaDeleteView(GestionRequiredMixin, DeleteView):
    model = Categoria
    template_name = "gestion/categorias/confirm_delete.html"
    success_url = reverse_lazy("gestion:categorias_lista")
    
    
class GestionUbicacionListView(GestionRequiredMixin, ListView):
    model = Ubicacion
    template_name = "gestion/ubicaciones/lista.html"
    context_object_name = "ubicaciones"
    ordering = ["nombre_ciudad", "nombre_barrio"]


class GestionUbicacionCreateView(GestionRequiredMixin, CreateView):
    model = Ubicacion
    form_class = UbicacionGestionForm
    template_name = "gestion/ubicaciones/form.html"
    success_url = reverse_lazy("gestion:ubicaciones_lista")


class GestionUbicacionUpdateView(GestionRequiredMixin, UpdateView):
    model = Ubicacion
    form_class = UbicacionGestionForm
    template_name = "gestion/ubicaciones/form.html"
    success_url = reverse_lazy("gestion:ubicaciones_lista")


class GestionUbicacionDeleteView(GestionRequiredMixin, DeleteView):
    model = Ubicacion
    template_name = "gestion/ubicaciones/confirm_delete.html"
    success_url = reverse_lazy("gestion:ubicaciones_lista")
    
class GestionResenaListView(GestionRequiredMixin, ListView):
    model = Resena
    template_name = "gestion/resenas/lista.html"
    context_object_name = "resenas"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            Resena.objects
            .select_related("usuario", "parrilla")
            .order_by("-created_at")
        )

        busqueda = self.request.GET.get("q", "").strip()
        parrilla = self.request.GET.get("parrilla", "").strip()
        puntaje = self.request.GET.get("puntaje", "").strip()

        if busqueda:
            queryset = queryset.filter(
                Q(usuario__username__icontains=busqueda)
                | Q(comentario__icontains=busqueda)
                | Q(parrilla__nombre__icontains=busqueda)
            )

        if parrilla:
            queryset = queryset.filter(parrilla_id=parrilla)

        if puntaje:
            queryset = queryset.filter(puntaje=puntaje)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["parrilla_actual"] = self.request.GET.get("parrilla", "").strip()
        context["puntaje_actual"] = self.request.GET.get("puntaje", "").strip()
        context["parrillas_filtro"] = Parrilla.objects.filter(is_active=True).order_by("nombre")
        return context


class GestionResenaCreateView(GestionRequiredMixin, CreateView):
    model = Resena
    form_class = ResenaGestionForm
    template_name = "gestion/resenas/form.html"
    success_url = reverse_lazy("gestion:resenas_lista")


class GestionResenaUpdateView(GestionRequiredMixin, UpdateView):
    model = Resena
    form_class = ResenaGestionForm
    template_name = "gestion/resenas/form.html"
    success_url = reverse_lazy("gestion:resenas_lista")


class GestionResenaDeleteView(GestionRequiredMixin, DeleteView):
    model = Resena
    template_name = "gestion/resenas/confirm_delete.html"
    success_url = reverse_lazy("gestion:resenas_lista")
    
    
class GestionUsuarioListView(GestionRequiredMixin, ListView):
    model = User
    template_name = "gestion/usuarios/lista.html"
    context_object_name = "usuarios"
    ordering = ["username"]

    def get_queryset(self):
        queryset = (
            User.objects
            .select_related("profile")
            .order_by("username")
        )

        busqueda = self.request.GET.get("q", "").strip()
        estado = self.request.GET.get("estado", "").strip()
        rol = self.request.GET.get("rol", "").strip()

        if busqueda:
            queryset = queryset.filter(
                Q(username__icontains=busqueda)
                | Q(first_name__icontains=busqueda)
                | Q(last_name__icontains=busqueda)
                | Q(email__icontains=busqueda)
                | Q(profile__nickname__icontains=busqueda)
            )

        if estado == "activos":
            queryset = queryset.filter(is_active=True)
        elif estado == "inactivos":
            queryset = queryset.filter(is_active=False)

        if rol == "admin":
            queryset = queryset.filter(is_staff=True)
        elif rol == "duenio":
            queryset = queryset.filter(
                profile__es_duenio_parrilla=True,
                profile__parrilla_asociada__isnull=False,
            )
        elif rol == "comun":
            queryset = queryset.filter(is_staff=False).exclude(
                profile__es_duenio_parrilla=True,
                profile__parrilla_asociada__isnull=False,
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["estado"] = self.request.GET.get("estado", "").strip()
        context["rol"] = self.request.GET.get("rol", "").strip()
        return context


class GestionUsuarioCreateView(GestionRequiredMixin, CreateView):
    model = User
    form_class = UsuarioGestionForm
    template_name = "gestion/usuarios/form.html"
    success_url = reverse_lazy("gestion:usuarios_lista")


class GestionUsuarioUpdateView(GestionRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioGestionForm
    template_name = "gestion/usuarios/form.html"
    success_url = reverse_lazy("gestion:usuarios_lista")


class GestionUsuarioDeleteView(GestionRequiredMixin, DeleteView):
    model = User
    template_name = "gestion/usuarios/confirm_delete.html"
    success_url = reverse_lazy("gestion:usuarios_lista")