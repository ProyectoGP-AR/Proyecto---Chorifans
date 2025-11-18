from ninja import NinjaAPI

# Instancia principal de la API de ChoriFans
api = NinjaAPI(
    title="ChoriFans API",
    version="1.0.0",
    description="API para parrillas, reseñas, categorías, ubicaciones y promociones.",
)


@api.get("/ping")
def ping(request):
    """
    Endpoint simple de prueba.
    Sirve para verificar que la API está funcionando.
    GET /api/ping -> {"pong": true}
    """
    return {"pong": True}


# ==========================
#   CATEGORÍAS
# ==========================

from typing import List
from datetime import datetime
from ninja import Schema
from ninja.errors import HttpError
from django.utils import timezone

from apps.categorias.models import Categoria
from apps.ubicaciones.models import Ubicacion
from apps.parrillas.models import Parrilla
from django.contrib.auth.models import User
from apps.resenas.models import Resena
from apps.promociones.models import Promocion





class CategoriaBaseSchema(Schema):
    """
    Esquema base para crear/actualizar categorías.
    """
    nombre: str
    slug: str
    descripcion: str | None = None
    is_active: bool = True


class CategoriaOutSchema(CategoriaBaseSchema):
    """
    Esquema de salida (lo que devuelve la API).
    Incluye campos de solo lectura.
    """
    id: int
    created_at: datetime
    updated_at: datetime


@api.get("/categorias", response=List[CategoriaOutSchema])
def listar_categorias(request):
    """
    Lista todas las categorías.
    GET /api/categorias
    """
    qs = Categoria.objects.all().order_by("nombre")
    return list(qs)


@api.post("/categorias", response=CategoriaOutSchema)
def crear_categoria(request, payload: CategoriaBaseSchema):
    """
    Crea una nueva categoría.
    POST /api/categorias
    Body JSON:
    {
      "nombre": "Gourmet",
      "slug": "gourmet",
      "descripcion": "Parrillas con enfoque gourmet",
      "is_active": true
    }
    """
    categoria = Categoria.objects.create(
        nombre=payload.nombre,
        slug=payload.slug,
        descripcion=payload.descripcion,
        is_active=payload.is_active,
    )
    return categoria

@api.get("/categorias/{categoria_id}", response=CategoriaOutSchema)
def detalle_categoria(request, categoria_id: int):
    """
    Devuelve una categoría por ID.
    GET /api/categorias/{id}
    """
    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        # Si no existe la categoría, devolvemos un 404
        raise HttpError(404, "Categoría no encontrada")
    return categoria


@api.put("/categorias/{categoria_id}", response=CategoriaOutSchema)
def actualizar_categoria(request, categoria_id: int, payload: CategoriaBaseSchema):
    """
    Actualiza una categoría existente.
    PUT /api/categorias/{id}
    Body JSON similar al de creación.
    """
    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        raise HttpError(404, "Categoría no encontrada")

    # Actualizamos campos
    categoria.nombre = payload.nombre
    categoria.slug = payload.slug
    categoria.descripcion = payload.descripcion
    categoria.is_active = payload.is_active
    categoria.save()

    return categoria


@api.delete("/categorias/{categoria_id}")
def eliminar_categoria(request, categoria_id: int):
    """
    Elimina una categoría por ID.
    DELETE /api/categorias/{id}
    """
    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        raise HttpError(404, "Categoría no encontrada")

    categoria.delete()
    return {"success": True, "message": "Categoría eliminada correctamente"}


# ==========================
#   UBICACIONES
# ==========================


class UbicacionBaseSchema(Schema):
    """
    Esquema base para crear/actualizar ubicaciones.
    """
    nombre_ciudad: str
    nombre_barrio: str
    latitud: float | None = None
    longitud: float | None = None
    google_maps_url: str | None = None
    is_active: bool = True


class UbicacionOutSchema(UbicacionBaseSchema):
    """
    Esquema de salida para ubicaciones.
    Incluye campos de solo lectura.
    """
    id: int
    created_at: datetime
    updated_at: datetime


