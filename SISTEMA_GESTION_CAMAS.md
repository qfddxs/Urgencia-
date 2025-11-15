# Sistema de Gestión Automática de Camas

## 🎯 Objetivo
Cuando el coordinador acepta una derivación, automáticamente se debe:
1. Descontar una cama del hospital receptor
2. Actualizar el estado en la base de datos
3. Validar que haya camas disponibles antes de aceptar

## 🏗️ Arquitectura Propuesta

### Flujo del Sistema:
```
Médico registra derivación
    ↓
Estado: "Pendiente"
    ↓
Coordinador revisa
    ↓
¿Acepta? → SÍ → Verificar camas disponibles
    ↓              ↓
    NO         ¿Hay camas?
    ↓              ↓
Rechazar       SÍ → Descontar 1 cama
               ↓    Estado: "Aceptada"
               NO → Mostrar error
                    "Hospital sin capacidad"
```

## 💾 Estructura de Base de Datos Actual

Ya tienes la estructura correcta en el modelo `Hospital`:
```python
class Hospital(models.Model):
    id_hospital = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    camas_totales = models.IntegerField(default=0)
    camas_ocupadas = models.IntegerField(default=0)
```

## ✅ Implementación Recomendada

### 1. Método en el Modelo Hospital
Agregar métodos para gestionar camas de forma segura:

```python
class Hospital(models.Model):
    # ... campos existentes ...
    
    def tiene_camas_disponibles(self):
        """Verifica si hay camas disponibles"""
        return self.camas_ocupadas < self.camas_totales
    
    def camas_disponibles(self):
        """Retorna el número de camas disponibles"""
        return self.camas_totales - self.camas_ocupadas
    
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
```

### 2. Actualizar la Vista del Coordinador

Modificar `gestionar_derivacion` para manejar camas:

```python
def gestionar_derivacion(request, derivacion_id, nuevo_estado):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    if request.session.get('usuario_rol') != 'Coordinador':
        return redirect('index')
    
    derivacion = get_object_or_404(Derivacion, id_derivacion=derivacion_id)
    estado_anterior = derivacion.estado
    
    # Si se está aceptando la derivación
    if nuevo_estado == 'Aceptada' and estado_anterior != 'Aceptada':
        hospital = derivacion.id_hospital
        
        # Verificar disponibilidad de camas
        if not hospital.tiene_camas_disponibles():
            messages.error(request, 
                f'No se puede aceptar: {hospital.nombre} no tiene camas disponibles. '
                f'Ocupación: {hospital.camas_ocupadas}/{hospital.camas_totales}')
            return redirect('coord_derivaciones')
        
        # Ocupar una cama
        if hospital.ocupar_cama():
            derivacion.estado = nuevo_estado
            derivacion.save()
            messages.success(request, 
                f'Derivación aceptada. Cama asignada en {hospital.nombre}. '
                f'Disponibles: {hospital.camas_disponibles()}/{hospital.camas_totales}')
        else:
            messages.error(request, 'Error al asignar cama.')
            return redirect('coord_derivaciones')
    
    # Si se está rechazando una derivación previamente aceptada
    elif nuevo_estado == 'Rechazada' and estado_anterior == 'Aceptada':
        hospital = derivacion.id_hospital
        hospital.liberar_cama()
        derivacion.estado = nuevo_estado
        derivacion.save()
        messages.info(request, f'Derivación rechazada. Cama liberada en {hospital.nombre}.')
    
    # Otros cambios de estado
    else:
        derivacion.estado = nuevo_estado
        derivacion.save()
        messages.success(request, f'Estado actualizado a: {nuevo_estado}')
    
    return redirect('coord_derivaciones')
```

### 3. Agregar Campo de Fecha de Alta (Opcional pero Recomendado)

Para liberar camas cuando un paciente es dado de alta:

```python
# En models.py - Agregar a Derivacion
class Derivacion(models.Model):
    # ... campos existentes ...
    fecha_alta = models.DateTimeField(null=True, blank=True)
    
    def dar_alta(self):
        """Registra el alta del paciente y libera la cama"""
        if self.estado == 'Aceptada' and not self.fecha_alta:
            self.fecha_alta = timezone.now()
            self.estado = 'Completada'  # Nuevo estado
            self.id_hospital.liberar_cama()
            self.save()
            return True
        return False
```

## 🔒 Consideraciones de Seguridad

### 1. Transacciones Atómicas
Para evitar condiciones de carrera (race conditions):

```python
from django.db import transaction

@transaction.atomic
def gestionar_derivacion(request, derivacion_id, nuevo_estado):
    # Bloquear el registro del hospital para evitar conflictos
    derivacion = Derivacion.objects.select_for_update().get(id_derivacion=derivacion_id)
    hospital = Hospital.objects.select_for_update().get(id_hospital=derivacion.id_hospital.id_hospital)
    
    # ... resto del código ...
```

