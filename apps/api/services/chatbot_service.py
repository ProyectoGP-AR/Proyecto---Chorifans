# apps/api/services/chatbot_service.py

import math
import os
import unicodedata
from typing import Any, Dict, List, Optional, Set

from django.db.models import Q
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from google import genai
from google.genai import types

from apps.categorias.models import Categoria
from apps.parrillas.models import Parrilla
from apps.promociones.models import Promocion
from apps.ubicaciones.models import Ubicacion


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _normalize(texto: str) -> str:
    if not texto:
        return ""

    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


def _safe_int(value: Any, default: int = 5, min_value: int = 1, max_value: int = 20) -> int:
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = default
    return max(min_value, min(max_value, value))


def _safe_float(value: Any, default: float = 0.0, min_value: float = 0.0, max_value: float = 5.0) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = default
    return max(min_value, min(max_value, value))


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default

    value_str = str(value).strip().lower()
    if value_str in {"true", "1", "si", "sí", "yes"}:
        return True
    if value_str in {"false", "0", "no"}:
        return False
    return default


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _usuario_pidio_puntaje(mensaje_normalizado: str) -> bool:
    return any(
        expresion in mensaje_normalizado
        for expresion in [
            "puntaje",
            "puntuacion",
            "puntuación",
            "calificacion",
            "calificación",
            "estrellas",
            "cuantas estrellas",
            "cuántas estrellas",
            "cuanto puntaje",
            "cuánto puntaje",
            "ranking",
            "puntuada",
            "puntuadas",
            "puntuado",
            "puntuados",
            "mejor puntuadas",
            "mejor puntuados",
            "top",
            "1 estrella",
            "2 estrellas",
            "3 estrellas",
            "4 estrellas",
            "5 estrellas",
        ]
    )


def _ubicacion_has_coords(ubicacion: Ubicacion) -> bool:
    lat = getattr(ubicacion, "latitud", None)
    lon = getattr(ubicacion, "longitud", None)
    return lat is not None and lon is not None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radio_tierra_km = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radio_tierra_km * c


def _describir_distancia(distancia_km: float) -> str:
    distancia_km = float(distancia_km)

    if distancia_km <= 5:
        return "Muy cerca."
    if distancia_km <= 10:
        return "Relativamente cerca."
    if distancia_km <= 15:
        return "Bastante cerca."
    if distancia_km <= 20:
        return "Moderadamente cerca."
    if distancia_km <= 30:
        return "Moderadamente lejos."
    if distancia_km <= 40:
        return "Bastante lejos."
    if distancia_km <= 50:
        return "Muy lejos."
    return "Estás lejos, pero a 1 hora de viaje en auto aproximadamente."


def _detectar_ubicacion(
    mensaje_normalizado: str,
    excluir_ids: Optional[Set[int]] = None,
) -> Optional[Ubicacion]:
    excluir_ids = excluir_ids or set()

    ubicaciones = list(
        Ubicacion.objects.filter(is_active=True).order_by("nombre_ciudad", "nombre_barrio")
    )

    coincidencias_combo = []
    coincidencias_barrio = []
    coincidencias_ciudad = []

    for ubicacion in ubicaciones:
        if ubicacion.id in excluir_ids:
            continue

        barrio = _normalize(ubicacion.nombre_barrio)
        ciudad = _normalize(ubicacion.nombre_ciudad)
        combo = _normalize(f"{ubicacion.nombre_barrio} {ubicacion.nombre_ciudad}")

        if combo and combo in mensaje_normalizado:
            coincidencias_combo.append((len(combo), ubicacion))
        elif barrio and barrio in mensaje_normalizado:
            coincidencias_barrio.append((len(barrio), ubicacion))
        elif ciudad and ciudad in mensaje_normalizado:
            coincidencias_ciudad.append((len(ciudad), ubicacion))

    for grupo in (coincidencias_combo, coincidencias_barrio, coincidencias_ciudad):
        if grupo:
            grupo.sort(key=lambda item: item[0], reverse=True)
            return grupo[0][1]

    return None


def _detectar_parrilla(mensaje_normalizado: str) -> Optional[Parrilla]:
    parrillas = (
        Parrilla.objects
        .filter(is_active=True)
        .select_related("categoria", "ubicacion")
        .order_by("-promedio_puntaje", "nombre")
    )

    coincidencias = []

    for parrilla in parrillas:
        nombre_normalizado = _normalize(parrilla.nombre)
        if nombre_normalizado and nombre_normalizado in mensaje_normalizado:
            coincidencias.append((len(nombre_normalizado), parrilla))

    if not coincidencias:
        return None

    coincidencias.sort(key=lambda item: item[0], reverse=True)
    return coincidencias[0][1]


def _extraer_categoria_desde_mensaje(mensaje_normalizado: str) -> str:
    coincidencias = []

    for categoria_obj in Categoria.objects.filter(is_active=True):
        nombre_categoria = _normalize(categoria_obj.nombre)
        if nombre_categoria and nombre_categoria in mensaje_normalizado:
            coincidencias.append((len(nombre_categoria), categoria_obj.nombre))

    if not coincidencias:
        return ""

    coincidencias.sort(key=lambda item: item[0], reverse=True)
    return coincidencias[0][1]


