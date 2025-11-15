# ✅ Sistema de Gestión Automática de Camas - IMPLEMENTADO

## 🎉 ¿Qué se implementó?

### 1. Métodos en el Modelo Hospital
Se agregaron métodos inteligentes para gestionar camas:

- `tiene_camas_disponibles()` - Verifica si hay camas libres
- `camas_disponibles()` - Retorna cuántas camas están libres
- `ocupar_cama()` - Ocupa una cama automáticamente
- `liberar_cama()` - Libera una cama automáticamente
- `porcentaje_ocupacion()` - Calcula el % de ocupación

### 2. Lógica Automática en gestionar_derivacion()

**Cuando el coordinador ACEPTA una derivación:**
1. ✅ Verifica que haya camas disponibles
2. ✅ Si hay camas → Descuenta 1 cama automáticamente
3. ✅ Si NO hay camas → Muestra error y no permite aceptar
4. ✅ Actualiza la base de datos inmediatamente

**Cuando el coordinador RECHAZA una derivación aceptada:**
1. ✅ Libera la cama automáticamente
2. ✅ Suma 1 cama disponible
3. ✅ Actualiza la base de datos

### 3. Interfaz Mejorada

**En la tabla de derivaciones:**
- Muestra camas disponibles en tiempo real
- Badge con colores:
  - 🟢 Verde: > 5 camas disponibles
  - 🟡 Amarillo: 1-5 camas disponibles
  - 🔴 Rojo: 0 camas disponibles
- Botón "Aceptar" se deshabilita si no hay camas
- Opción de "Liberar" cama en derivaciones aceptadas

**Mensajes de error:**
- Alerta roja si intenta aceptar sin camas
- Indica qué hospital no tiene capacidad

### 4. Seguridad y Consistencia

- ✅ Usa transacciones atómicas (evita conflictos)
- ✅ Validaciones antes de modificar camas
- ✅ No permite valores negativos
- ✅ Sincronización inmediata con la base de datos

## 🚀 Cómo Usar el Sistema

### Paso 1: Recargar Hospitales con 50 Camas
```cmd
python manage.py cargar_hospitales
```
Esto creará/actualizará los hospitales con 50 camas cada uno.

### Paso 2: Probar el Flujo Completo

#### Como Médico:
1. Inicia sesión como médico
2. Registra una derivación
3. Selecciona un hospital
4. La derivación queda en estado "Pendiente"

#### Como Coordinador:
1. Inicia sesión como coordinador
2. Ve al dashboard → Verás estadísticas actualizadas
3. Ve a "Gestionar Derivaciones"
4. Verás las camas disponibles de cada hospital
5. Haz clic en "Aceptar" (✓)
   - ✅ La cama se descuenta automáticamente
   - ✅ El estado cambia a "Aceptada"
   - ✅ La base de datos se actualiza
6. Si intentas aceptar sin camas:
   - ❌ Verás un mensaje de error
   - ❌ El botón estará deshabilitado

### Paso 3: Verificar en la Base de Datos

Puedes verificar en phpMyAdmin:
```sql
SELECT nombre, camas_totales, camas_ocupadas, 
       (camas_totales - camas_ocupadas) as disponibles
FROM HOSPITAL;
```

## 📊 Ejemplo de Flujo

```
Estado Inicial:
Hospital Rancagua: 50 camas totales, 0 ocupadas

Médico registra derivación → Estado: Pendiente
Hospital Rancagua: 50 camas totales, 0 ocupadas

Coordinador acepta derivación → Estado: Aceptada
Hospital Rancagua: 50 camas totales, 1 ocupada ✅

Coordinador acepta otra derivación → Estado: Aceptada
Hospital Rancagua: 50 camas totales, 2 ocupadas ✅

... (48 derivaciones más) ...

Hospital Rancagua: 50 camas totales, 50 ocupadas

Coordinador intenta aceptar otra derivación:
❌ ERROR: "No se puede aceptar: Hospital Rancagua no tiene camas disponibles"
Botón "Aceptar" deshabilitado

Coordinador rechaza una derivación aceptada:
Hospital Rancagua: 50 camas totales, 49 ocupadas ✅ (liberó 1 cama)
```

## 🎨 Características Visuales

### Dashboard del Coordinador
- Muestra camas disponibles totales
- Porcentaje de ocupación con colores
- Barras de progreso por hospital

### Gestión de Derivaciones
- Badge de disponibilidad en cada fila
- Botones inteligentes (se deshabilitan sin camas)
- Alertas visuales de error
- Confirmación al liberar camas

## 🔧 Mantenimiento

### Resetear Camas a 0
Si necesitas resetear todas las camas:
```python
python manage.py shell
>>> from hospital.models import Hospital
>>> Hospital.objects.all().update(camas_ocupadas=0)
```

### Cambiar Total de Camas
Para cambiar el total de camas de un hospital:
```python
>>> hospital = Hospital.objects.get(nombre='Hospital Rancagua')
>>> hospital.camas_totales = 100
>>> hospital.save()
```

### Ver Estado Actual
```python
>>> for h in Hospital.objects.all():
...     print(f"{h.nombre}: {h.camas_disponibles()}/{h.camas_totales} disponibles")
```

## 📈 Próximas Mejoras (Opcionales)

1. **Historial de Camas**: Registrar cada cambio
2. **Alertas Automáticas**: Notificar cuando queden pocas camas
3. **Reserva de Camas**: Permitir reservar antes de aceptar
4. **Alta de Pacientes**: Botón para dar de alta y liberar cama
5. **Reportes**: Gráficos de ocupación histórica
6. **Predicción**: Estimar cuándo se llenarán los hospitales

## ⚠️ Notas Importantes

1. **Sincronización**: Los cambios son inmediatos en la BD
2. **Múltiples Usuarios**: El sistema maneja múltiples coordinadores simultáneamente
3. **Validación**: No permite camas negativas ni exceder el total
4. **Transacciones**: Usa transacciones atómicas para evitar errores
5. **Reversible**: Puedes rechazar una derivación aceptada para liberar la cama

## 🧪 Testing

Prueba estos escenarios:

1. ✅ Aceptar derivación con camas disponibles
2. ✅ Intentar aceptar sin camas (debe fallar)
3. ✅ Rechazar derivación aceptada (debe liberar cama)
4. ✅ Ver dashboard actualizado en tiempo real
5. ✅ Filtrar derivaciones por hospital
6. ✅ Verificar que los números coincidan con la BD

## 🎓 Conceptos Implementados

- **Transacciones Atómicas**: Para consistencia de datos
- **Métodos de Modelo**: Lógica encapsulada
- **Validación de Negocio**: Reglas antes de guardar
- **UI Reactiva**: Botones que se adaptan al estado
- **Mensajes de Usuario**: Feedback claro
- **Sincronización en Tiempo Real**: Actualización inmediata

¡El sistema está listo para usar! 🚀
