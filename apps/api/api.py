"""
API oficial de ChoriFans implementada con Django Ninja.

Este archivo está completamente comentado y estructurado para cumplir
con todos los requisitos del TP final de la materia:

✔ CRUD completo por cada recurso
✔ Parámetros de ruta y de consulta
✔ Paginación (requisito 22 del TP)
✔ Protección de endpoints sensibles (auth=session_auth)
✔ Schemas basados en Pydantic (Ninja Schema)
✔ Esquemas anidados simples (categoría + ubicación dentro de parrilla)
✔ Filtros avanzados en listados
✔ Manejo claro de errores
"""

# ============================================================
#   IMPORTS
# ============================================================

from typing import List
from datetime import datetime

from django.utils import timezone
from django.contrib.auth.models import User

from ninja import NinjaAPI, Schema, Query
from ninja.security import SessionAuth
from ninja.errors import HttpError

from apps.categorias.models import Categoria
from apps.ubicaciones.models import Ubicacion
from apps.parrillas.models import Parrilla
from apps.resenas.models import Resena
from apps.promociones.models import Promocion

# Helper para paginación (creado por nosotros en apps/api/pagination.py)
from apps.api.pagination import paginate_queryset


# ============================================================
#   API PRINCIPAL
# ============================================================

api = NinjaAPI(
    title="ChoriFans API",
    version="1.0.0",
    description="API oficial del proyecto ChoriFans.",
)

# Autenticación basada en la sesión del usuario (login del sitio)
session_auth = SessionAuth()


# ============================================================
#   PING – ENDPOINT DE PRUEBA
# ============================================================

@api.get("/ping")
def ping(request):
    """Devuelve pong=True para comprobar que la API funciona."""
    return {"pong": True}


# ============================================================
#   MODELOS DE PAGINACIÓN
# ============================================================

class PaginatedResponse(Schema):
    """
    Esquema estándar para cualquier respuesta paginada.

    page         → Nº de página actual
    page_size    → Cantidad de elementos por página
    total_items  → Total de registros en la base
    total_pages  → Total de páginas calculadas
    results      → Lista con los datos reales (p.ej., parrillas)
    """
    page: int
    page_size: int
    total_items: int
    total_pages: int
    results: list


# ============================================================
#   SCHEMAS ANIDADOS (Opción B = simple)
# ============================================================

class CategoriaSimple(Schema):
    """Esquema simple para anidar dentro de Parrilla."""
    id: int
    nombre: str


class UbicacionSimple(Schema):
    """Esquema simple para anidar dentro de Parrilla."""
    id: int
    nombre_ciudad: str
    nombre_barrio: str


# ============================================================
#   SCHEMAS COMPLETOS POR RECURSO
# ============================================================

# ------------------- CATEGORÍAS -------------------

class CategoriaBaseSchema(Schema):
    """Payload para crear/editar categorías."""
    nombre: str
    slug: str
    descripcion: str | None = None
    is_active: bool = True


class CategoriaOutSchema(CategoriaBaseSchema):
    """Respuesta enviada al cliente."""
    id: int
    created_at: datetime
    updated_at: datetime


# ------------------- UBICACIONES -------------------

class UbicacionBaseSchema(Schema):
    """Payload para crear/editar ubicaciones."""
    nombre_ciudad: str
    nombre_barrio: str
    latitud: float | None = None
    longitud: float | None = None
    google_maps_url: str | None = None
    is_active: bool = True


class UbicacionOutSchema(UbicacionBaseSchema):
    """Respuesta enviada al cliente."""
    id: int
    created_at: datetime
    updated_at: datetime


# ------------------- PARRILLAS -------------------

class ParrillaBaseSchema(Schema):
    """
    Payload para crear/editar parrillas.
    Recibe categoría y ubicación como IDs.
    """
    nombre: str
    descripcion: str | None = None
    direccion: str
    telefono: str | None = None
    sitio_web: str | None = None
    ubicacion_id: int
    categoria_id: int
    is_active: bool = True
    promedio_puntaje: float | None = None