### 2. Validación en el Modelo
Agregar validación para evitar valores negativos:

```python
from django.core.exceptions import ValidationError

class Hospital(models.Model):
    # ... campos existentes ...
    
    def clean(self):
        if self.camas_ocupadas < 0:
            raise ValidationError('Las camas ocupadas no pueden ser negativas.')
        if self.camas_ocupadas > self.camas_totales:
            raise ValidationError('Las camas ocupadas no pueden exceder el total.')
```

## 📊 Sincronización con Base de Datos

### Opción 1: Actualización en Tiempo Real (Recomendada)
- Cada acción (aceptar/rechazar) actualiza inmediatamente la BD
- Usa transacciones atómicas para consistencia
- Ya implementado en el código de arriba

### Opción 2: Actualización por Lotes (No recomendada para este caso)
- Útil solo si tienes miles de operaciones simultáneas
- Más complejo de implementar

### Opción 3: Triggers de Base de Datos (Avanzado)
```sql
-- Trigger en MySQL para validar
DELIMITER $$
CREATE TRIGGER validar_camas_antes_actualizar
BEFORE UPDATE ON HOSPITAL
FOR EACH ROW
BEGIN
    IF NEW.camas_ocupadas < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Camas ocupadas no puede ser negativo';
    END IF;
    IF NEW.camas_ocupadas > NEW.camas_totales THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Camas ocupadas excede el total';
    END IF;
END$$
DELIMITER ;
```

## 🎨 Mejoras en la Interfaz

### 1. Mostrar Disponibilidad en Tiempo Real
En `coord_derivaciones.html`:

```html
<td>
    {{ derivacion.id_hospital.nombre }}
    <br>
    <small class="text-muted">
        Disponibles: 
        <span class="badge bg-{% if derivacion.id_hospital.camas_disponibles > 5 %}success{% elif derivacion.id_hospital.camas_disponibles > 0 %}warning{% else %}danger{% endif %}">
            {{ derivacion.id_hospital.camas_disponibles }}
        </span>
    </small>
</td>
```

### 2. Deshabilitar Botón "Aceptar" si No Hay Camas
```html
{% if derivacion.id_hospital.tiene_camas_disponibles %}
    <a href="{% url 'gestionar_derivacion' derivacion.id_derivacion 'Aceptada' %}" 
       class="btn btn-sm btn-success">
        <i class="fa fa-check"></i> Aceptar
    </a>
{% else %}
    <button class="btn btn-sm btn-secondary" disabled title="Sin camas disponibles">
        <i class="fa fa-ban"></i> Sin Capacidad
    </button>
{% endif %}
```

## 📈 Reportes y Auditoría

### Crear un Modelo de Historial (Recomendado)
```python
class HistorialCamas(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    derivacion = models.ForeignKey(Derivacion, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=20)  # 'OCUPAR' o 'LIBERAR'
    camas_antes = models.IntegerField()
    camas_despues = models.IntegerField()
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'HISTORIAL_CAMAS'
```

## 🧪 Testing

### Casos de Prueba Importantes:
1. ✅ Aceptar derivación con camas disponibles
2. ✅ Intentar aceptar sin camas disponibles
3. ✅ Rechazar derivación aceptada (liberar cama)
4. ✅ Múltiples coordinadores aceptando simultáneamente
5. ✅ Validar que camas_ocupadas nunca sea negativo
6. ✅ Validar que camas_ocupadas nunca exceda camas_totales

## 🚀 Orden de Implementación

1. **Paso 1**: Agregar métodos al modelo Hospital
2. **Paso 2**: Actualizar la vista gestionar_derivacion
3. **Paso 3**: Instalar django messages: `pip install django-contrib-messages`
4. **Paso 4**: Actualizar templates para mostrar disponibilidad
5. **Paso 5**: Agregar transacciones atómicas
6. **Paso 6**: Crear modelo de historial (opcional)
7. **Paso 7**: Testing exhaustivo

## 📝 Configuración Inicial de Camas

Para establecer 50 camas por hospital:

```python
# En manage.py shell o en cargar_hospitales.py
from hospital.models import Hospital

Hospital.objects.all().update(camas_totales=50, camas_ocupadas=0)
```

O actualizar el comando cargar_hospitales:
```python
hospitales = [
    {'nombre': 'Hospital Rancagua', 'camas_totales': 50, 'camas_ocupadas': 0},
    {'nombre': 'Hospital San Fernando', 'camas_totales': 50, 'camas_ocupadas': 0},
    {'nombre': 'Hospital Santa Cruz', 'camas_totales': 50, 'camas_ocupadas': 0},
]
```

## ⚠️ Advertencias

1. **No usar `+=` directamente**: Siempre usar métodos del modelo
2. **Usar transacciones**: Para operaciones críticas
3. **Validar siempre**: Antes de modificar camas
4. **Registrar cambios**: Para auditoría
5. **Manejar errores**: Con mensajes claros al usuario
