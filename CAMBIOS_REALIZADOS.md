# Cambios Realizados en el Sistema

## 1. Movimiento de "Registrar Derivación" de TENS a Médico

### ✅ Cambios Implementados:

#### A. Restricciones de Seguridad (views.py)
- **registrar_derivacion()**: Ahora solo médicos pueden acceder
- **editar_derivacion()**: Ahora solo médicos pueden editar
- **borrar_derivacion()**: Ahora solo médicos pueden borrar

#### B. Rutas Actualizadas (urls.py)
**Eliminadas del panel TENS:**
- `tens/derivacion` (registrar)
- `tens/derivacion/editar/<id>/`
- `tens/derivacion/borrar/<id>/`

**Agregadas al panel Médico:**
- `medico/derivacion` (registrar)
- `medico/derivaciones` (ver listado)
- `medico/derivacion/editar/<id>/`
- `medico/derivacion/borrar/<id>/`

#### C. Interfaz Actualizada

**Panel TENS (tens.html):**
- ❌ Eliminado: Botón "Registrar Derivación"
- ✅ Mantiene: "Ver Derivaciones Registradas" (solo lectura)

**Panel Médico (medico.html):**
- ✅ Agregado: Botón "Registrar Derivación"
- ✅ Agregado: Botón "Ver Derivaciones"

**Formulario de Derivación (registrar_derivacion.html):**
- Botón "Volver" ahora redirige al Panel Médico (antes iba a TENS)

## 2. Permisos por Rol

### TENS puede:
- ✅ Crear fichas de pacientes
- ✅ Ver fichas de pacientes
- ✅ Editar fichas de pacientes
- ✅ Borrar fichas de pacientes
- ✅ Ver derivaciones (solo lectura)
- ❌ NO puede registrar derivaciones
- ❌ NO puede editar derivaciones
- ❌ NO puede borrar derivaciones

### Médico puede:
- ✅ Buscar pacientes
- ✅ Ver ficha clínica
- ✅ Ver historial de derivaciones
- ✅ Ver derivación actual
- ✅ Registrar derivaciones (NUEVO)
- ✅ Ver todas las derivaciones (NUEVO)
- ✅ Editar derivaciones (NUEVO)
- ✅ Borrar derivaciones (NUEVO)

### Coordinador puede:
- ✅ Gestionar derivaciones (aceptar/rechazar)
- ✅ Ver camas disponibles
- ✅ Generar reportes

## 3. Flujo de Trabajo Actualizado

```
1. TENS registra al paciente
   └─> Crea ficha con datos básicos

2. Médico evalúa al paciente
   └─> Decide si requiere derivación
       └─> Registra la derivación con detalles médicos

3. Coordinador gestiona la derivación
   └─> Revisa disponibilidad
       └─> Acepta o rechaza según capacidad

4. Todos pueden ver el estado
   └─> TENS: solo lectura
   └─> Médico: puede modificar
   └─> Coordinador: gestiona aceptación
```

## Archivos Modificados

1. ✅ `hospital/views.py` - Agregadas validaciones de rol
2. ✅ `Proyecto/urls.py` - Reorganizadas las rutas
3. ✅ `hospital/templates/tens.html` - Removido botón de derivación
4. ✅ `hospital/templates/medico.html` - Agregados botones de derivación
5. ✅ `hospital/templates/registrar_derivacion.html` - Actualizado enlace de retorno

## Próximos Pasos Sugeridos

1. Probar el flujo completo con cada rol
2. Verificar que las restricciones funcionen correctamente
3. Implementar mejoras en el panel de coordinador (ver IDEAS_PANEL_COORDINADOR.md)
4. Considerar agregar notificaciones cuando se crea una derivación