@api.get("/ubicaciones", response=List[UbicacionOutSchema])
def listar_ubicaciones(request):
    """
    Lista todas las ubicaciones.
    GET /api/ubicaciones
    """
    qs = Ubicacion.objects.all().order_by("nombre_ciudad", "nombre_barrio")
    return list(qs)


@api.post("/ubicaciones", response=UbicacionOutSchema)
def crear_ubicacion(request, payload: UbicacionBaseSchema):
    """
    Crea una nueva ubicación.
    POST /api/ubicaciones

    Body JSON ejemplo:
    {
      "nombre_ciudad": "Buenos Aires",
      "nombre_barrio": "Caballito",
      "latitud": -34.6201,
      "longitud": -58.4425,
      "google_maps_url": "https://maps.google.com/...",
      "is_active": true
    }
    """
    ubicacion = Ubicacion.objects.create(
        nombre_ciudad=payload.nombre_ciudad,
        nombre_barrio=payload.nombre_barrio,
        latitud=payload.latitud,
        longitud=payload.longitud,
        google_maps_url=payload.google_maps_url,
        is_active=payload.is_active,
    )
    return ubicacion

@api.get("/ubicaciones/{ubicacion_id}", response=UbicacionOutSchema)
def detalle_ubicacion(request, ubicacion_id: int):
    """
    Devuelve los datos de una ubicación por ID.
    GET /api/ubicaciones/{id}
    """
    try:
        ubicacion = Ubicacion.objects.get(id=ubicacion_id)
    except Ubicacion.DoesNotExist:
        raise HttpError(404, "Ubicación no encontrada")
    return ubicacion


@api.put("/ubicaciones/{ubicacion_id}", response=UbicacionOutSchema)
def actualizar_ubicacion(request, ubicacion_id: int, payload: UbicacionBaseSchema):
    """
    Actualiza una ubicación existente.
    PUT /api/ubicaciones/{id}
    """
    try:
        ubicacion = Ubicacion.objects.get(id=ubicacion_id)
    except Ubicacion.DoesNotExist:
        raise HttpError(404, "Ubicación no encontrada")

    ubicacion.nombre_ciudad = payload.nombre_ciudad
    ubicacion.nombre_barrio = payload.nombre_barrio
    ubicacion.latitud = payload.latitud
    ubicacion.longitud = payload.longitud
    ubicacion.google_maps_url = payload.google_maps_url
    ubicacion.is_active = payload.is_active
    ubicacion.save()

    return ubicacion


@api.delete("/ubicaciones/{ubicacion_id}")
def eliminar_ubicacion(request, ubicacion_id: int):
    """
    Elimina una ubicación por ID.
    DELETE /api/ubicaciones/{id}
    """
    try:
        ubicacion = Ubicacion.objects.get(id=ubicacion_id)
    except Ubicacion.DoesNotExist:
        raise HttpError(404, "Ubicación no encontrada")

    ubicacion.delete()
    return {"success": True, "message": "Ubicación eliminada correctamente"}



# ==========================
#   PARRILLAS
# ==========================

class ParrillaBaseSchema(Schema):
    """
    Esquema base para crear/actualizar parrillas.
    Nota: usamos IDs de categoria y ubicacion.
    """
    nombre: str
    descripcion: str | None = None
    direccion: str
    telefono: str | None = None
    sitio_web: str | None = None
    ubicacion_id: int
    categoria_id: int
    is_active: bool = True
    promedio_puntaje: float | None = None  # opcional, por ahora lo dejamos manual


class ParrillaOutSchema(ParrillaBaseSchema):
    """
    Esquema de salida para parrillas.
    Incluye id y timestamps.
    """
    id: int
    created_at: datetime
    updated_at: datetime



@api.get("/parrillas", response=List[ParrillaOutSchema])
def listar_parrillas(request):
    """
    Lista todas las parrillas.
    GET /api/parrillas
    """
    qs = Parrilla.objects.all().order_by("nombre")
    # Devolvemos el queryset tal cual; Ninja lo convierte según el schema
    return list(qs)