def _formatear_parrilla_resultado(
    parrilla_data: Dict[str, Any],
    incluir_distancia: bool = False,
    incluir_puntaje: bool = False,
) -> str:
    nombre = parrilla_data.get("nombre", "Parrilla")
    detalle_url = parrilla_data.get("detalle_url", "#")
    nombre_link = f"[{nombre}]({detalle_url})"

    if incluir_distancia and parrilla_data.get("distancia_km") is not None:
        texto = (
            f"• {nombre_link} "
            f"({parrilla_data['barrio']} - {parrilla_data['ciudad']}, "
            f"{parrilla_data['distancia_km']} km"
        )
        if incluir_puntaje:
            texto += f", puntaje {parrilla_data['puntaje']:.1f}/5"
        texto += ")"
        return texto

    texto = (
        f"• {nombre_link} "
        f"({parrilla_data['categoria']}, {parrilla_data['barrio']} - "
        f"{parrilla_data['ciudad']}"
    )
    if incluir_puntaje:
        texto += f", puntaje {parrilla_data['puntaje']:.1f}/5"
    texto += ")"
    return texto


def _get_origen_ubicacion(barrio: str = "", ciudad: str = "") -> Optional[Ubicacion]:
    barrio = _safe_str(barrio)
    ciudad = _safe_str(ciudad)

    qs = Ubicacion.objects.filter(is_active=True)
    if barrio:
        qs = qs.filter(nombre_barrio__icontains=barrio)
    if ciudad:
        qs = qs.filter(nombre_ciudad__icontains=ciudad)

    for ubicacion in qs.order_by("nombre_ciudad", "nombre_barrio"):
        if _ubicacion_has_coords(ubicacion):
            return ubicacion
    return None


def _get_parrilla_by_name_or_id(parrilla_id: Optional[int] = None, nombre: str = "") -> Optional[Parrilla]:
    nombre = _safe_str(nombre)
    parrilla = None

    if parrilla_id:
        parrilla = (
            Parrilla.objects
            .filter(id=parrilla_id, is_active=True)
            .select_related("categoria", "ubicacion")
            .first()
        )

    if parrilla is None and nombre:
        parrilla = (
            Parrilla.objects
            .filter(nombre__icontains=nombre, is_active=True)
            .select_related("categoria", "ubicacion")
            .order_by("-promedio_puntaje", "nombre")
            .first()
        )

    return parrilla


def _base_parrillas_queryset():
    return (
        Parrilla.objects
        .filter(is_active=True)
        .select_related("categoria", "ubicacion")
    )


def _apply_parrilla_filters(
    qs,
    termino: str = "",
    categoria: str = "",
    barrio: str = "",
    ciudad: str = "",
    min_puntaje: Optional[float] = None,
    max_puntaje: Optional[float] = None,
    solo_con_promociones: bool = False,
):
    termino = _safe_str(termino)
    categoria = _safe_str(categoria)
    barrio = _safe_str(barrio)
    ciudad = _safe_str(ciudad)

    if termino:
        qs = qs.filter(
            Q(nombre__icontains=termino)
            | Q(descripcion__icontains=termino)
            | Q(direccion__icontains=termino)
            | Q(categoria__nombre__icontains=termino)
            | Q(ubicacion__nombre_barrio__icontains=termino)
            | Q(ubicacion__nombre_ciudad__icontains=termino)
        )
    if categoria:
        qs = qs.filter(categoria__nombre__icontains=categoria)
    if barrio:
        qs = qs.filter(ubicacion__nombre_barrio__icontains=barrio)
    if ciudad:
        qs = qs.filter(ubicacion__nombre_ciudad__icontains=ciudad)
    if min_puntaje is not None:
        qs = qs.filter(promedio_puntaje__gte=min_puntaje)
    if max_puntaje is not None:
        qs = qs.filter(promedio_puntaje__lte=max_puntaje)

    if solo_con_promociones:
        hoy = timezone.now().date()
        qs = qs.filter(
            promocion__is_active=True,
            promocion__fecha_inicio__lte=hoy,
            promocion__fecha_fin__gte=hoy,
        )

    return qs.distinct()


def _get_parrilla_detail_url(parrilla: Parrilla) -> str:
    try:
        return reverse("parrillas:detalle", args=[parrilla.id])
    except NoReverseMatch:
        return f"/parrillas/{parrilla.id}/"


def _serialize_parrilla(parrilla: Parrilla) -> Dict[str, Any]:
    return {
        "id": parrilla.id,
        "nombre": parrilla.nombre,
        "detalle_url": _get_parrilla_detail_url(parrilla),
        "categoria": parrilla.categoria.nombre,
        "barrio": parrilla.ubicacion.nombre_barrio,
        "ciudad": parrilla.ubicacion.nombre_ciudad,
        "direccion": parrilla.direccion,
        "puntaje": float(parrilla.promedio_puntaje or 0),
        "descripcion": parrilla.descripcion or "",
        "telefono": parrilla.telefono or "",
        "sitio_web": parrilla.sitio_web or "",
    }


