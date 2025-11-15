from django.core.management.base import BaseCommand
from hospital.models import Hospital

class Command(BaseCommand):
    help = 'Carga hospitales de prueba en la base de datos'

    def handle(self, *args, **kwargs):
        # Verificar si ya existen hospitales
        if Hospital.objects.exists():
            self.stdout.write(self.style.WARNING('Ya existen hospitales en la base de datos.'))
            respuesta = input('¿Desea eliminarlos y crear nuevos? (s/n): ')
            if respuesta.lower() != 's':
                self.stdout.write(self.style.SUCCESS('Operación cancelada.'))
                return
            Hospital.objects.all().delete()
            self.stdout.write(self.style.WARNING('Hospitales anteriores eliminados.'))

        # Crear hospitales de prueba (todos con 50 camas)
        hospitales = [
            {
                'nombre': 'Hospital Rancagua',
                'camas_totales': 50,
                'camas_ocupadas': 0
            },
            {
                'nombre': 'Hospital San Fernando',
                'camas_totales': 50,
                'camas_ocupadas': 0
            },
            {
                'nombre': 'Hospital Santa Cruz',
                'camas_totales': 50,
                'camas_ocupadas': 0
            },
        ]

        for hospital_data in hospitales:
            hospital = Hospital.objects.create(**hospital_data)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Hospital creado: {hospital.nombre} ({hospital.camas_ocupadas}/{hospital.camas_totales} camas)')
            )

        self.stdout.write(self.style.SUCCESS(f'\n¡Éxito! Se crearon {len(hospitales)} hospitales.'))