@api.post("/parrillas", response=ParrillaOutSchema)
def crear_parrilla(request, payload: ParrillaBaseSchema):
    """
    Crea una nueva parrilla.
    POST /api/parrillas

    Body JSON ejemplo:
    {
      "nombre": "El Chori de Caballito",
      "descripcion": "Parrilla de barrio con choripanes épicos",
      "direccion": "Av. Rivadavia 1234",
      "telefono": "11-1234-5678",
      "sitio_web": "https://instagram.com/elchoridecaballito",
      "ubicacion_id": 1,
      "categoria_id": 2,
      "is_active": true,
      "promedio_puntaje": null
    }
    """
    # Validamos que existan la categoría y la ubicación
    try:
        ubicacion = Ubicacion.objects.get(id=payload.ubicacion_id)
    except Ubicacion.DoesNotExist:
        raise HttpError(404, "Ubicación no encontrada")

    try:
        categoria = Categoria.objects.get(id=payload.categoria_id)
    except Categoria.DoesNotExist:
        raise HttpError(404, "Categoría no encontrada")

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

    return parrilla

@api.get("/parrillas/{parrilla_id}", response=ParrillaOutSchema)
def detalle_parrilla(request, parrilla_id: int):
    """
    Devuelve los datos de una parrilla por ID.
    GET /api/parrillas/{id}
    """
    try:
        parrilla = Parrilla.objects.get(id=parrilla_id)
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")
    return parrilla


@api.put("/parrillas/{parrilla_id}", response=ParrillaOutSchema)
def actualizar_parrilla(request, parrilla_id: int, payload: ParrillaBaseSchema):
    """
    Actualiza una parrilla existente.
    PUT /api/parrillas/{id}
    """
    try:
        parrilla = Parrilla.objects.get(id=parrilla_id)
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    # Validamos de nuevo categoria y ubicacion (por si cambian)
    try:
        ubicacion = Ubicacion.objects.get(id=payload.ubicacion_id)
    except Ubicacion.DoesNotExist:
        raise HttpError(404, "Ubicación no encontrada")

    try:
        categoria = Categoria.objects.get(id=payload.categoria_id)
    except Categoria.DoesNotExist:
        raise HttpError(404, "Categoría no encontrada")

    # Actualizamos campos
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

    return parrilla


@api.delete("/parrillas/{parrilla_id}")
def eliminar_parrilla(request, parrilla_id: int):
    """
    Elimina una parrilla por ID.
    DELETE /api/parrillas/{id}
    """
    parrilla = Parrilla.objects.get(id=parrilla_id)
    if parrilla is None:
        raise HttpError(404, "Parrilla no encontrada")

    parrilla.delete()
    return {"success": True, "message": "Parrilla eliminada correctamente"}



@api.get("/parrillas/por_ubicacion/{ubicacion_id}", response=List[ParrillaOutSchema])
def parrillas_por_ubicacion(request, ubicacion_id: int):
    """
    Lista parrillas filtradas por ubicación.
    GET /api/parrillas/por_ubicacion/{ubicacion_id}
    """
    try:
        ubicacion = Ubicacion.objects.get(id=ubicacion_id)
    except Ubicacion.DoesNotExist:
        raise HttpError(404, "Ubicación no encontrada")

    qs = Parrilla.objects.filter(ubicacion=ubicacion, is_active=True).order_by("nombre")
    return list(qs)


@api.get("/parrillas/por_categoria/{categoria_id}", response=List[ParrillaOutSchema])
def parrillas_por_categoria(request, categoria_id: int):
    """
    Lista parrillas filtradas por categoría.
    GET /api/parrillas/por_categoria/{categoria_id}
    """
    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        raise HttpError(404, "Categoría no encontrada")

    qs = Parrilla.objects.filter(categoria=categoria, is_active=True).order_by("nombre")
    return list(qs)

# ==========================
#   RESEÑAS
# ==========================

