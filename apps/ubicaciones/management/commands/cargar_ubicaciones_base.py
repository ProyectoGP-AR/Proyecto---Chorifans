from django.core.management.base import BaseCommand
from apps.ubicaciones.models import Ubicacion


CABA_BARRIOS = [
    "Agronomía",
    "Almagro",
    "Balvanera",
    "Barracas",
    "Belgrano",
    "Boedo",
    "Caballito",
    "Chacarita",
    "Coghlan",
    "Colegiales",
    "Constitución",
    "Flores",
    "Floresta",
    "La Boca",
    "La Paternal",
    "Liniers",
    "Mataderos",
    "Monte Castro",
    "Monserrat",
    "Nueva Pompeya",
    "Núñez",
    "Palermo",
    "Parque Avellaneda",
    "Parque Chacabuco",
    "Parque Chas",
    "Parque Patricios",
    "Puerto Madero",
    "Recoleta",
    "Retiro",
    "Saavedra",
    "San Cristóbal",
    "San Nicolás",
    "San Telmo",
    "Vélez Sarsfield",
    "Versalles",
    "Villa Crespo",
    "Villa del Parque",
    "Villa Devoto",
    "Villa General Mitre",
    "Villa Lugano",
    "Villa Luro",
    "Villa Ortúzar",
    "Villa Pueyrredón",
    "Villa Real",
    "Villa Riachuelo",
    "Villa Santa Rita",
    "Villa Soldati",
    "Villa Urquiza",
]

# Criterio habitual de cordones.
# Como tu modelo no tiene campo "cordón", solo cargamos el municipio una vez.
PRIMER_CORDON = [
    "Avellaneda",
    "General San Martín",
    "La Matanza",
    "Lanús",
    "Lomas de Zamora",
    "Morón",
    "San Isidro",
    "Tres de Febrero",
    "Vicente López",
]

SEGUNDO_CORDON = [
    "Almirante Brown",
    "Berazategui",
    "Esteban Echeverría",
    "Ezeiza",
    "Florencio Varela",
    "Hurlingham",
    "Ituzaingó",
    "José C. Paz",
    "Malvinas Argentinas",
    "Merlo",
    "Moreno",
    "Quilmes",
    "San Fernando",
    "San Miguel",
    "Tigre",
]

TERCER_CORDON = [
    "Escobar",
    "General Rodríguez",
    "Marcos Paz",
    "Pilar",
    "Presidente Perón",
    "San Vicente",
]


class Command(BaseCommand):
    help = "Carga ubicaciones base de CABA y municipios del conurbano bonaerense."

    def handle(self, *args, **options):
        creadas = 0
        existentes = 0

        for barrio in CABA_BARRIOS:
            _, created = Ubicacion.objects.get_or_create(
                nombre_ciudad="Ciudad Autónoma de Buenos Aires",
                nombre_barrio=barrio,
                defaults={
                    "is_active": True,
                },
            )
            if created:
                creadas += 1
            else:
                existentes += 1

        municipios = []
        municipios.extend(PRIMER_CORDON)
        municipios.extend(SEGUNDO_CORDON)
        municipios.extend(TERCER_CORDON)

        # Evitamos duplicados por si algún municipio aparece en más de un criterio.
        municipios_unicos = sorted(set(municipios))

        for municipio in municipios_unicos:
            _, created = Ubicacion.objects.get_or_create(
                nombre_ciudad="Provincia de Buenos Aires",
                nombre_barrio=municipio,
                defaults={
                    "is_active": True,
                },
            )
            if created:
                creadas += 1
            else:
                existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Proceso terminado. Creadas: {creadas} | Ya existentes: {existentes}"
            )
        )