def _serialize_promocion(promocion: Promocion) -> Dict[str, Any]:
    return {
        "id": promocion.id,
        "titulo": promocion.titulo,
        "descripcion": promocion.descripcion,
        "precio_promocional": float(promocion.precio_promocional) if promocion.precio_promocional is not None else None,
        "fecha_inicio": promocion.fecha_inicio.isoformat(),
        "fecha_fin": promocion.fecha_fin.isoformat(),
        "parrilla": promocion.parrilla.nombre,
    }


def _respuesta_bienvenida(context=None) -> str:
    context = context or {}
    current_path = (context.get("currentPath") or "").lower()

    if "categor" in current_path:
        return (
            "¡Hola! Soy Chori Bot 👋\n"
            "Estoy para ayudarte con las categorías del sitio. "
            "Si querés, te puedo decir qué tipos de parrillas hay "
            "o recomendarte algunas opciones destacadas."
        )

    if "ubicacion" in current_path:
        return (
            "¡Hola! Soy Chori Bot 👋\n"
            "Te puedo ayudar a encontrar parrillas por barrio o ciudad. "
            "Decime una ubicación y te recomiendo algunas."
        )

    if "buscar" in current_path:
        return (
            "¡Hola! Soy Chori Bot 👋\n"
            "Podés preguntarme por parrillas, categorías, ubicaciones, promociones o cercanía, "
            "y te doy recomendaciones para que encuentres tu chori ideal."
        )

    return (
        "¡Hola! Soy Chori Bot 👋\n"
        "Puedo ayudarte a encontrar parrillas, categorías, ubicaciones, promociones "
        "o recomendarte opciones destacadas."
    )


