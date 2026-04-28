from datetime import date, datetime
from typing import List, Optional

from django.contrib.auth.models import User
from django.utils import timezone

from ninja import NinjaAPI, Query, Schema
from ninja.errors import HttpError
from ninja.security import SessionAuth

from apps.api.pagination import paginate_queryset
from apps.api.services.chatbot_service import get_chori_bot_response
from apps.categorias.models import Categoria
from apps.parrillas.models import Parrilla
from apps.promociones.models import Promocion
from apps.resenas.models import Resena
from apps.ubicaciones.models import Ubicacion


api = NinjaAPI(
    title="ChoriFans API",
    version="1.0.0",
    description="API oficial del proyecto ChoriFans.",
)

session_auth = SessionAuth()


def schema_dump(schema_obj):
    """
    Compatibilidad entre Pydantic v1 y v2.
    """
    if hasattr(schema_obj, "model_dump"):
        return schema_obj.model_dump()
    return schema_obj.dict()


def convert_parrilla(parrilla: Parrilla):
    return {
        "id": parrilla.id,
        "nombre": parrilla.nombre,
        "descripcion": parrilla.descripcion,
        "direccion": parrilla.direccion,
        "telefono": parrilla.telefono,
        "sitio_web": parrilla.sitio_web,
        "is_active": parrilla.is_active,
        "promedio_puntaje": parrilla.promedio_puntaje,
        "created_at": parrilla.created_at,
        "updated_at": parrilla.updated_at,
        "categoria": {
            "id": parrilla.categoria.id,
            "nombre": parrilla.categoria.nombre,
        },
        "ubicacion": {
            "id": parrilla.ubicacion.id,
            "nombre_ciudad": parrilla.ubicacion.nombre_ciudad,
            "nombre_barrio": parrilla.ubicacion.nombre_barrio,
        },
    }


@api.get("/ping")
def ping(request):
    return {"pong": True}


class PaginatedResponse(Schema):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    results: list


class CategoriaSimple(Schema):
    id: int
    nombre: str


class UbicacionSimple(Schema):
    id: int
    nombre_ciudad: str
    nombre_barrio: str


class CategoriaBaseSchema(Schema):
    nombre: str
    slug: str
    descripcion: Optional[str] = None
    is_active: bool = True


