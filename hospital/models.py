from django.db import models
from django.utils import timezone

# Modelo para almacenar los datos de los pacientes
class Paciente(models.Model):
    GENERO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]
    PREVISION_CHOICES = [
        ('Fonasa', 'Fonasa'),
        ('Isapre', 'Isapre'),
        ('Particular', 'Particular'),
    ]
    FUNCIONALIDAD_CHOICES = [
        ('Autovalente', 'Autovalente'),
        ('Dependencia Leve', 'Dependencia Leve'),
        ('Dependencia Severa', 'Dependencia Severa'),
    ]

    rut = models.CharField(max_length=12, primary_key=True, unique=True, help_text="RUT sin puntos y con guión")
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, blank=True, null=True)
    prevision = models.CharField(max_length=20, choices=PREVISION_CHOICES, blank=True, null=True)
    comorbilidades = models.CharField(max_length=200, blank=True, null=True)
    funcionalidad = models.CharField(max_length=50, choices=FUNCIONALIDAD_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo para almacenar las derivaciones
class Derivacion(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aceptada', 'Aceptada'),
        ('Rechazada', 'Rechazada'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    motivo = models.TextField()
    prestacion_requerida = models.CharField(max_length=100)
    estado_paciente = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)
    hospital_receptor = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Derivación de {self.paciente.nombre} a {self.hospital_receptor}"