class ResenaBaseSchema(Schema):
    """
    Esquema base para crear/actualizar reseñas.
    Nota: usamos IDs de usuario y parrilla.
    """
    usuario_id: int
    parrilla_id: int
    puntaje: int        # 1 a 5 (choripanes)
    comentario: str
    is_active: bool = True


class ResenaOutSchema(ResenaBaseSchema):
    """
    Esquema de salida para reseñas.
    Incluye id y timestamps.
    """
    id: int
    created_at: datetime
    updated_at: datetime

@api.get("/resenas", response=List[ResenaOutSchema])
def listar_resenas(request):
    """
    Lista todas las reseñas.
    GET /api/resenas
    """
    qs = Resena.objects.all().order_by("-created_at")
    return list(qs)


@api.post("/resenas", response=ResenaOutSchema)
def crear_resena(request, payload: ResenaBaseSchema):
    """
    Crea una nueva reseña.
    POST /api/resenas

    Body JSON ejemplo:
    {
      "usuario_id": 1,
      "parrilla_id": 2,
      "puntaje": 4,
      "comentario": "Chori bien cargado, pan medio flojo pero zafa",
      "is_active": true
    }

    Importante: solo se permite UNA reseña por usuario/parrilla.
    """
    # Validamos usuario
    try:
        usuario = User.objects.get(id=payload.usuario_id)
    except User.DoesNotExist:
        raise HttpError(404, "Usuario no encontrado")

    # Validamos parrilla
    try:
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    # Verificamos si ya existe una reseña para ese usuario y parrilla
    if Resena.objects.filter(usuario=usuario, parrilla=parrilla).exists():
        raise HttpError(400, "Ya existe una reseña de este usuario para esta parrilla")

    # Creamos la reseña
    resena = Resena.objects.create(
        usuario=usuario,
        parrilla=parrilla,
        puntaje=payload.puntaje,
        comentario=payload.comentario,
        is_active=payload.is_active,
    )

    return resena


@api.get("/resenas/{resena_id}", response=ResenaOutSchema)
def detalle_resena(request, resena_id: int):
    """
    Devuelve una reseña por ID.
    GET /api/resenas/{id}
    """
    try:
        resena = Resena.objects.get(id=resena_id)
    except Resena.DoesNotExist:
        raise HttpError(404, "Reseña no encontrada")

    return resena


@api.put("/resenas/{resena_id}", response=ResenaOutSchema)
def actualizar_resena(request, resena_id: int, payload: ResenaBaseSchema):
    """
    Actualiza una reseña existente.
    PUT /api/resenas/{id}
    """
    try:
        resena = Resena.objects.get(id=resena_id)
    except Resena.DoesNotExist:
        raise HttpError(404, "Reseña no encontrada")

    # Validamos usuario y parrilla (por si los cambian)
    try:
        usuario = User.objects.get(id=payload.usuario_id)
    except User.DoesNotExist:
        raise HttpError(404, "Usuario no encontrado")

    try:
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    # Si se cambia usuario/parrilla, verificamos que no haya otra reseña igual
    existe_otra = Resena.objects.filter(
        usuario=usuario,
        parrilla=parrilla
    ).exclude(id=resena_id).exists()

    if existe_otra:
        raise HttpError(
            400,
            "Ya existe otra reseña de este usuario para esta parrilla",
        )

    # Actualizamos campos
    resena.usuario = usuario
    resena.parrilla = parrilla
    resena.puntaje = payload.puntaje
    resena.comentario = payload.comentario
    resena.is_active = payload.is_active
    resena.save()

    return resena


@api.delete("/resenas/{resena_id}")
def eliminar_resena(request, resena_id: int):
    """
    Elimina una reseña por ID.
    DELETE /api/resenas/{id}
    """
    try:
        resena = Resena.objects.get(id=resena_id)
    except Resena.DoesNotExist:
        raise HttpError(404, "Reseña no encontrada")

    resena.delete()
    return {"success": True, "message": "Reseña eliminada correctamente"}

# ==========================
#   PROMOCIONES
# ==========================