class CategoriaOutSchema(CategoriaBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class UbicacionBaseSchema(Schema):
    nombre_ciudad: str
    nombre_barrio: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    google_maps_url: Optional[str] = None
    is_active: bool = True


class UbicacionOutSchema(UbicacionBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class ParrillaBaseSchema(Schema):
    nombre: str
    descripcion: Optional[str] = None
    direccion: str
    telefono: Optional[str] = None
    sitio_web: Optional[str] = None
    ubicacion_id: int
    categoria_id: int
    is_active: bool = True
    promedio_puntaje: Optional[float] = None


class ParrillaOutSchema(Schema):
    id: int
    nombre: str
    descripcion: Optional[str]
    direccion: str
    telefono: Optional[str]
    sitio_web: Optional[str]
    is_active: bool
    promedio_puntaje: Optional[float]
    created_at: datetime
    updated_at: datetime
    categoria: CategoriaSimple
    ubicacion: UbicacionSimple


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


class PromocionBaseSchema(Schema):
    parrilla_id: int
    titulo: str
    descripcion: str
    precio_promocional: Optional[float] = None
    fecha_inicio: date
    fecha_fin: date
    is_active: bool = True


class PromocionOutSchema(PromocionBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class ChatbotContextSchema(Schema):
    currentPath: Optional[str] = None
    currentView: Optional[str] = None
    isAuthenticated: Optional[bool] = None
    username: Optional[str] = None
    pageTitle: Optional[str] = None


class ChatbotRequestSchema(Schema):
    message: str
    context: Optional[ChatbotContextSchema] = None


class ChatbotResponseSchema(Schema):
    reply: str


@api.post("/chatbot", response=ChatbotResponseSchema)
def chori_bot(request, payload: ChatbotRequestSchema):
    mensaje = (payload.message or "").strip()

    if not mensaje:
        raise HttpError(400, "El mensaje no puede estar vacío")

    contexto = schema_dump(payload.context) if payload.context else {}

    if request.user.is_authenticated:
        contexto["django_user_authenticated"] = True
        contexto["django_username"] = request.user.username
    else:
        contexto["django_user_authenticated"] = False
        contexto["django_username"] = None

    try:
        respuesta = get_chori_bot_response(mensaje, contexto)
    except Exception as e:
        raise HttpError(500, f"Error al generar respuesta del chatbot: {str(e)}")

    return {"reply": respuesta}


# ============================================================
# CATEGORÍAS
# ============================================================

@api.get("/categorias", response=List[CategoriaOutSchema])
def listar_categorias(request):
    return list(Categoria.objects.all().order_by("nombre"))


@api.post("/categorias", response=CategoriaOutSchema, auth=session_auth)
def crear_categoria(request, payload: CategoriaBaseSchema):
    return Categoria.objects.create(**schema_dump(payload))


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

    for key, value in schema_dump(payload).items():
        setattr(categoria, key, value)

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
# UBICACIONES
# ============================================================

@api.get("/ubicaciones", response=List[UbicacionOutSchema])
def listar_ubicaciones(request):
    return list(Ubicacion.objects.all().order_by("nombre_ciudad", "nombre_barrio"))


@api.post("/ubicaciones", response=UbicacionOutSchema, auth=session_auth)
def crear_ubicacion(request, payload: UbicacionBaseSchema):
    return Ubicacion.objects.create(**schema_dump(payload))


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

    for key, value in schema_dump(payload).items():
        setattr(ubicacion, key, value)

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
# PARRILLAS
# ============================================================

@api.get("/parrillas", response=List[ParrillaOutSchema])
def listar_parrillas(
    request,
    categoria_id: Optional[int] = None,
    ubicacion_id: Optional[int] = None,
    min_puntaje: Optional[float] = None,
):
    qs = (
        Parrilla.objects
        .filter(is_active=True)
        .select_related("categoria", "ubicacion")
        .order_by("nombre")
    )

    if categoria_id is not None:
        qs = qs.filter(categoria_id=categoria_id)

    if ubicacion_id is not None:
        qs = qs.filter(ubicacion_id=ubicacion_id)

    if min_puntaje is not None:
        qs = qs.filter(promedio_puntaje__gte=min_puntaje)

    return [convert_parrilla(parrilla) for parrilla in qs]


@api.get("/parrillas/paginadas", response=PaginatedResponse)
def listar_parrillas_paginadas(
    request,
    page: int = Query(1),
    page_size: int = Query(10),
):
    qs = (
        Parrilla.objects
        .filter(is_active=True)
        .select_related("categoria", "ubicacion")
        .order_by("nombre")
    )
    return paginate_queryset(qs, page, page_size, converter=convert_parrilla)


@api.post("/parrillas", response=ParrillaOutSchema, auth=session_auth)
def crear_parrilla(request, payload: ParrillaBaseSchema):
    try:
        ubicacion = Ubicacion.objects.get(id=payload.ubicacion_id)
        categoria = Categoria.objects.get(id=payload.categoria_id)
    except (Ubicacion.DoesNotExist, Categoria.DoesNotExist):
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
        parrilla = (
            Parrilla.objects
            .select_related("categoria", "ubicacion")
            .get(id=parrilla_id)
        )
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
    except (Ubicacion.DoesNotExist, Categoria.DoesNotExist):
        raise HttpError(404, "Categoría o ubicación inválida")

    parrilla.nombre = payload.nombre
    parrilla.descripcion = payload.descripcion
    parrilla.direccion = payload.direccion
    parrilla.telefono = payload.telefono
    parrilla.sitio_web = payload.sitio_web
    parrilla.ubicacion = ubicacion
    parrilla.categoria = categoria
    parrilla.is_active = payload.is_active
    parrilla.promedio_puntaje = payload.promedio_puntaje
    parrilla.save()

    return convert_parrilla(parrilla)


@api.delete("/parrillas/{parrilla_id}", auth=session_auth)
def eliminar_parrilla(request, parrilla_id: int):
    try:
        Parrilla.objects.get(id=parrilla_id).delete()
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    return {"success": True}


# ============================================================
# RESEÑAS
# ============================================================

@api.get("/resenas", response=List[ResenaOutSchema])
def listar_resenas(request):
    return list(Resena.objects.all().order_by("-created_at"))


@api.post("/resenas", response=ResenaOutSchema, auth=session_auth)
def crear_resena(request, payload: ResenaBaseSchema):
    try:
        usuario = User.objects.get(id=payload.usuario_id)
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except (User.DoesNotExist, Parrilla.DoesNotExist):
        raise HttpError(404, "Usuario o parrilla no encontrada")

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
    except (Resena.DoesNotExist, User.DoesNotExist, Parrilla.DoesNotExist):
        raise HttpError(404, "Datos inválidos")

    existe_otra = (
        Resena.objects
        .filter(usuario=usuario, parrilla=parrilla)
        .exclude(id=resena_id)
        .exists()
    )
    if existe_otra:
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
# PROMOCIONES
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
        promocion = Promocion.objects.get(id=promo_id)
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except (Promocion.DoesNotExist, Parrilla.DoesNotExist):
        raise HttpError(404, "Datos inválidos")

    promocion.parrilla = parrilla
    promocion.titulo = payload.titulo
    promocion.descripcion = payload.descripcion
    promocion.precio_promocional = payload.precio_promocional
    promocion.fecha_inicio = payload.fecha_inicio
    promocion.fecha_fin = payload.fecha_fin
    promocion.is_active = payload.is_active
    promocion.save()

    return promocion


@api.delete("/promociones/{promo_id}", auth=session_auth)
def eliminar_promocion(request, promo_id: int):
    try:
        Promocion.objects.get(id=promo_id).delete()
    except Promocion.DoesNotExist:
        raise HttpError(404, "Promoción no encontrada")

    return {"success": True}