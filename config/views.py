from django.shortcuts import render

# Importamos el modelo de parrillas desde la app correspondiente
from apps.parrillas.models import Parrilla
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

def home_view(request):
    """
    Renderiza la página de inicio de ChoriFans con parrillas reales.

    Contexto:
      - parrillas: queryset de Parrilla con las primeras 6 activas,
                   ordenadas por promedio_puntaje DESC.
    """
    # Obtenemos las parrillas activas, ordenadas por puntaje promedio
    parrillas_qs = (
        Parrilla.objects
        .filter(is_active=True)
        .order_by("-promedio_puntaje")[:6]
    )

    context = {
        "parrillas": parrillas_qs,
    }

    return render(request, "home.html", context)