def _fallback_rule_based(message: str, context=None) -> str:
    context = context or {}

    if not message or not message.strip():
        return (
            "Contame qué necesitás y te ayudo. "
            "Por ejemplo: “recomendame una parrilla gourmet”, "
            "“¿qué categorías hay?” o “¿qué me queda más cerca?”"
        )

    mensaje = _normalize(message.strip())
    mostrar_puntaje = _usuario_pidio_puntaje(mensaje)

    if any(saludo in mensaje for saludo in ["hola", "buenas", "buen dia", "buenas tardes", "buenas noches", "hey"]):
        if len(mensaje.split()) <= 3:
            return _respuesta_bienvenida(context)

    pregunta_distancia = any(expresion in mensaje for expresion in [
        "que tan lejos",
        "qué tan lejos",
        "cuanto me queda",
        "cuánto me queda",
        "me queda lejos",
        "distancia",
        "que tan cerca",
        "qué tan cerca",
    ])

    pregunta_promociones = any(expresion in mensaje for expresion in [
        "promocion",
        "promociones",
        "promo",
        "promos",
        "descuento",
        "descuentos",
        "oferta",
        "ofertas",
    ])

    pregunta_cercania = any(expresion in mensaje for expresion in [
        "cual me queda mas cerca",
        "cuál me queda más cerca",
        "que me queda mas cerca",
        "qué me queda más cerca",
        "cual es la mas cercana",
        "cuál es la más cercana",
        "cuales me quedan mas cerca",
        "cuáles me quedan más cerca",
        "mas cercana",
        "más cercana",
        "mas cercanas",
        "más cercanas",
    ])

    if pregunta_distancia:
        origen = _detectar_ubicacion(mensaje)
        parrilla_destino = _detectar_parrilla(mensaje)

        if origen and parrilla_destino:
            resultado = _tool_distancia_entre_ubicaciones(
                origen_barrio=origen.nombre_barrio,
                origen_ciudad=origen.nombre_ciudad,
                nombre_parrilla=parrilla_destino.nombre,
            )
            if resultado.get("ok"):
                descripcion_distancia = _describir_distancia(resultado["distancia_km"])
                detalle_url = _get_parrilla_detail_url(parrilla_destino)
                return (
                    f"Desde {resultado['origen']['barrio']} - {resultado['origen']['ciudad']} "
                    f"hasta [{parrilla_destino.nombre}]({detalle_url}) en "
                    f"{resultado['destino']['barrio']} - {resultado['destino']['ciudad']} "
                    f"hay una distancia aproximada de {resultado['distancia_km']} km. "
                    f"{descripcion_distancia}"
                )
            return (
                "No pude calcular la distancia exacta con la información disponible. "
                "Probá consultarme por barrio o ciudad."
            )

        if origen:
            destino = _detectar_ubicacion(mensaje, excluir_ids={origen.id})
            if destino:
                resultado = _tool_distancia_entre_ubicaciones(
                    origen_barrio=origen.nombre_barrio,
                    origen_ciudad=origen.nombre_ciudad,
                    destino_barrio=destino.nombre_barrio,
                    destino_ciudad=destino.nombre_ciudad,
                )
                if resultado.get("ok"):
                    descripcion_distancia = _describir_distancia(resultado["distancia_km"])
                    return (
                        f"Desde {resultado['origen']['barrio']} - {resultado['origen']['ciudad']} "
                        f"hasta {resultado['destino']['barrio']} - {resultado['destino']['ciudad']} "
                        f"hay una distancia aproximada de {resultado['distancia_km']} km. "
                        f"{descripcion_distancia}"
                    )

        return (
            "Para decirte qué tan lejos te queda, necesito reconocer una ubicación de origen "
            "y una parrilla o destino."
        )

    if pregunta_promociones:
        promos = _tool_promociones_vigentes(limit=5)
        if promos["total"] > 0:
            items = "\n".join(f"• {p['titulo']} en {p['parrilla']}" for p in promos["promociones"])
            return f"Estas son algunas promociones vigentes:\n{items}"
        return "Por ahora no encontré promociones vigentes en el sitio."

    if pregunta_cercania:
        origen = _detectar_ubicacion(mensaje)
        solo_recomendadas = "recomendada" in mensaje or "recomendadas" in mensaje
        categoria = _extraer_categoria_desde_mensaje(mensaje)

        if origen:
            resultado = _tool_parrillas_cercanas(
                origen_barrio=origen.nombre_barrio,
                origen_ciudad=origen.nombre_ciudad,
                categoria=categoria,
                solo_recomendadas=solo_recomendadas,
                limit=5,
            )
            if resultado.get("ok") and resultado.get("resultados"):
                items = "\n".join(
                    f"{_formatear_parrilla_resultado(p, incluir_distancia=True, incluir_puntaje=mostrar_puntaje)} — {_describir_distancia(p['distancia_km'])}"
                    for p in resultado["resultados"]
                )
                return (
                    f"Tomando como origen {resultado['origen']['barrio']} - "
                    f"{resultado['origen']['ciudad']}, estas son algunas de las parrillas más cercanas:\n"
                    f"{items}"
                )
            return "No encontré parrillas cercanas con coordenadas cargadas."

        return "Para decirte cuál te queda más cerca, necesito reconocer tu barrio o ciudad de origen."

    if "mejor" in mensaje or "top" in mensaje or "puntuada" in mensaje:
        top = _tool_top_parrillas(limit=5)
        if top["total"] > 0:
            items = "\n".join(
                _formatear_parrilla_resultado(p, incluir_puntaje=mostrar_puntaje)
                for p in top["resultados"]
            )
            return f"Estas son algunas opciones destacadas:\n{items}"
        return "No encontré parrillas destacadas para mostrarte ahora."

    if "peor" in mensaje:
        return (
            "Prefiero recomendarte opciones destacadas del sitio. "
            "Si querés, te muestro parrillas recomendadas por zona, categoría o cercanía."
        )

    if "recomendada" in mensaje or "recomendadas" in mensaje:
        recomendadas = _tool_parrillas_recomendadas(min_puntaje=3.0, limit=5)
        if recomendadas["total"] > 0:
            items = "\n".join(
                _formatear_parrilla_resultado(p, incluir_puntaje=mostrar_puntaje)
                for p in recomendadas["resultados"]
            )
            return f"Estas son algunas parrillas recomendadas:\n{items}"
        return "No encontré parrillas recomendadas en este momento."

    if "categoria" in mensaje or "categorias" in mensaje or "categorías" in mensaje:
        categorias = _tool_listar_categorias(limit=20)
        if categorias["total"] > 0:
            nombres = ", ".join(c["nombre"] for c in categorias["categorias"])
            return f"Las categorías disponibles son: {nombres}."
        return "Por ahora no encontré categorías cargadas."

    return (
        "Puedo ayudarte con cosas como estas:\n"
        "• decirte qué categorías hay\n"
        "• mostrarte opciones destacadas\n"
        "• listar parrillas recomendadas\n"
        "• buscar opciones por barrio o ciudad\n"
        "• mostrarte promociones vigentes\n"
        "• decirte cuál te queda más cerca\n\n"
        "Por ejemplo:\n"
        "“¿Qué me recomendás?”\n"
        "“¿Qué hay en Boedo?”\n"
        "“¿Qué recomendadas hay en Pilar?”\n"
        "“Estoy en Almagro, ¿qué tan lejos me queda una parrilla de Pilar?”"
    )


def _tool_busca_parrillas(
    termino: str = "",
    categoria: str = "",
    barrio: str = "",
    ciudad: str = "",
    min_puntaje: float = 0,
    max_puntaje: Optional[float] = None,
    solo_con_promociones: bool = False,
    limit: int = 5,
) -> Dict[str, Any]:
    limit = _safe_int(limit, default=5, min_value=1, max_value=10)
    min_puntaje = _safe_float(min_puntaje, default=0.0, min_value=0.0, max_value=5.0)
    max_puntaje_value = None
    if max_puntaje is not None:
        max_puntaje_value = _safe_float(max_puntaje, default=5.0, min_value=0.0, max_value=5.0)

    qs = _base_parrillas_queryset()
    qs = _apply_parrilla_filters(
        qs,
        termino=termino,
        categoria=categoria,
        barrio=barrio,
        ciudad=ciudad,
        min_puntaje=min_puntaje,
        max_puntaje=max_puntaje_value,
        solo_con_promociones=_safe_bool(solo_con_promociones),
    ).order_by("-promedio_puntaje", "nombre")

    resultados = [_serialize_parrilla(parrilla) for parrilla in qs[:limit]]

    return {
        "total": len(resultados),
        "filtros": {
            "termino": _safe_str(termino),
            "categoria": _safe_str(categoria),
            "barrio": _safe_str(barrio),
            "ciudad": _safe_str(ciudad),
            "min_puntaje": min_puntaje,
            "max_puntaje": max_puntaje_value,
            "solo_con_promociones": _safe_bool(solo_con_promociones),
        },
        "resultados": resultados,
    }


