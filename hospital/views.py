from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import models
from django.db.models import Q, Count
# Importamos los modelos que acabamos de crear
from .models import Paciente, Derivacion, FichaPaciente, Hospital, Usuario

# LOGIN

def index(request):
    return render(request, "index.html")

def login(request):
    if request.method == "POST":
        usuario_input = request.POST.get("usuario")
        clave_input = request.POST.get("clave")

        # Validaciones básicas
        if not usuario_input or not clave_input:
            return render(request, "index.html", {
                "error": "Por favor ingrese usuario y contraseña"
            })

        try:
            # Buscar el usuario en la base de datos
            user = Usuario.objects.get(usuario=usuario_input)
            
            # Verificar la contraseña encriptada
            from django.contrib.auth.hashers import check_password
            
            if check_password(clave_input, user.clave):
                # Contraseña correcta - Guardar en sesión
                request.session['usuario_id'] = user.id_usuario
                request.session['usuario_nombre'] = user.nombre
                request.session['usuario_rol'] = user.rol
                
                # Redirigir según el rol
                if user.rol == 'TENS':
                    return redirect('tens')
                elif user.rol == 'Médico':
                    return redirect('medico')
                elif user.rol == 'Coordinador':
                    return redirect('coordinador')
                else:
                    return render(request, "index.html", {
                        "error": "Rol no válido en el sistema"
                    })
            else:
                # Contraseña incorrecta
                return render(request, "index.html", {
                    "error": "Usuario o contraseña incorrectos"
                })
                
        except Usuario.DoesNotExist:
            # Usuario no existe
            return render(request, "index.html", {
                "error": "Usuario o contraseña incorrectos"
            })
    
    return render(request, "index.html")


def logout(request):
    """Cerrar sesión del usuario"""
    request.session.flush()
    return redirect('index')


# PANEL TENS

