from time import sleep
from urllib.parse import quote_plus

import requests
from django.core.management.base import BaseCommand

from apps.ubicaciones.models import Ubicacion


class Command(BaseCommand):
    help = (
        "Busca y guarda latitud/longitud para las ubicaciones cargadas "
        "usando Nominatim (OpenStreetMap)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Sobrescribe coordenadas aunque la ubicación ya tenga latitud/longitud.",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=1.2,
            help="Segundos de espera entre consultas para no saturar el servicio.",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=15,
            help="Timeout de cada request HTTP.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Procesa solo N ubicaciones (0 = todas).",
        )

    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        sleep_seconds = options["sleep"]
        timeout = options["timeout"]
        limit = options["limit"]

        qs = Ubicacion.objects.all().order_by("nombre_ciudad", "nombre_barrio")

        if not overwrite:
            qs = qs.filter(latitud__isnull=True, longitud__isnull=True)

        if limit and limit > 0:
            qs = qs[:limit]

        total = qs.count() if hasattr(qs, "count") else len(qs)

        if total == 0:
            self.stdout.write(
                self.style.WARNING("No hay ubicaciones pendientes para geocodificar.")
            )
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Se procesarán {total} ubicaciones "
                f"(overwrite={'sí' if overwrite else 'no'})."
            )
        )

        headers = {
            "User-Agent": "ChoriFans/1.0 (geocodificacion ubicaciones Django)"
        }

        ok = 0
        fail = 0

        for idx, ubicacion in enumerate(qs, start=1):
            self.stdout.write(
                f"\n[{idx}/{total}] Procesando: "
                f"{ubicacion.nombre_barrio} - {ubicacion.nombre_ciudad}"
            )

            consulta = self._resolver_consulta(ubicacion)
            if not consulta:
                self.stdout.write(
                    self.style.WARNING("  No pude construir una consulta válida.")
                )
                fail += 1
                continue

            resultado = self._buscar_coordenadas(
                consulta=consulta,
                headers=headers,
                timeout=timeout,
            )

            if resultado is None:
                self.stdout.write(
                    self.style.WARNING("  No se encontraron coordenadas.")
                )
                fail += 1
                sleep(sleep_seconds)
                continue

            lat, lon, display_name = resultado
            ubicacion.latitud = lat
            ubicacion.longitud = lon

            if not ubicacion.google_maps_url:
                ubicacion.google_maps_url = (
                    "https://www.google.com/maps/search/?api=1&query="
                    f"{quote_plus(f'{lat},{lon}')}"
                )

            ubicacion.save(
                update_fields=[
                    "latitud",
                    "longitud",
                    "google_maps_url",
                    "updated_at",
                ]
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"  OK -> lat={lat}, lon={lon} | {display_name}"
                )
            )
            ok += 1
            sleep(sleep_seconds)

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"Geocodificadas correctamente: {ok}"))
        self.stdout.write(self.style.WARNING(f"Sin resolver: {fail}"))

    def _resolver_consulta(self, ubicacion: Ubicacion) -> str:
        barrio = (ubicacion.nombre_barrio or "").strip()
        ciudad = (ubicacion.nombre_ciudad or "").strip()

        ciudad_norm = ciudad.lower()

        # CABA
        if "autónoma de buenos aires" in ciudad_norm or ciudad_norm == "caba":
            return f"{barrio}, Ciudad Autónoma de Buenos Aires, Argentina"

        # Provincia / conurbano
        if "provincia de buenos aires" in ciudad_norm:
            return f"{barrio}, Buenos Aires, Argentina"

        # Caso general
        if barrio and ciudad:
            return f"{barrio}, {ciudad}, Argentina"

        if barrio:
            return f"{barrio}, Argentina"

        return ""

    def _buscar_coordenadas(self, consulta: str, headers: dict, timeout: int):
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": consulta,
            "format": "jsonv2",
            "limit": 1,
            "countrycodes": "ar",
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"  Error HTTP: {exc}"))
            return None

        if not data:
            return None

        item = data[0]

        try:
            lat = float(item["lat"])
            lon = float(item["lon"])
            display_name = item.get("display_name", consulta)
            return lat, lon, display_name
        except Exception:
            return None