def _tool_top_parrillas(
    categoria: str = "",
    barrio: str = "",
    ciudad: str = "",
    limit: int = 5,
) -> Dict[str, Any]:
    limit = _safe_int(limit, default=5, min_value=1, max_value=10)
    qs = _apply_parrilla_filters(
        _base_parrillas_queryset(),
        categoria=categoria,
        barrio=barrio,
        ciudad=ciudad,
    ).order_by("-promedio_puntaje", "nombre")

    resultados = [_serialize_parrilla(parrilla) for parrilla in qs[:limit]]
    return {"total": len(resultados), "resultados": resultados}


def _tool_bottom_parrillas(
    categoria: str = "",
    barrio: str = "",
    ciudad: str = "",
    limit: int = 5,
) -> Dict[str, Any]:
    limit = _safe_int(limit, default=5, min_value=1, max_value=10)
    qs = _apply_parrilla_filters(
        _base_parrillas_queryset(),
        categoria=categoria,
        barrio=barrio,
        ciudad=ciudad,
    ).order_by("promedio_puntaje", "nombre")

    resultados = [_serialize_parrilla(parrilla) for parrilla in qs[:limit]]
    return {"total": len(resultados), "resultados": resultados}


def _tool_parrillas_recomendadas(
    min_puntaje: float = 3.0,
    categoria: str = "",
    barrio: str = "",
    ciudad: str = "",
    solo_con_promociones: bool = False,
    limit: int = 5,
) -> Dict[str, Any]:
    limit = _safe_int(limit, default=5, min_value=1, max_value=15)
    min_puntaje = _safe_float(min_puntaje, default=3.0, min_value=0.0, max_value=5.0)
    qs = _apply_parrilla_filters(
        _base_parrillas_queryset(),
        categoria=categoria,
        barrio=barrio,
        ciudad=ciudad,
        min_puntaje=min_puntaje,
        solo_con_promociones=_safe_bool(solo_con_promociones),
    ).order_by("-promedio_puntaje", "nombre")

    resultados = [_serialize_parrilla(parrilla) for parrilla in qs[:limit]]
    return {
        "total": len(resultados),
        "resultados": resultados,
    }





def _tool_listar_categorias(limit: int = 20) -> Dict[str, Any]:
    limit = _safe_int(limit, default=20, min_value=1, max_value=50)
    categorias = []
    for categoria in Categoria.objects.filter(is_active=True).order_by("nombre")[:limit]:
        categorias.append(
            {
                "id": categoria.id,
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion or "",
            }
        )
    return {"total": len(categorias), "categorias": categorias}


def _tool_listar_ubicaciones(ciudad: str = "", limit: int = 20) -> Dict[str, Any]:
    limit = _safe_int(limit, default=20, min_value=1, max_value=50)
    ciudad = _safe_str(ciudad)
    qs = Ubicacion.objects.filter(is_active=True)
    if ciudad:
        qs = qs.filter(nombre_ciudad__icontains=ciudad)

    ubicaciones = []
    for ubicacion in qs.order_by("nombre_ciudad", "nombre_barrio")[:limit]:
        ubicaciones.append(
            {
                "id": ubicacion.id,
                "barrio": ubicacion.nombre_barrio,
                "ciudad": ubicacion.nombre_ciudad,
                "tiene_coordenadas": _ubicacion_has_coords(ubicacion),
            }
        )
    return {"total": len(ubicaciones), "ubicaciones": ubicaciones}


def _tool_detalle_parrilla(parrilla_id: Optional[int] = None, nombre: str = "") -> Dict[str, Any]:
    parrilla = _get_parrilla_by_name_or_id(parrilla_id=parrilla_id, nombre=nombre)
    if parrilla is None:
        return {"encontrada": False, "detalle": None}

    detalle = _serialize_parrilla(parrilla)
    detalle["tiene_coordenadas"] = _ubicacion_has_coords(parrilla.ubicacion)
    promos = _tool_promociones_vigentes(nombre_parrilla=parrilla.nombre, limit=10)
    detalle["promociones_vigentes"] = promos["promociones"]
    return {"encontrada": True, "detalle": detalle}


def _tool_promociones_vigentes(
    nombre_parrilla: str = "",
    barrio: str = "",
    ciudad: str = "",
    limit: int = 5,
) -> Dict[str, Any]:
    nombre_parrilla = _safe_str(nombre_parrilla)
    barrio = _safe_str(barrio)
    ciudad = _safe_str(ciudad)
    limit = _safe_int(limit, default=5, min_value=1, max_value=20)
    hoy = timezone.now().date()

    qs = (
        Promocion.objects
        .filter(
            is_active=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
            parrilla__is_active=True,
        )
        .select_related("parrilla", "parrilla__ubicacion")
        .order_by("fecha_fin", "titulo")
    )

    if nombre_parrilla:
        qs = qs.filter(parrilla__nombre__icontains=nombre_parrilla)
    if barrio:
        qs = qs.filter(parrilla__ubicacion__nombre_barrio__icontains=barrio)
    if ciudad:
        qs = qs.filter(parrilla__ubicacion__nombre_ciudad__icontains=ciudad)

    promociones = [_serialize_promocion(promo) for promo in qs[:limit]]
    return {"total": len(promociones), "promociones": promociones}