def tens(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    # Verificar rol correcto
    if request.session.get('usuario_rol') != 'TENS':
        return redirect('index')
    return render(request, "tens.html")

def ficha_paciente(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        edad = request.POST.get('edad')
        genero = request.POST.get('genero')
        prevision = request.POST.get('prevision')
        comorbilidades = request.POST.get('comorbilidades')
        funcionalidad = request.POST.get('funcionalidad')

        if rut and nombre and edad:
            # Crear el paciente primero
            paciente = Paciente.objects.create(
                rut=rut, 
                nombre=nombre, 
                edad=edad, 
                genero=genero,
                prevision=prevision
            )
            
            # Crear la ficha del paciente con comorbilidades y funcionalidad
            FichaPaciente.objects.create(
                id_paciente=paciente,
                comorbilidades=comorbilidades,
                funcionalidad=funcionalidad
            )
            
            return redirect('ver_fichas') # Redirige a la lista de pacientes
    return render(request, "ficha_paciente.html")

def registrar_derivacion(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    # Solo médicos pueden registrar derivaciones
    if request.session.get('usuario_rol') != 'Médico':
        return redirect('index')
    
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        paciente_rut = request.POST.get('paciente_rut')
        motivo = request.POST.get('motivo')
        prestacion = request.POST.get('prestacion')
        hospital_id = request.POST.get('hospital')

        # Validar que hospital_id sea un número
        if not hospital_id or not hospital_id.isdigit():
            pacientes = Paciente.objects.all().order_by('nombre')
            hospitales = Hospital.objects.all()
            return render(request, "registrar_derivacion.html", {
                'error': f'Hospital no válido. Por favor, seleccione un hospital de la lista. Valor recibido: "{hospital_id}"', 
                'pacientes': pacientes,
                'hospitales': hospitales
            })

        # Buscamos al paciente por RUT
        try:
            paciente = Paciente.objects.get(rut=paciente_rut)
        except Paciente.DoesNotExist:
            pacientes = Paciente.objects.all().order_by('nombre')
            hospitales = Hospital.objects.all()
            return render(request, "registrar_derivacion.html", {
                'error': 'Paciente no válido. Por favor, seleccione uno de la lista.', 
                'pacientes': pacientes,
                'hospitales': hospitales
            })
        
        # Buscamos el hospital
        try:
            hospital = Hospital.objects.get(id_hospital=int(hospital_id))
        except Hospital.DoesNotExist:
            pacientes = Paciente.objects.all().order_by('nombre')
            hospitales = Hospital.objects.all()
            return render(request, "registrar_derivacion.html", {
                'error': f'Hospital con ID {hospital_id} no existe en la base de datos.', 
                'pacientes': pacientes,
                'hospitales': hospitales
            })
        
        # Obtener el usuario actual
        usuario = Usuario.objects.get(id_usuario=request.session['usuario_id'])

        # Creamos el objeto Derivacion y lo guardamos
        Derivacion.objects.create(
            id_paciente=paciente,
            id_hospital=hospital,
            id_usuario=usuario,
            motivo=motivo,
            prestacion=prestacion,
            estado='Pendiente'
        )
        # Redirigimos al usuario a la lista de derivaciones
        return redirect('ver_derivaciones')

    # Obtenemos todos los pacientes y hospitales para mostrarlos en el formulario
    pacientes = Paciente.objects.all().order_by('nombre')
    hospitales = Hospital.objects.all()
    
    # Verificar si hay hospitales disponibles
    if not hospitales.exists():
        return render(request, "registrar_derivacion.html", {
            "pacientes": pacientes,
            "hospitales": hospitales,
            "error": "No hay hospitales registrados en el sistema. Por favor, contacte al administrador."
        })
    
    return render(request, "registrar_derivacion.html", {
        "pacientes": pacientes,
        "hospitales": hospitales
    })

def ver_derivaciones(request):
    # Obtenemos todas las derivaciones de la base de datos, ordenadas por fecha
    derivaciones = Derivacion.objects.all().order_by('-fecha')
    # Las pasamos a la plantilla
    return render(request, "ver_derivaciones.html", {"derivaciones": derivaciones})

def ver_fichas(request):
    # Obtenemos todos los pacientes de la base de datos
    pacientes = Paciente.objects.all().order_by('nombre')
    return render(request, 'ver_fichas.html', {'pacientes': pacientes})

def editar_derivacion(request, derivacion_id):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    # Solo médicos pueden editar derivaciones
    if request.session.get('usuario_rol') != 'Médico':
        return redirect('index')
    
    # Obtenemos la derivación específica o mostramos un error 404 si no existe
    derivacion = get_object_or_404(Derivacion, id_derivacion=derivacion_id)

    if request.method == 'POST':
        # Obtenemos los datos del formulario de edición
        derivacion.motivo = request.POST.get('motivo')
        derivacion.prestacion = request.POST.get('prestacion')
        
        # Actualizar hospital si cambió
        hospital_id = request.POST.get('hospital')
        if hospital_id:
            try:
                hospital = Hospital.objects.get(id_hospital=int(hospital_id))
                derivacion.id_hospital = hospital
            except Hospital.DoesNotExist:
                pass
        
        # El estado NO se modifica aquí, solo el coordinador puede cambiarlo
        # derivacion.estado se mantiene igual
        
        # Guardamos los cambios en la base de datos
        derivacion.save()

        # Redirigimos a la lista de derivaciones
        return redirect('ver_derivaciones')

    # Si es una petición GET, mostramos el formulario con los datos actuales
    hospitales = Hospital.objects.all()
    return render(request, 'editar_derivacion.html', {
        'derivacion': derivacion,
        'hospitales': hospitales
    })

def borrar_derivacion(request, derivacion_id):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    # Solo médicos pueden borrar derivaciones
    if request.session.get('usuario_rol') != 'Médico':
        return redirect('index')
    
    # Obtenemos la derivación que se va a borrar
    derivacion = get_object_or_404(Derivacion, id_derivacion=derivacion_id)
    
    # Si el usuario confirma en el formulario POST, borramos el objeto
    if request.method == 'POST':
        derivacion.delete()
        return redirect('ver_derivaciones')
    
    # Si es GET, mostramos una página de confirmación
    return render(request, 'borrar_derivacion.html', {'derivacion': derivacion})

def editar_paciente(request, paciente_rut):
    paciente = get_object_or_404(Paciente, rut=paciente_rut)
    
    # Obtener o crear la ficha del paciente
    try:
        ficha = FichaPaciente.objects.get(id_paciente=paciente)
    except FichaPaciente.DoesNotExist:
        ficha = None

    if request.method == 'POST':
        # Actualizar datos del paciente
        paciente.nombre = request.POST.get('nombre')
        paciente.edad = request.POST.get('edad')
        
        # Manejar campos opcionales (no guardar cadenas vacías)
        genero = request.POST.get('genero')
        paciente.genero = genero if genero else None
        
        prevision = request.POST.get('prevision')
        paciente.prevision = prevision if prevision else None
        
        paciente.save()
        
        # Actualizar o crear la ficha
        comorbilidades = request.POST.get('comorbilidades', '').strip()
        funcionalidad = request.POST.get('funcionalidad', '').strip()
        
        # Solo crear/actualizar ficha si hay datos
        if comorbilidades or funcionalidad:
            if ficha:
                ficha.comorbilidades = comorbilidades if comorbilidades else None
                ficha.funcionalidad = funcionalidad if funcionalidad else None
                ficha.save()
            else:
                FichaPaciente.objects.create(
                    id_paciente=paciente,
                    comorbilidades=comorbilidades if comorbilidades else None,
                    funcionalidad=funcionalidad if funcionalidad else None
                )
        
        return redirect('ver_fichas')

    return render(request, 'editar_paciente.html', {'paciente': paciente, 'ficha': ficha})

def borrar_paciente(request, paciente_rut):
    paciente = get_object_or_404(Paciente, rut=paciente_rut)

    if request.method == 'POST':
        try:
            paciente.delete()
            return redirect('ver_fichas')
        except Exception as e:
            # Manejar el caso en que un paciente no se puede borrar porque tiene derivaciones asociadas
            error_msg = f"No se puede borrar el paciente porque tiene derivaciones asociadas. Error: {e}"
            return render(request, 'borrar_paciente.html', {'paciente': paciente, 'error': error_msg})

    return render(request, 'borrar_paciente.html', {'paciente': paciente})


# PANEL MÉDICO

def medico(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    # Verificar rol correcto
    if request.session.get('usuario_rol') != 'Médico':
        return redirect('index')
    return render(request, "medico.html")

def medico_buscar(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    if request.session.get('usuario_rol') != 'Médico':
        return redirect('index')
    
    pacientes = []
    busqueda = request.GET.get('busqueda', '')
    
    if busqueda:
        pacientes = Paciente.objects.filter(
            Q(nombre__icontains=busqueda) | 
            Q(rut__icontains=busqueda)
        ).order_by('nombre')
    
    return render(request, "medico_buscar.html", {
        'pacientes': pacientes,
        'busqueda': busqueda
    })

def medico_ficha(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    if request.session.get('usuario_rol') != 'Médico':
        return redirect('index')
    
    paciente = None
    ficha = None
    paciente_rut = request.GET.get('rut', '')
    
    if paciente_rut:
        try:
            paciente = Paciente.objects.get(rut=paciente_rut)
            try:
                ficha = FichaPaciente.objects.get(id_paciente=paciente)
            except FichaPaciente.DoesNotExist:
                ficha = None
        except Paciente.DoesNotExist:
            pass
    
    return render(request, "medico_ficha.html", {
        'paciente': paciente,
        'ficha': ficha
    })

def medico_historial(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    if request.session.get('usuario_rol') != 'Médico':
        return redirect('index')
    
    derivaciones = []
    paciente = None
    paciente_rut = request.GET.get('rut', '')
    
    if paciente_rut:
        try:
            paciente = Paciente.objects.get(rut=paciente_rut)
            derivaciones = Derivacion.objects.filter(
                id_paciente=paciente
            ).select_related('id_hospital', 'id_usuario').order_by('-fecha')
        except Paciente.DoesNotExist:
            pass
    
    return render(request, "medico_historial.html", {
        'paciente': paciente,
        'derivaciones': derivaciones
    })

def medico_actual(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    if request.session.get('usuario_rol') != 'Médico':
        return redirect('index')
    
    derivacion = None
    paciente = None
    paciente_rut = request.GET.get('rut', '')
    
    if paciente_rut:
        try:
            paciente = Paciente.objects.get(rut=paciente_rut)
            # Obtener la derivación más reciente que no esté rechazada
            derivacion = Derivacion.objects.filter(
                id_paciente=paciente
            ).exclude(
                estado='Rechazada'
            ).select_related('id_hospital', 'id_usuario').order_by('-fecha').first()
        except Paciente.DoesNotExist:
            pass
    
    return render(request, "medico_actual.html", {
        'paciente': paciente,
        'derivacion': derivacion
    })


# PANEL COORDINADOR

def coordinador(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    # Verificar rol correcto
    if request.session.get('usuario_rol') != 'Coordinador':
        return redirect('index')
    
    # Estadísticas para el dashboard
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Total de derivaciones
    total_derivaciones = Derivacion.objects.count()
    
    # Derivaciones pendientes
    derivaciones_pendientes = Derivacion.objects.filter(estado='Pendiente').count()
    
    # Derivaciones del día
    hoy = datetime.now().date()
    derivaciones_hoy = Derivacion.objects.filter(fecha__date=hoy).count()
    
    # Derivaciones por estado
    derivaciones_por_estado = Derivacion.objects.values('estado').annotate(total=Count('id_derivacion'))
    
    # Hospitales y ocupación de camas
    hospitales = Hospital.objects.all()
    total_camas = sum(h.camas_totales for h in hospitales)
    total_ocupadas = sum(h.camas_ocupadas for h in hospitales)
    total_disponibles = total_camas - total_ocupadas
    porcentaje_ocupacion = round((total_ocupadas / total_camas * 100) if total_camas > 0 else 0, 1)
    
    context = {
        'total_derivaciones': total_derivaciones,
        'derivaciones_pendientes': derivaciones_pendientes,
        'derivaciones_hoy': derivaciones_hoy,
        'derivaciones_por_estado': derivaciones_por_estado,
        'total_camas': total_camas,
        'total_ocupadas': total_ocupadas,
        'total_disponibles': total_disponibles,
        'porcentaje_ocupacion': porcentaje_ocupacion,
        'hospitales': hospitales,
    }
    
    return render(request, "coordinador.html", context)

def coord_derivaciones(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    if request.session.get('usuario_rol') != 'Coordinador':
        return redirect('index')
    
    # Obtener todas las derivaciones
    derivaciones = Derivacion.objects.all().select_related('id_paciente', 'id_hospital', 'id_usuario').order_by('-fecha')
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    hospital_filtro = request.GET.get('hospital', '')
    busqueda = request.GET.get('busqueda', '')
    error = request.GET.get('error', '')
    hospital_nombre = request.GET.get('hospital', '')
    
    if estado_filtro:
        derivaciones = derivaciones.filter(estado=estado_filtro)
    
    if hospital_filtro:
        derivaciones = derivaciones.filter(id_hospital=hospital_filtro)
    
    if busqueda:
        derivaciones = derivaciones.filter(
            Q(id_paciente__nombre__icontains=busqueda) | 
            Q(id_paciente__rut__icontains=busqueda)
        )
    
    # Obtener lista de hospitales para el filtro
    hospitales = Hospital.objects.all()
    
    # Mensajes de error
    mensaje_error = None
    if error == 'sin_camas':
        mensaje_error = f'No se puede aceptar la derivación: {hospital_nombre} no tiene camas disponibles.'
    elif error == 'error_cama':
        mensaje_error = 'Error al asignar la cama. Intente nuevamente.'
    
    context = {
        'derivaciones': derivaciones,
        'hospitales': hospitales,
        'estado_filtro': estado_filtro,
        'hospital_filtro': hospital_filtro,
        'busqueda': busqueda,
        'mensaje_error': mensaje_error,
    }
    
    return render(request, "coord_derivaciones.html", context)

def buscar_pacientes_coord(request):
    """Endpoint para autocompletado de pacientes en búsqueda del coordinador"""
    if 'usuario_id' not in request.session:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    if request.session.get('usuario_rol') != 'Coordinador':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'pacientes': []})
    
    # Buscar pacientes que tengan derivaciones
    pacientes = Paciente.objects.filter(
        Q(rut__icontains=query) | Q(nombre__icontains=query)
    ).filter(
        derivacion__isnull=False
    ).distinct()[:10]
    
    resultados = [
        {
            'rut': p.rut,
            'nombre': p.nombre,
            'display': f"{p.rut} - {p.nombre}"
        }
        for p in pacientes
    ]
    
    return JsonResponse({'pacientes': resultados})

def gestionar_derivacion(request, derivacion_id, nuevo_estado):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    if request.session.get('usuario_rol') != 'Coordinador':
        return redirect('index')
    
    from django.contrib import messages
    from django.db import transaction
    
    with transaction.atomic():
        derivacion = get_object_or_404(Derivacion, id_derivacion=derivacion_id)
        estado_anterior = derivacion.estado
        hospital = derivacion.id_hospital
        
        # Si se está aceptando la derivación
        if nuevo_estado == 'Aceptada' and estado_anterior != 'Aceptada':
            # Verificar disponibilidad de camas
            if not hospital.tiene_camas_disponibles():
                # Redirigir con mensaje de error en la URL
                return redirect(f'/coordinador/derivaciones?error=sin_camas&hospital={hospital.nombre}')
            
            # Ocupar una cama
            if hospital.ocupar_cama():
                derivacion.estado = nuevo_estado
                derivacion.save()
            else:
                return redirect(f'/coordinador/derivaciones?error=error_cama')
        
        # Si se está rechazando una derivación previamente aceptada
        elif nuevo_estado == 'Rechazada' and estado_anterior == 'Aceptada':
            hospital.liberar_cama()
            derivacion.estado = nuevo_estado
            derivacion.save()
        
        # Otros cambios de estado
        else:
            derivacion.estado = nuevo_estado
            derivacion.save()
    
    return redirect('coord_derivaciones')

def coord_camas(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    if request.session.get('usuario_rol') != 'Coordinador':
        return redirect('index')
    
    # Obtener todos los hospitales con información de camas
    hospitales = Hospital.objects.all()
    
    # Calcular información adicional para cada hospital
    hospitales_info = []
    for hospital in hospitales:
        disponibles = hospital.camas_totales - hospital.camas_ocupadas
        porcentaje = round((hospital.camas_ocupadas / hospital.camas_totales * 100) if hospital.camas_totales > 0 else 0, 1)
        
        # Determinar el estado (verde, amarillo, rojo)
        if porcentaje < 70:
            estado = 'success'
        elif porcentaje < 90:
            estado = 'warning'
        else:
            estado = 'danger'
        
        hospitales_info.append({
            'hospital': hospital,
            'disponibles': disponibles,
            'porcentaje': porcentaje,
            'estado': estado
        })
    
    return render(request, "coord_camas.html", {'hospitales_info': hospitales_info})

def coord_reportes(request):
    return render(request, "coord_reportes.html")
