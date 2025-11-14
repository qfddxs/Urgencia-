from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from hospital.models import Usuario


class Command(BaseCommand):
    help = 'Carga usuarios iniciales'

    def handle(self, *args, **options):
        # Crear usuarios solo si no existen
        usuarios = [
            ('María González', 'tens', 'tens123', 'TENS'),
            ('Dr. Juan Pérez', 'medico', 'medico123', 'Médico'),
            ('Ana Martínez', 'coordinador', 'coord123', 'Coordinador')
        ]
        
        for nombre, usuario, clave, rol in usuarios:
            if not Usuario.objects.filter(usuario=usuario).exists():
                Usuario.objects.create(
                    nombre=nombre,
                    usuario=usuario,
                    clave=make_password(clave),
                    rol=rol
                )
                self.stdout.write(f'Usuario creado: {usuario}')
            else:
                self.stdout.write(f'Usuario ya existe: {usuario}')

        self.stdout.write('Proceso completado')