def _tool_distancia_entre_ubicaciones(
    origen_barrio: str = "",
    origen_ciudad: str = "",
    destino_barrio: str = "",
    destino_ciudad: str = "",
    nombre_parrilla: str = "",
) -> Dict[str, Any]:
    origen = _get_origen_ubicacion(barrio=origen_barrio, ciudad=origen_ciudad)
    destino = None

    nombre_parrilla = _safe_str(nombre_parrilla)
    if nombre_parrilla:
        parrilla = _get_parrilla_by_name_or_id(nombre=nombre_parrilla)
        if parrilla and _ubicacion_has_coords(parrilla.ubicacion):
            destino = parrilla.ubicacion

    if destino is None:
        destino = _get_origen_ubicacion(barrio=destino_barrio, ciudad=destino_ciudad)

    if origen is None:
        return {"ok": False, "motivo": "No encontré coordenadas para la ubicación de origen.", "distancia_km": None}
    if destino is None:
        return {"ok": False, "motivo": "No encontré coordenadas para la ubicación de destino o la parrilla solicitada.", "distancia_km": None}

    distancia_km = _haversine_km(
        float(origen.latitud),
        float(origen.longitud),
        float(destino.latitud),
        float(destino.longitud),
    )

    return {
        "ok": True,
        "origen": {"barrio": origen.nombre_barrio, "ciudad": origen.nombre_ciudad},
        "destino": {"barrio": destino.nombre_barrio, "ciudad": destino.nombre_ciudad},
        "distancia_km": round(distancia_km, 2),
        "nombre_parrilla": nombre_parrilla or None,
    }


def _tool_parrillas_cercanas(
    origen_barrio: str = "",
    origen_ciudad: str = "",
    categoria: str = "",
    min_puntaje: float = 0,
    solo_recomendadas: bool = False,
    limit: int = 5,
) -> Dict[str, Any]:
    origen = _get_origen_ubicacion(barrio=origen_barrio, ciudad=origen_ciudad)
    if origen is None:
        return {"ok": False, "motivo": "No encontré coordenadas para la ubicación de origen.", "resultados": []}

    limit = _safe_int(limit, default=5, min_value=1, max_value=15)
    min_puntaje = _safe_float(min_puntaje, default=0.0, min_value=0.0, max_value=5.0)

    if _safe_bool(solo_recomendadas) and min_puntaje < 3.0:
        min_puntaje = 3.0

    qs = _apply_parrilla_filters(
        _base_parrillas_queryset(),
        categoria=categoria,
        min_puntaje=min_puntaje,
    )

    resultados = []
    for parrilla in qs:
        if not _ubicacion_has_coords(parrilla.ubicacion):
            continue

        distancia_km = _haversine_km(
            float(origen.latitud),
            float(origen.longitud),
            float(parrilla.ubicacion.latitud),
            float(parrilla.ubicacion.longitud),
        )

        item = _serialize_parrilla(parrilla)
        item["distancia_km"] = round(distancia_km, 2)
        resultados.append(item)

    resultados.sort(key=lambda x: (x["distancia_km"], -x["puntaje"], x["nombre"]))

    return {
        "ok": True,
        "origen": {"barrio": origen.nombre_barrio, "ciudad": origen.nombre_ciudad},
        "total": min(len(resultados), limit),
        "resultados": resultados[:limit],
    }


