# Cargar Datos Iniciales en el Sistema

## ⚠️ Problema Actual

Si ves el error: `Field 'id_hospital' expected a number but got 'Hospital Rancagua'`

Esto significa que **no tienes hospitales en la base de datos**.

## ✅ Solución: Cargar Hospitales

Ejecuta este comando en tu terminal (desde la carpeta del proyecto):

```cmd
python manage.py cargar_hospitales
```

Este comando creará 3 hospitales de prueba:
- Hospital Rancagua (60 camas, 48 ocupadas)
- Hospital San Fernando (30 camas, 25 ocupadas)
- Hospital Santa Cruz (20 camas, 17 ocupadas)

## 📋 Cargar Usuarios (si aún no lo has hecho)

Si necesitas crear usuarios de prueba:

```cmd
python manage.py cargar_usuarios
```

Este comando creará usuarios para cada rol:
- TENS (usuario: tens, clave: tens123)
- Médico (usuario: medico, clave: medico123)
- Coordinador (usuario: coordinador, clave: coord123)

## 🔄 Orden Recomendado para Probar el Sistema

1. **Cargar hospitales:**
   ```cmd
   python manage.py cargar_hospitales
   ```

2. **Cargar usuarios (si no existen):**
   ```cmd
   python manage.py cargar_usuarios
   ```

3. **Iniciar el servidor:**
   ```cmd
   python manage.py runserver
   ```

4. **Probar el flujo completo:**
   
   a. **Como TENS** (http://127.0.0.1:8000):
      - Usuario: `tens`
      - Clave: `tens123`
      - Crear fichas de pacientes
   
   b. **Como Médico** (http://127.0.0.1:8000):
      - Usuario: `medico`
      - Clave: `medico123`
      - Registrar derivaciones de pacientes
   
   c. **Como Coordinador** (http://127.0.0.1:8000):
      - Usuario: `coordinador`
      - Clave: `coord123`
      - Ver dashboard con estadísticas
      - Gestionar derivaciones (aceptar/rechazar)
      - Ver estado de camas

## 🗄️ Alternativa: Cargar Hospitales Manualmente

Si prefieres usar phpMyAdmin o SQL directo:

1. Abre phpMyAdmin: `http://localhost/phpmyadmin`
2. Selecciona tu base de datos
3. Ejecuta este SQL:

```sql
INSERT INTO HOSPITAL (nombre, camas_totales, camas_ocupadas) VALUES
('Hospital Rancagua', 60, 48),
('Hospital San Fernando', 30, 25),
('Hospital Santa Cruz', 20, 17);
```

## 🔍 Verificar que los Datos se Cargaron

Puedes verificar en phpMyAdmin o ejecutar:

```cmd
python manage.py shell
```

Y luego:

```python
from hospital.models import Hospital, Usuario, Paciente
print(f"Hospitales: {Hospital.objects.count()}")
print(f"Usuarios: {Usuario.objects.count()}")
print(f"Pacientes: {Paciente.objects.count()}")
```

## 📝 Notas Importantes

- Los comandos `cargar_hospitales` y `cargar_usuarios` son seguros de ejecutar múltiples veces
- Te preguntarán si quieres sobrescribir los datos existentes
- Asegúrate de estar en la carpeta raíz del proyecto al ejecutar los comandos
- MySQL debe estar corriendo en XAMPP

## 🆘 Si Sigues Teniendo Problemas

1. Verifica que MySQL esté corriendo en XAMPP
2. Verifica la conexión a la base de datos en `settings.py`
3. Ejecuta las migraciones: `python manage.py migrate`
4. Revisa que la tabla HOSPITAL exista en phpMyAdmin