class ParrillaOutSchema(Schema):
    """
    Esquema COMPLETO de salida de parrilla:

    ✔ Datos propios
    ✔ Categoría anidada (simple)
    ✔ Ubicación anidada (simple)
    """
    id: int
    nombre: str
    descripcion: str | None
    direccion: str
    telefono: str | None
    sitio_web: str | None
    is_active: bool
    promedio_puntaje: float | None
    created_at: datetime
    updated_at: datetime

    # Esquemas anidados simples (Opción B)
    categoria: CategoriaSimple
    ubicacion: UbicacionSimple


# ------------------- RESEÑAS -------------------

class ResenaBaseSchema(Schema):
    usuario_id: int
    parrilla_id: int
    puntaje: int
    comentario: str
    is_active: bool = True


class ResenaOutSchema(ResenaBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


# ------------------- PROMOCIONES -------------------

class PromocionBaseSchema(Schema):
    parrilla_id: int
    titulo: str
    descripcion: str
    precio_promocional: float | None
    fecha_inicio: datetime
    fecha_fin: datetime
    is_active: bool = True


class PromocionOutSchema(PromocionBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


# ============================================================
#   CATEGORÍAS – CRUD
# ============================================================

@api.get("/categorias", response=List[CategoriaOutSchema])
def listar_categorias(request):
    return list(Categoria.objects.all().order_by("nombre"))


@api.post("/categorias", response=CategoriaOutSchema, auth=session_auth)
def crear_categoria(request, payload: CategoriaBaseSchema):
    return Categoria.objects.create(**payload.dict())


@api.get("/categorias/{categoria_id}", response=CategoriaOutSchema)
def detalle_categoria(request, categoria_id: int):
    try:
        return Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        raise HttpError(404, "Categoría no encontrada")


@api.put("/categorias/{categoria_id}", response=CategoriaOutSchema, auth=session_auth)
def actualizar_categoria(request, categoria_id: int, payload: CategoriaBaseSchema):
    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        raise HttpError(404, "Categoría no encontrada")

    for k, v in payload.dict().items():
        setattr(categoria, k, v)

    categoria.save()
    return categoria


@api.delete("/categorias/{categoria_id}", auth=session_auth)
def eliminar_categoria(request, categoria_id: int):
    try:
        Categoria.objects.get(id=categoria_id).delete()
    except Categoria.DoesNotExist:
        raise HttpError(404, "Categoría no encontrada")

    return {"success": True}


# ============================================================
#   UBICACIONES – CRUD
# ============================================================

@api.get("/ubicaciones", response=List[UbicacionOutSchema])
def listar_ubicaciones(request):
    return list(Ubicacion.objects.all().order_by("nombre_ciudad", "nombre_barrio"))


@api.post("/ubicaciones", response=UbicacionOutSchema, auth=session_auth)
def crear_ubicacion(request, payload: UbicacionBaseSchema):
    return Ubicacion.objects.create(**payload.dict())


@api.get("/ubicaciones/{ubicacion_id}", response=UbicacionOutSchema)
def detalle_ubicacion(request, ubicacion_id: int):
    try:
        return Ubicacion.objects.get(id=ubicacion_id)
    except Ubicacion.DoesNotExist:
        raise HttpError(404, "Ubicación no encontrada")


@api.put("/ubicaciones/{ubicacion_id}", response=UbicacionOutSchema, auth=session_auth)
def actualizar_ubicacion(request, ubicacion_id: int, payload: UbicacionBaseSchema):
    try:
        ubicacion = Ubicacion.objects.get(id=ubicacion_id)
    except Ubicacion.DoesNotExist:
        raise HttpError(404, "Ubicación no encontrada")

    for k, v in payload.dict().items():
        setattr(ubicacion, k, v)

    ubicacion.save()
    return ubicacion


@api.delete("/ubicaciones/{ubicacion_id}", auth=session_auth)
def eliminar_ubicacion(request, ubicacion_id: int):
    try:
        Ubicacion.objects.get(id=ubicacion_id).delete()
    except Ubicacion.DoesNotExist:
        raise HttpError(404, "Ubicación no encontrada")

    return {"success": True}


# ============================================================
#   PARRILLAS – CRUD + FILTROS + PAGINACIÓN
# ============================================================

@api.get("/parrillas", response=List[ParrillaOutSchema])
def listar_parrillas(request, categoria_id: int | None = None, ubicacion_id: int | None = None, min_puntaje: float | None = None):
    qs = Parrilla.objects.filter(is_active=True)

    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)
    if ubicacion_id:
        qs = qs.filter(ubicacion_id=ubicacion_id)
    if min_puntaje:
        qs = qs.filter(promedio_puntaje__gte=min_puntaje)

    return [convert_parrilla(p) for p in qs.order_by("nombre")]


@api.get("/parrillas/paginadas", response=PaginatedResponse)
def listar_parrillas_paginadas(request, page: int = Query(1), page_size: int = Query(10)):
    qs = Parrilla.objects.filter(is_active=True).order_by("nombre")
    return paginate_queryset(qs, page, page_size, converter=convert_parrilla)


@api.post("/parrillas", response=ParrillaOutSchema, auth=session_auth)
def crear_parrilla(request, payload: ParrillaBaseSchema):
    try:
        ubicacion = Ubicacion.objects.get(id=payload.ubicacion_id)
        categoria = Categoria.objects.get(id=payload.categoria_id)
    except:
        raise HttpError(404, "Categoría o ubicación inválida")

    parrilla = Parrilla.objects.create(
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        direccion=payload.direccion,
        telefono=payload.telefono,
        sitio_web=payload.sitio_web,
        ubicacion=ubicacion,
        categoria=categoria,
        is_active=payload.is_active,
        promedio_puntaje=payload.promedio_puntaje,
    )

    return convert_parrilla(parrilla)


@api.get("/parrillas/{parrilla_id}", response=ParrillaOutSchema)
def detalle_parrilla(request, parrilla_id: int):
    try:
        parrilla = Parrilla.objects.get(id=parrilla_id)
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    return convert_parrilla(parrilla)


@api.put("/parrillas/{parrilla_id}", response=ParrillaOutSchema, auth=session_auth)
def actualizar_parrilla(request, parrilla_id: int, payload: ParrillaBaseSchema):
    try:
        parrilla = Parrilla.objects.get(id=parrilla_id)
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    try:
        ubicacion = Ubicacion.objects.get(id=payload.ubicacion_id)
        categoria = Categoria.objects.get(id=payload.categoria_id)
    except:
        raise HttpError(404, "Categoría o ubicación inválida")

    for k, v in payload.dict().items():
        if k == "categoria_id":
            parrilla.categoria = categoria
        elif k == "ubicacion_id":
            parrilla.ubicacion = ubicacion
        else:
            setattr(parrilla, k, v)

    parrilla.save()
    return convert_parrilla(parrilla)


@api.delete("/parrillas/{parrilla_id}", auth=session_auth)
def eliminar_parrilla(request, parrilla_id: int):
    try:
        Parrilla.objects.get(id=parrilla_id).delete()
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    return {"success": True}


# Conversor a esquema anidado simple
def convert_parrilla(p):
    return {
        "id": p.id,
        "nombre": p.nombre,
        "descripcion": p.descripcion,
        "direccion": p.direccion,
        "telefono": p.telefono,
        "sitio_web": p.sitio_web,
        "is_active": p.is_active,
        "promedio_puntaje": p.promedio_puntaje,
        "created_at": p.created_at,
        "updated_at": p.updated_at,

        "categoria": {
            "id": p.categoria.id,
            "nombre": p.categoria.nombre,
        },
        "ubicacion": {
            "id": p.ubicacion.id,
            "nombre_ciudad": p.ubicacion.nombre_ciudad,
            "nombre_barrio": p.ubicacion.nombre_barrio,
        }
    }


# ============================================================
#   RESEÑAS – CRUD
# ============================================================

@api.get("/resenas", response=List[ResenaOutSchema])
def listar_resenas(request):
    return list(Resena.objects.all().order_by("-created_at"))


@api.post("/resenas", response=ResenaOutSchema, auth=session_auth)
def crear_resena(request, payload: ResenaBaseSchema):
    try:
        usuario = User.objects.get(id=payload.usuario_id)
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except:
        raise HttpError(404, "Usuario o parrilla no encontrada")

    # Solo 1 reseña por usuario/parrilla
    if Resena.objects.filter(usuario=usuario, parrilla=parrilla).exists():
        raise HttpError(400, "Ya existe una reseña de este usuario para esta parrilla")

    return Resena.objects.create(
        usuario=usuario,
        parrilla=parrilla,
        puntaje=payload.puntaje,
        comentario=payload.comentario,
        is_active=payload.is_active,
    )


@api.get("/resenas/{resena_id}", response=ResenaOutSchema)
def detalle_resena(request, resena_id: int):
    try:
        return Resena.objects.get(id=resena_id)
    except Resena.DoesNotExist:
        raise HttpError(404, "Reseña no encontrada")


@api.put("/resenas/{resena_id}", response=ResenaOutSchema, auth=session_auth)
def actualizar_resena(request, resena_id: int, payload: ResenaBaseSchema):
    try:
        resena = Resena.objects.get(id=resena_id)
        usuario = User.objects.get(id=payload.usuario_id)
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except:
        raise HttpError(404, "Datos inválidos")

    # Evita duplicados
    if Resena.objects.filter(usuario=usuario, parrilla=parrilla).exclude(id=resena_id).exists():
        raise HttpError(400, "Ya existe otra reseña para esta parrilla")

    resena.usuario = usuario
    resena.parrilla = parrilla
    resena.puntaje = payload.puntaje
    resena.comentario = payload.comentario
    resena.is_active = payload.is_active
    resena.save()

    return resena


@api.delete("/resenas/{resena_id}", auth=session_auth)
def eliminar_resena(request, resena_id: int):
    try:
        Resena.objects.get(id=resena_id).delete()
    except Resena.DoesNotExist:
        raise HttpError(404, "Reseña no encontrada")

    return {"success": True}


# ============================================================
#   PROMOCIONES – CRUD
# ============================================================

@api.get("/promociones", response=List[PromocionOutSchema])
def listar_promociones(request, solo_activas: bool = False):
    qs = Promocion.objects.all()

    if solo_activas:
        hoy = timezone.now().date()
        qs = qs.filter(
            is_active=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        )

    return list(qs.order_by("-fecha_inicio"))


@api.post("/promociones", response=PromocionOutSchema, auth=session_auth)
def crear_promocion(request, payload: PromocionBaseSchema):
    try:
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    return Promocion.objects.create(
        parrilla=parrilla,
        titulo=payload.titulo,
        descripcion=payload.descripcion,
        precio_promocional=payload.precio_promocional,
        fecha_inicio=payload.fecha_inicio,
        fecha_fin=payload.fecha_fin,
        is_active=payload.is_active,
    )


@api.get("/promociones/{promo_id}", response=PromocionOutSchema)
def detalle_promocion(request, promo_id: int):
    try:
        return Promocion.objects.get(id=promo_id)
    except Promocion.DoesNotExist:
        raise HttpError(404, "Promoción no encontrada")


@api.put("/promociones/{promo_id}", response=PromocionOutSchema, auth=session_auth)
def actualizar_promocion(request, promo_id: int, payload: PromocionBaseSchema):
    try:
        promo = Promocion.objects.get(id=promo_id)
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except:
        raise HttpError(404, "Datos inválidos")

    promo.parrilla = parrilla
    promo.titulo = payload.titulo
    promo.descripcion = payload.descripcion
    promo.precio_promocional = payload.precio_promocional
    promo.fecha_inicio = payload.fecha_inicio
    promo.fecha_fin = payload.fecha_fin
    promo.is_active = payload.is_active
    promo.save()

    return promo


@api.delete("/promociones/{promo_id}", auth=session_auth)
def eliminar_promocion(request, promo_id: int):
    try:
        Promocion.objects.get(id=promo_id).delete()
    except Promocion.DoesNotExist:
        raise HttpError(404, "Promoción no encontrada")

    return {"success": True}
