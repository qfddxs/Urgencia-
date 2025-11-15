# Ideas para el Panel de Coordinador

## Funcionalidades Actuales
El coordinador actualmente tiene:
- ✅ Gestión de derivaciones (aceptar/rechazar)
- ✅ Vista de camas
- ✅ Reportes

## Ideas para Mejorar el Panel de Coordinador

### 1. Dashboard Principal
**Objetivo:** Vista general del estado del sistema

**Elementos sugeridos:**
- Tarjetas con estadísticas clave:
  - Total de derivaciones pendientes
  - Total de derivaciones del día
  - Ocupación de camas (% ocupado)
  - Derivaciones por estado (gráfico de torta)
- Alertas importantes:
  - Derivaciones urgentes sin atender
  - Hospitales con capacidad crítica
  - Pacientes en espera prolongada

### 2. Gestión Avanzada de Derivaciones
**Mejoras sugeridas:**

**Filtros y búsqueda:**
- Filtrar por estado (Pendiente, Aceptada, Rechazada, En revisión)
- Filtrar por hospital receptor
- Filtrar por fecha
- Buscar por nombre de paciente o RUT
- Filtrar por prioridad/urgencia

**Acciones adicionales:**
- Asignar prioridad a derivaciones
- Agregar comentarios/notas internas
- Historial de cambios de estado
- Notificaciones automáticas al médico cuando se acepta/rechaza
- Reasignar derivación a otro hospital

**Vista mejorada:**
```
Tabla con columnas:
- ID Derivación
- Paciente (nombre + RUT)
- Médico solicitante
- Hospital destino
- Fecha solicitud
- Estado
- Prioridad
- Acciones (Ver detalle, Aceptar, Rechazar, Reasignar)
```

### 3. Gestión de Camas Hospitalarias
**Funcionalidades sugeridas:**

**Vista por hospital:**
- Lista de hospitales con:
  - Nombre del hospital
  - Camas totales
  - Camas ocupadas
  - Camas disponibles
  - % de ocupación
  - Indicador visual (verde/amarillo/rojo según ocupación)

**Acciones:**
- Actualizar disponibilidad de camas
- Registrar ingreso de paciente (ocupar cama)
- Registrar alta de paciente (liberar cama)
- Historial de ocupación
- Proyección de disponibilidad

**Vista detallada por hospital:**
- Servicios disponibles (UCI, Urgencias, Hospitalización, etc.)
- Camas por servicio
- Pacientes actualmente hospitalizados

### 4. Sistema de Reportes
**Reportes sugeridos:**

**Reportes estadísticos:**
- Derivaciones por período (día/semana/mes)
- Tiempo promedio de respuesta
- Tasa de aceptación/rechazo por hospital
- Hospitales más solicitados
- Motivos de derivación más frecuentes
- Prestaciones más requeridas

**Reportes operativos:**
- Derivaciones pendientes de respuesta
- Pacientes en tránsito
- Ocupación histórica de camas
- Eficiencia del sistema (KPIs)

**Exportación:**
- Descargar reportes en PDF
- Exportar a Excel/CSV
- Gráficos visuales (Chart.js o similar)

### 5. Gestión de Hospitales
**Nueva funcionalidad sugerida:**

- CRUD completo de hospitales
- Configurar servicios disponibles por hospital
- Definir capacidades y especialidades
- Contactos de emergencia
- Horarios de atención
- Estado operativo (activo/inactivo/mantenimiento)

### 6. Gestión de Usuarios
**Control de acceso:**

- Ver lista de usuarios del sistema
- Crear nuevos usuarios (TENS, Médicos, Coordinadores)
- Editar información de usuarios
- Desactivar/activar usuarios
- Cambiar contraseñas
- Registro de actividad por usuario

### 7. Notificaciones y Alertas
**Sistema de comunicación:**

- Panel de notificaciones en tiempo real
- Alertas cuando:
  - Nueva derivación registrada
  - Derivación urgente sin atender
  - Hospital alcanza capacidad máxima
  - Paciente en espera prolongada (>X horas)
- Historial de notificaciones

### 8. Auditoría y Trazabilidad
**Registro de actividades:**

- Log de todas las acciones importantes:
  - Quién aceptó/rechazó cada derivación
  - Cambios en el estado de derivaciones
  - Modificaciones en datos de pacientes
  - Cambios en disponibilidad de camas
- Filtros por usuario, fecha, tipo de acción

## Priorización Sugerida

### Fase 1 (Esencial):
1. Dashboard con estadísticas básicas
2. Filtros en gestión de derivaciones
3. Gestión básica de camas por hospital

### Fase 2 (Importante):
4. Sistema de reportes básicos
5. Gestión de hospitales (CRUD)
6. Mejoras en la vista de derivaciones

### Fase 3 (Avanzado):
7. Sistema de notificaciones
8. Gestión de usuarios
9. Auditoría completa
10. Reportes avanzados con gráficos

## Ejemplo de Estructura de Menú Mejorado

```
Panel del Coordinador
├── Dashboard (inicio)
├── Derivaciones
│   ├── Pendientes
│   ├── Todas las derivaciones
│   └── Historial
├── Hospitales
│   ├── Lista de hospitales
│   ├── Gestión de camas
│   └── Agregar hospital
├── Reportes
│   ├── Estadísticas generales
│   ├── Por hospital
│   ├── Por período
│   └── Exportar datos
├── Usuarios (opcional)
│   ├── Lista de usuarios
│   └── Crear usuario
└── Configuración
    ├── Notificaciones
    └── Auditoría
```

## Tecnologías Sugeridas para Implementar

- **Gráficos:** Chart.js o ApexCharts
- **Tablas dinámicas:** DataTables (jQuery) o tablas con filtros en Bootstrap
- **Exportación:** ReportLab (PDF) o openpyxl (Excel)
- **Notificaciones:** Django Channels (WebSockets) o polling con AJAX
- **Iconos:** Font Awesome o Bootstrap Icons

## Notas de Implementación

1. Mantener la consistencia visual con el resto del sistema
2. Usar Bootstrap para mantener el diseño responsive
3. Implementar validaciones en el backend para seguridad
4. Considerar permisos granulares si hay múltiples coordinadores
5. Agregar confirmaciones para acciones críticas (rechazar derivación, etc.)
