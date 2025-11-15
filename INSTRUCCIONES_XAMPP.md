# Instrucciones para Implementar Fase 1 con XAMPP

## ✅ Cambios Realizados

Se ha implementado la **Fase 1** del panel de coordinador con:

1. **Dashboard con estadísticas en tiempo real**
2. **Filtros avanzados en gestión de derivaciones**
3. **Gestión visual de camas por hospital**

## 🔧 Configuración Necesaria

### 1. Asegúrate de tener XAMPP corriendo

```cmd
# Inicia Apache y MySQL desde el panel de control de XAMPP
```

### 2. Verifica que Django esté instalado

```cmd
python --version
pip show django
```

### 3. Aplica las migraciones (si es necesario)

```cmd
cd ruta\de\tu\proyecto
python manage.py makemigrations
python manage.py migrate
```

### 4. Crea datos de prueba para hospitales

Necesitas tener hospitales en la base de datos. Puedes hacerlo de dos formas:

#### Opción A: Usando el Admin de Django

1. Crea un superusuario (si no lo has hecho):
```cmd
python manage.py createsuperuser
```

2. Inicia el servidor:
```cmd
python manage.py runserver
```

3. Ve a: `http://127.0.0.1:8000/admin`

4. Agrega hospitales con estos datos de ejemplo:
   - **Hospital Rancagua**: 60 camas totales, 48 ocupadas
   - **Hospital San Fernando**: 30 camas totales, 25 ocupadas
   - **Hospital Santa Cruz**: 20 camas totales, 17 ocupadas

#### Opción B: Usando SQL directo en phpMyAdmin

1. Abre phpMyAdmin: `http://localhost/phpmyadmin`

2. Selecciona tu base de datos

3. Ejecuta este SQL:

```sql
INSERT INTO HOSPITAL (nombre, camas_totales, camas_ocupadas) VALUES
('Hospital Rancagua', 60, 48),
('Hospital San Fernando', 30, 25),
('Hospital Santa Cruz', 20, 17);
```

#### Opción C: Crear un comando de Django (Recomendado)

Voy a crear un archivo para que puedas cargar datos de prueba fácilmente.

### 5. Inicia el servidor de desarrollo

```cmd
python manage.py runserver
```

### 6. Accede al sistema

1. Ve a: `http://127.0.0.1:8000`
2. Inicia sesión como Coordinador
3. Verás el nuevo dashboard con estadísticas

## 📊 Nuevas Funcionalidades

### Dashboard Principal (coordinador/)
- **Tarjetas de estadísticas:**
  - Derivaciones pendientes
  - Derivaciones del día
  - Camas disponibles
  - Porcentaje de ocupación
- **Gráfico de derivaciones por estado**
- **Barras de progreso de ocupación por hospital**

### Gestión de Derivaciones (coordinador/derivaciones)
- **Filtros:**
  - Buscar por nombre o RUT del paciente
  - Filtrar por estado (Pendiente, En revisión, Aceptada, Rechazada)
  - Filtrar por hospital
- **Tabla mejorada con más información:**
  - ID de derivación
  - Datos del paciente
  - Médico solicitante
  - Fecha y hora
  - Estado con colores
  - Acciones rápidas

### Gestión de Camas (coordinador/camas)
- **Tarjetas visuales por hospital** con:
  - Camas disponibles, ocupadas y totales
  - Barra de progreso con colores según ocupación
  - Estado visual (verde/amarillo/rojo)
- **Tabla detallada** con porcentajes
- **Leyenda de estados:**
  - Verde: < 70% ocupación
  - Amarillo: 70-90% ocupación
  - Rojo: > 90% ocupación

## 🎨 Colores y Estados

El sistema usa colores intuitivos:
- 🟢 **Verde (success)**: Todo bien, capacidad disponible
- 🟡 **Amarillo (warning)**: Atención, ocupación media
- 🔴 **Rojo (danger)**: Crítico, capacidad casi llena
- 🔵 **Azul (info)**: Información general
- 🟠 **Naranja (warning)**: Pendiente de acción

## ⚠️ Notas Importantes

1. **Base de datos**: Asegúrate de que MySQL esté corriendo en XAMPP
2. **Hospitales**: Debes tener al menos un hospital registrado para ver las estadísticas
3. **Derivaciones**: Las estadísticas se calculan en tiempo real desde la base de datos
4. **Permisos**: Solo usuarios con rol "Coordinador" pueden acceder a estas vistas

## 🐛 Solución de Problemas

### Error: "No module named 'django'"
```cmd
pip install django
```

### Error: "No such table: HOSPITAL"
```cmd
python manage.py migrate
```

### No aparecen estadísticas
- Verifica que tengas hospitales registrados
- Verifica que tengas derivaciones en la base de datos
- Revisa la consola del servidor para errores

### Error de conexión a MySQL
- Verifica que MySQL esté corriendo en XAMPP
- Revisa la configuración en `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tu_base_de_datos',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 📝 Próximos Pasos (Fase 2)

Una vez que la Fase 1 esté funcionando, podemos implementar:
- Sistema de reportes con gráficos (Chart.js)
- CRUD completo de hospitales
- Exportación de datos a Excel/PDF
- Notificaciones en tiempo real

## 🆘 ¿Necesitas Ayuda?

Si encuentras algún error, comparte:
1. El mensaje de error completo
2. La URL donde ocurre
3. El rol con el que estás logueado