class PromocionBaseSchema(Schema):
    """
    Esquema base para crear/actualizar promociones.
    Usamos parrilla_id para relacionar.
    """
    parrilla_id: int
    titulo: str
    descripcion: str
    precio_promocional: float | None = None
    fecha_inicio: datetime
    fecha_fin: datetime
    is_active: bool = True


class PromocionOutSchema(PromocionBaseSchema):
    """
    Esquema de salida para promociones.
    Incluye id y timestamps.
    """
    id: int
    created_at: datetime
    updated_at: datetime

@api.get("/promociones", response=List[PromocionOutSchema])
def listar_promociones(request):
    """
    Lista todas las promociones.
    GET /api/promociones
    """
    qs = Promocion.objects.all().order_by("-fecha_inicio")
    return list(qs)


@api.post("/promociones", response=PromocionOutSchema)
def crear_promocion(request, payload: PromocionBaseSchema):
    """
    Crea una nueva promoción.
    POST /api/promociones

    Body JSON ejemplo:
    {
      "parrilla_id": 1,
      "titulo": "2x1 en choripán",
      "descripcion": "De lunes a viernes, 2x1 en chori con chimi casero.",
      "precio_promocional": 3000.00,
      "fecha_inicio": "2025-11-15T00:00:00",
      "fecha_fin": "2025-11-30T23:59:59",
      "is_active": true
    }
    """
    # Validamos que la parrilla exista
    try:
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    promo = Promocion.objects.create(
        parrilla=parrilla,
        titulo=payload.titulo,
        descripcion=payload.descripcion,
        precio_promocional=payload.precio_promocional,
        fecha_inicio=payload.fecha_inicio,
        fecha_fin=payload.fecha_fin,
        is_active=payload.is_active,
    )

    return promo


@api.get("/promociones/{promo_id}", response=PromocionOutSchema)
def detalle_promocion(request, promo_id: int):
    """
    Devuelve una promoción por ID.
    GET /api/promociones/{id}
    """
    try:
        promo = Promocion.objects.get(id=promo_id)
    except Promocion.DoesNotExist:
        raise HttpError(404, "Promoción no encontrada")

    return promo


@api.put("/promociones/{promo_id}", response=PromocionOutSchema)
def actualizar_promocion(request, promo_id: int, payload: PromocionBaseSchema):
    """
    Actualiza una promoción existente.
    PUT /api/promociones/{id}
    """
    try:
        promo = Promocion.objects.get(id=promo_id)
    except Promocion.DoesNotExist:
        raise HttpError(404, "Promoción no encontrada")

    # Validar parrilla (por si se cambia)
    try:
        parrilla = Parrilla.objects.get(id=payload.parrilla_id)
    except Parrilla.DoesNotExist:
        raise HttpError(404, "Parrilla no encontrada")

    # Actualizar campos
    promo.parrilla = parrilla
    promo.titulo = payload.titulo
    promo.descripcion = payload.descripcion
    promo.precio_promocional = payload.precio_promocional
    promo.fecha_inicio = payload.fecha_inicio
    promo.fecha_fin = payload.fecha_fin
    promo.is_active = payload.is_active
    promo.save()

    return promo


@api.delete("/promociones/{promo_id}")
def eliminar_promocion(request, promo_id: int):
    """
    Elimina una promoción por ID.
    DELETE /api/promociones/{id}
    """
    try:
        promo = Promocion.objects.get(id=promo_id)
    except Promocion.DoesNotExist:
        raise HttpError(404, "Promoción no encontrada")

    promo.delete()
    return {"success": True, "message": "Promoción eliminada correctamente"}

@api.get("/promociones/activas", response=List[PromocionOutSchema])
def listar_promociones_activas(request):
    """
    Lista promociones activas a la fecha actual.
    GET /api/promociones/activas

    Criterio:
    - is_active = True
    - fecha_inicio <= hoy
    - fecha_fin >= hoy
    """
    hoy = timezone.now().date()
    qs = Promocion.objects.filter(
        is_active=True,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy,
    ).order_by("fecha_fin")
    return list(qs)
