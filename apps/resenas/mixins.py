# apps/resenas/mixins.py

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.accounts.models import Profile


class DuenioParrillaMixin(LoginRequiredMixin):
    """
    Mixin para vistas que solo pueden usar usuarios dueños de una parrilla.

    - Requiere que el usuario esté autenticado.
    - Requiere que tenga Profile.
    - Requiere que ese Profile tenga:
        es_duenio_parrilla = True
        parrilla_asociada != None

    Si todo eso se cumple, deja disponible self.parrilla_duenio para usar
    en la vista (por ejemplo, para filtrar las reseñas de ESA parrilla).
    """

    def dispatch(self, request, *args, **kwargs):
        # Primero nos aseguramos que esté logueado (LoginRequiredMixin ya ayuda, pero reforzamos)
        if not request.user.is_authenticated:
            # Esto lo manejará LoginRequiredMixin redirigiendo al login,
            # pero podemos cortar igual por seguridad.
            raise PermissionDenied("Debe iniciar sesión para acceder aquí.")

        # Obtenemos el profile del usuario
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            raise PermissionDenied("No tiene un perfil configurado.")

        # Verificamos que sea dueño de parrilla y tenga parrilla asociada
        if not profile.es_duenio_parrilla or not profile.parrilla_asociada:
            raise PermissionDenied(
                "No tiene permisos para valorar reseñas. "
                "Este panel es solo para dueños de parrillas."
            )

        # Guardamos la parrilla del dueño para usarla en la vista
        self.parrilla_duenio = profile.parrilla_asociada

        # Continuamos el flujo normal de la vista
        return super().dispatch(request, *args, **kwargs)
