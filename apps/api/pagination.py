from math import ceil

def paginate_queryset(queryset, page: int = 1, page_size: int = 10, converter=None):
    """
    Helper general de paginación con soporte opcional para 'converter'.

    Parámetros:
    - queryset: QuerySet a paginar
    - page: número de página
    - page_size: cantidad por página
    - converter: función opcional que transforma cada objeto (ej: convert_parrilla)

    Retorna:
    - Diccionario compatible con PaginatedResponse
    """

    total = queryset.count()
    total_pages = ceil(total / page_size)

    start = (page - 1) * page_size
    end = start + page_size

    objects = queryset[start:end]

    # Convertimos los objetos si se pasa un converter
    if converter:
        objects = [converter(obj) for obj in objects]
    else:
        objects = list(objects)

    return {
        "page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": total_pages,
        "results": objects,
    }
