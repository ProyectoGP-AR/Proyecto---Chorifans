from django.views.generic import TemplateView  # Importamos la clase base para vistas de tipo template
from apps.parrillas.models import Parrilla # Importamos el modelo Parrilla para mostrar info en el inicio

# ============================================================
# Vista: home_view
# Página de inicio de ChoriFans.
#
# Por ahora:
#   - Solo muestra el template "home.html".
#   - Más adelante vamos a pasarle datos reales:
#       * Lista de parrillas destacadas
#       * Promociones activas
#       * Categorías / ubicaciones
# ============================================================

# ============================================================
# Vista: home_view
# Página de inicio de ChoriFans.
#
# Ahora:
#   - Trae parrillas reales desde la base de datos.
#   - Filtra solo las activas.
#   - Las ordena por promedio_puntaje (de mayor a menor).
#   - Limita a las primeras 6 para mostrar como "destacadas".
# ============================================================

class HomeView(TemplateView):
    """
    Vista basada en clases (Class-Based View) para la página de inicio.

    Hereda de TemplateView, que está pensada para:
      - Renderizar un template concreto
      - Opcionalmente agregar datos al contexto

    """

    # Nombre del template que se va a usar para esta vista
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        """
        Método que nos permite agregar datos al contexto del template.

        - Llamamos a super() para obtener el contexto base.
        - Agregamos la lista de parrillas activas ordenadas por puntaje.
        """
        context = super().get_context_data(**kwargs)

        # Obtenemos las parrillas activas, ordenadas por puntaje promedio
        parrillas_qs = (
            Parrilla.objects
            .filter(is_active=True)
            .order_by("-promedio_puntaje")[:6]
        )

        # En el template se usa la variable "parrillas"
        context["parrillas"] = parrillas_qs

        return context