def _build_tool_declarations() -> List[types.Tool]:
    function_declarations = [
        types.FunctionDeclaration(
            name="buscar_parrillas",
            description="Busca parrillas del sitio por nombre, categoría, barrio, ciudad, puntaje mínimo o promociones.",
            parameters={
                "type": "object",
                "properties": {
                    "termino": {"type": "string"},
                    "categoria": {"type": "string"},
                    "barrio": {"type": "string"},
                    "ciudad": {"type": "string"},
                    "min_puntaje": {"type": "number"},
                    "max_puntaje": {"type": "number"},
                    "solo_con_promociones": {"type": "boolean"},
                    "limit": {"type": "integer"},
                },
            },
        ),
        types.FunctionDeclaration(
            name="top_parrillas",
            description="Devuelve parrillas destacadas según el ranking del sitio.",
            parameters={
                "type": "object",
                "properties": {
                    "categoria": {"type": "string"},
                    "barrio": {"type": "string"},
                    "ciudad": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            },
        ),
        types.FunctionDeclaration(
            name="bottom_parrillas",
            description="Devuelve opciones de menor valoración para uso interno del asistente.",
            parameters={
                "type": "object",
                "properties": {
                    "categoria": {"type": "string"},
                    "barrio": {"type": "string"},
                    "ciudad": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            },
        ),
        types.FunctionDeclaration(
            name="parrillas_recomendadas",
            description="Lista parrillas recomendadas según el criterio interno de recomendación de ChoriFans.",
            parameters={
                "type": "object",
                "properties": {
                    "min_puntaje": {"type": "number"},
                    "categoria": {"type": "string"},
                    "barrio": {"type": "string"},
                    "ciudad": {"type": "string"},
                    "solo_con_promociones": {"type": "boolean"},
                    "limit": {"type": "integer"},
                },
            },
        ),
        types.FunctionDeclaration(
            name="listar_categorias",
            description="Lista las categorías activas disponibles en ChoriFans.",
            parameters={"type": "object", "properties": {"limit": {"type": "integer"}}},
        ),
        types.FunctionDeclaration(
            name="listar_ubicaciones",
            description="Lista barrios y ciudades disponibles en ChoriFans.",
            parameters={
                "type": "object",
                "properties": {
                    "ciudad": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            },
        ),
        types.FunctionDeclaration(
            name="detalle_parrilla",
            description="Devuelve el detalle de una parrilla usando su id o su nombre.",
            parameters={
                "type": "object",
                "properties": {
                    "parrilla_id": {"type": "integer"},
                    "nombre": {"type": "string"},
                },
            },
        ),
        types.FunctionDeclaration(
            name="promociones_vigentes",
            description="Devuelve promociones vigentes del sitio, o filtradas por parrilla, barrio o ciudad.",
            parameters={
                "type": "object",
                "properties": {
                    "nombre_parrilla": {"type": "string"},
                    "barrio": {"type": "string"},
                    "ciudad": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            },
        ),
        types.FunctionDeclaration(
            name="distancia_entre_ubicaciones",
            description="Calcula distancia aproximada en kilómetros entre un origen y un destino, o entre un origen y la ubicación de una parrilla.",
            parameters={
                "type": "object",
                "properties": {
                    "origen_barrio": {"type": "string"},
                    "origen_ciudad": {"type": "string"},
                    "destino_barrio": {"type": "string"},
                    "destino_ciudad": {"type": "string"},
                    "nombre_parrilla": {"type": "string"},
                },
            },
        ),
        types.FunctionDeclaration(
            name="parrillas_cercanas",
            description="Devuelve las parrillas más cercanas a una ubicación de origen.",
            parameters={
                "type": "object",
                "properties": {
                    "origen_barrio": {"type": "string"},
                    "origen_ciudad": {"type": "string"},
                    "categoria": {"type": "string"},
                    "min_puntaje": {"type": "number"},
                    "solo_recomendadas": {"type": "boolean"},
                    "limit": {"type": "integer"},
                },
            },
        ),
    ]
    return [types.Tool(function_declarations=function_declarations)]


def _execute_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "buscar_parrillas":
        return _tool_busca_parrillas(
            termino=args.get("termino", ""),
            categoria=args.get("categoria", ""),
            barrio=args.get("barrio", ""),
            ciudad=args.get("ciudad", ""),
            min_puntaje=args.get("min_puntaje", 0),
            max_puntaje=args.get("max_puntaje"),
            solo_con_promociones=args.get("solo_con_promociones", False),
            limit=args.get("limit", 5),
        )
    if name == "top_parrillas":
        return _tool_top_parrillas(
            categoria=args.get("categoria", ""),
            barrio=args.get("barrio", ""),
            ciudad=args.get("ciudad", ""),
            limit=args.get("limit", 5),
        )
    if name == "bottom_parrillas":
        return _tool_bottom_parrillas(
            categoria=args.get("categoria", ""),
            barrio=args.get("barrio", ""),
            ciudad=args.get("ciudad", ""),
            limit=args.get("limit", 5),
        )
    if name == "parrillas_recomendadas":
        return _tool_parrillas_recomendadas(
            min_puntaje=args.get("min_puntaje", 3.0),
            categoria=args.get("categoria", ""),
            barrio=args.get("barrio", ""),
            ciudad=args.get("ciudad", ""),
            solo_con_promociones=args.get("solo_con_promociones", False),
            limit=args.get("limit", 5),
        )
    if name == "listar_categorias":
        return _tool_listar_categorias(limit=args.get("limit", 20))
    if name == "listar_ubicaciones":
        return _tool_listar_ubicaciones(
            ciudad=args.get("ciudad", ""),
            limit=args.get("limit", 20),
        )
    if name == "detalle_parrilla":
        return _tool_detalle_parrilla(
            parrilla_id=args.get("parrilla_id"),
            nombre=args.get("nombre", ""),
        )
    if name == "promociones_vigentes":
        return _tool_promociones_vigentes(
            nombre_parrilla=args.get("nombre_parrilla", ""),
            barrio=args.get("barrio", ""),
            ciudad=args.get("ciudad", ""),
            limit=args.get("limit", 5),
        )
    if name == "distancia_entre_ubicaciones":
        return _tool_distancia_entre_ubicaciones(
            origen_barrio=args.get("origen_barrio", ""),
            origen_ciudad=args.get("origen_ciudad", ""),
            destino_barrio=args.get("destino_barrio", ""),
            destino_ciudad=args.get("destino_ciudad", ""),
            nombre_parrilla=args.get("nombre_parrilla", ""),
        )
    if name == "parrillas_cercanas":
        return _tool_parrillas_cercanas(
            origen_barrio=args.get("origen_barrio", ""),
            origen_ciudad=args.get("origen_ciudad", ""),
            categoria=args.get("categoria", ""),
            min_puntaje=args.get("min_puntaje", 0),
            solo_recomendadas=args.get("solo_recomendadas", False),
            limit=args.get("limit", 5),
        )
    return {"error": f"Herramienta no soportada: {name}"}


def _build_system_instruction(context: Optional[Dict[str, Any]] = None) -> str:
    context = context or {}
    current_path = context.get("currentPath", "")
    current_view = context.get("currentView", "")
    page_title = context.get("pageTitle", "")
    is_authenticated = context.get("isAuthenticated", False)

    return (
        "Sos Chori Bot, el asistente de ChoriFans. "
        "Respondés en castellano rioplatense, de forma amable, clara, concreta y natural. "
        "Ayudás a usuarios a encontrar parrillas, categorías, ubicaciones, promociones, rankings y cercanía. "
        "Usá las herramientas siempre que necesites datos del sistema. "
        "No inventes parrillas, categorías, ubicaciones, promociones, puntajes ni distancias. "
        "Si una consulta pide datos del sitio, primero llamá a la herramienta adecuada. "
        "Después, con el resultado, redactá una respuesta humana y útil. "
        "Reglas importantes: "
        "1) Si preguntan por opciones destacadas o mejores, usá top_parrillas. "
        "2) Si preguntan por recomendadas, usá parrillas_recomendadas con el criterio interno del sistema, pero no expliques umbrales, mínimos de puntaje ni reglas internas al usuario. "
        "3) No menciones puntajes, estrellas ni valoraciones bajas o negativas salvo que el usuario lo pida explícitamente. "
        "4) Si preguntan por peores o valoraciones negativas, reconducí la conversación hacia opciones destacadas del sitio sin exponer puntajes bajos. "
        "5) Si preguntan qué tan lejos queda una parrilla o una ubicación, usá distancia_entre_ubicaciones. "
        "6) Si preguntan cuál queda más cerca, usá parrillas_cercanas. "
        "7) Si preguntan por promociones, usá promociones_vigentes. "
        "8) Si no hay coordenadas para calcular distancia, decilo claramente y ofrecé alternativas por barrio o ciudad. "
        "9) Cuando haya varias opciones, listalas y destacá las más relevantes. "
        "Contexto actual del usuario: "
        f"currentPath={current_path}; currentView={current_view}; "
        f"pageTitle={page_title}; isAuthenticated={is_authenticated}."
    )


def _build_contents(message: str, context: Optional[Dict[str, Any]] = None) -> List[types.Content]:
    context = context or {}

    context_lines = [
        f"Ruta actual: {context.get('currentPath', '')}",
        f"Vista actual: {context.get('currentView', '')}",
        f"Título de la página: {context.get('pageTitle', '')}",
        f"Autenticado: {context.get('isAuthenticated', False)}",
        f"Usuario: {context.get('username', '')}",
    ]

    user_text = (
        "Mensaje del usuario:\n"
        f"{message}\n\n"
        "Contexto de la página:\n"
        + "\n".join(context_lines)
    )

    return [types.Content(role="user", parts=[types.Part(text=user_text)])]


def _get_gemini_client():
    if not GEMINI_API_KEY or GEMINI_API_KEY == "tu_clave":
        return None
    return genai.Client(api_key=GEMINI_API_KEY)


def _gemini_function_call_response(message: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    client = _get_gemini_client()
    if client is None:
        return None

    tools = _build_tool_declarations()
    config = types.GenerateContentConfig(
        tools=tools,
        system_instruction=_build_system_instruction(context),
    )
    contents = _build_contents(message, context)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=config,
    )

    function_calls = getattr(response, "function_calls", None) or []
    if not function_calls:
        if getattr(response, "text", None):
            return response.text
        return None

    function_response_parts = []
    for function_call in function_calls:
        args = dict(function_call.args or {})
        result = _execute_tool_call(function_call.name, args)

        kwargs = {
            "name": function_call.name,
            "response": {"result": result},
        }
        if getattr(function_call, "id", None):
            kwargs["id"] = function_call.id

        function_response_parts.append(types.Part.from_function_response(**kwargs))

    if getattr(response, "candidates", None):
        contents.append(response.candidates[0].content)
    contents.append(types.Content(role="user", parts=function_response_parts))

    final_response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=config,
    )

    if getattr(final_response, "text", None):
        return final_response.text
    return None


def get_chori_bot_response(message: str, context=None) -> str:
    context = context or {}

    if not message or not message.strip():
        return (
            "Contame qué necesitás y te ayudo. "
            "Por ejemplo: “recomendame una parrilla gourmet”, "
            "“¿qué categorías hay?” o “¿qué me queda más cerca?”"
        )

    try:
        respuesta_gemini = _gemini_function_call_response(message, context)
        if respuesta_gemini:
            return respuesta_gemini
    except Exception as e:
        error_text = str(e)
        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            respuesta_local = _fallback_rule_based(message, context)
            return (
                " "
                f"{respuesta_local}"
            )

        respuesta_local = _fallback_rule_based(message, context)
        return (
            " "
            f"{respuesta_local}"
        )

    return _fallback_rule_based(message, context)