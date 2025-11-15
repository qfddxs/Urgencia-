from django.db import models
from django.utils import timezone


class Usuario(models.Model):
    ROL_CHOICES = [
        ('TENS', 'TENS'),
        ('Médico', 'Médico'),
        ('Coordinador', 'Coordinador'),
    ]
    
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    usuario = models.CharField(max_length=100, unique=True)
    clave = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    
    class Meta:
        db_table = 'USUARIO'
    
    def __str__(self):
        return f"{self.nombre} ({self.rol})"


class Paciente(models.Model):
    id_paciente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=12, unique=True)
    edad = models.IntegerField(null=True, blank=True)
    genero = models.CharField(max_length=50, null=True, blank=True)
    prevision = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        db_table = 'PACIENTE'
    
    def __str__(self):
        return self.nombre


class FichaPaciente(models.Model):
    id_ficha = models.AutoField(primary_key=True)
    id_paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, db_column='id_paciente')
    comorbilidades = models.TextField(null=True, blank=True)
    funcionalidad = models.CharField(max_length=255, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'FICHA_PACIENTE'
    
    def __str__(self):
        return f"Ficha de {self.id_paciente.nombre}"


class Hospital(models.Model):
    id_hospital = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    camas_totales = models.IntegerField(default=0)
    camas_ocupadas = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'HOSPITAL'
    
    def __str__(self):
        return self.nombre
    
    def tiene_camas_disponibles(self):
        """Verifica si hay camas disponibles"""
        return self.camas_ocupadas < self.camas_totales
    
    def camas_disponibles(self):
        """Retorna el número de camas disponibles"""
        return max(0, self.camas_totales - self.camas_ocupadas)
    
    def ocupar_cama(self):
        """Ocupa una cama si hay disponibilidad"""
        if self.tiene_camas_disponibles():
            self.camas_ocupadas += 1
            self.save()
            return True
        return False
    
    def liberar_cama(self):
        """Libera una cama ocupada"""
        if self.camas_ocupadas > 0:
            self.camas_ocupadas -= 1
            self.save()
            return True
        return False
    
    def porcentaje_ocupacion(self):
        """Calcula el porcentaje de ocupación"""
        if self.camas_totales == 0:
            return 0
        return round((self.camas_ocupadas / self.camas_totales) * 100, 1)


class Derivacion(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aceptada', 'Aceptada'),
        ('Rechazada', 'Rechazada'),
        ('En revisión', 'En revisión'),
    ]
    
    id_derivacion = models.AutoField(primary_key=True)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.RESTRICT, db_column='id_paciente')
    id_hospital = models.ForeignKey(Hospital, on_delete=models.RESTRICT, db_column='id_hospital')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, db_column='id_usuario')
    motivo = models.CharField(max_length=255, null=True, blank=True)
    prestacion = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    fecha = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'DERIVACION'
    
    def __str__(self):
        return f"Derivación de {self.id_paciente.nombre} a {self.id_hospital.nombre}"
