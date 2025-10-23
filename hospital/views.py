from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import models
# Importamos los modelos que acabamos de crear
from .models import Paciente, Derivacion, FichaPaciente, Hospital, Usuario

# LOGIN

def index(request):
    return render(request, "index.html")

def login(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        clave = request.POST.get("clave")
        rol = request.POST.get("rol")

        # Validaciones
        if not usuario or not clave or not rol:
            return render(request, "index.html", {"error": "Todos los campos son obligatorios."})

        if rol == "coordinador":
            return redirect("coordinador")
        elif rol == "medico":
            return redirect("medico")
        elif rol == "tens":
            return redirect("tens")
        else:
            return render(request, "index.html", {"error": "Rol inválido, selecciona uno correcto."})

    return render(request, "index.html")


# PANEL TENS

def tens(request):
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
            # Primero, creamos o actualizamos el Paciente.
            # Usamos update_or_create para evitar duplicados por RUT.
            paciente, created = Paciente.objects.update_or_create(
                rut=rut,
                defaults={'nombre': nombre, 'edad': edad, 'genero': genero, 'prevision': prevision}
            )
            # Luego, creamos o actualizamos la FichaPaciente asociada.
            FichaPaciente.objects.update_or_create(
                id_paciente=paciente,
                defaults={'comorbilidades': comorbilidades, 'funcionalidad': funcionalidad}
            )
            return redirect('ver_fichas') # Redirige a la lista de pacientes
    return render(request, "ficha_paciente.html")

def buscar_paciente_por_rut(request):
    """API endpoint para buscar pacientes por RUT"""
    rut = request.GET.get('rut', '').strip()
    
    if not rut:
        return JsonResponse({'pacientes': []})
    
    # Buscar pacientes cuyo RUT contenga el texto ingresado
    pacientes = Paciente.objects.filter(rut__icontains=rut)[:10]  # Limitar a 10 resultados
    
    resultados = [{
        'rut': p.rut,
        'nombre': p.nombre,
        'edad': p.edad,
        'prevision': p.prevision
    } for p in pacientes]
    
    return JsonResponse({'pacientes': resultados})

def registrar_derivacion(request):
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        paciente_rut = request.POST.get('paciente_rut')
        motivo = request.POST.get('motivo')
        prestacion = request.POST.get('prestacion')
        estado_paciente = request.POST.get('estado_paciente')
        observaciones = request.POST.get('observaciones')
        hospital_nombre = request.POST.get('hospital')

        # Buscamos al paciente por RUT
        try:
            paciente = Paciente.objects.get(rut=paciente_rut)
        except Paciente.DoesNotExist:
            return render(request, "registrar_derivacion.html", {
                'error': f'No se encontró ningún paciente con el RUT: {paciente_rut}. Por favor, verifique el RUT ingresado.'
            })

        # Buscamos o creamos el hospital
        hospital, created = Hospital.objects.get_or_create(
            nombre=hospital_nombre,
            defaults={'camas_totales': 0, 'camas_ocupadas': 0}
        )

        # Obtenemos o creamos un usuario por defecto
        # En producción, deberías usar request.user si tienes autenticación
        usuario, created = Usuario.objects.get_or_create(
            usuario='sistema',
            defaults={
                'nombre': 'Sistema',
                'clave': 'sistema123',
                'rol': 'TENS'
            }
        )

        # Creamos el objeto Derivacion con los nombres correctos de los campos del modelo
        derivacion = Derivacion.objects.create(
            id_paciente=paciente,
            id_hospital=hospital,
            id_usuario=usuario,
            motivo=motivo,
            prestacion=prestacion,
            estado='Pendiente'
        )
        
        # Guardamos estado_paciente y observaciones en la ficha del paciente
        # ya que no están en el modelo Derivacion
        if observaciones or estado_paciente:
            FichaPaciente.objects.update_or_create(
                id_paciente=paciente,
                defaults={
                    'observaciones': observaciones or ''
                }
            )
        
        # Redirigimos al usuario a la lista de derivaciones
        return redirect('ver_derivaciones')

    return render(request, "registrar_derivacion.html")

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
    # Obtenemos la derivación específica o mostramos un error 404 si no existe
    derivacion = get_object_or_404(Derivacion, id_derivacion=derivacion_id)

    if request.method == 'POST':
        # Obtenemos los datos del formulario de edición
        derivacion.motivo = request.POST.get('motivo')
        derivacion.prestacion = request.POST.get('prestacion')
        derivacion.estado = request.POST.get('estado')
        
        # Actualizamos el hospital si cambió
        hospital_nombre = request.POST.get('hospital')
        if hospital_nombre:
            hospital, created = Hospital.objects.get_or_create(
                nombre=hospital_nombre,
                defaults={'camas_totales': 0, 'camas_ocupadas': 0}
            )
            derivacion.id_hospital = hospital
        
        # Guardamos los cambios en la base de datos
        derivacion.save()

        # Redirigimos a la lista de derivaciones
        return redirect('ver_derivaciones')

    # Si es una petición GET, mostramos el formulario con los datos actuales
    return render(request, 'editar_derivacion.html', {'derivacion': derivacion})

def borrar_derivacion(request, derivacion_id):
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

    if request.method == 'POST':
        # El RUT no se edita, es la clave primaria
        paciente.nombre = request.POST.get('nombre')
        paciente.edad = request.POST.get('edad')
        paciente.genero = request.POST.get('genero')
        paciente.prevision = request.POST.get('prevision')
        paciente.save()

        # Actualizamos también la FichaPaciente
        FichaPaciente.objects.update_or_create(
            id_paciente=paciente,
            defaults={
                'comorbilidades': request.POST.get('comorbilidades'),
                'funcionalidad': request.POST.get('funcionalidad')
            }
        )
        return redirect('ver_fichas')

    return render(request, 'editar_paciente.html', {'paciente': paciente})

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
    return render(request, "medico.html")

def medico_buscar(request):
    resultados = []
    query = request.GET.get('q', '').strip()
    
    if query:
        # Buscar por RUT o nombre
        resultados = Paciente.objects.filter(
            models.Q(rut__icontains=query) | 
            models.Q(nombre__icontains=query)
        ).order_by('nombre')[:20]  # Limitar a 20 resultados
    
    return render(request, "medico_buscar.html", {
        'resultados': resultados,
        'query': query
    })

def medico_ficha(request, paciente_rut=None):
    paciente = None
    ficha = None
    error = None
    
    # Si viene un RUT por GET (búsqueda desde el formulario)
    rut_busqueda = request.GET.get('rut', '').strip()
    if rut_busqueda:
        try:
            paciente = Paciente.objects.get(rut=rut_busqueda)
            try:
                ficha = FichaPaciente.objects.get(id_paciente=paciente)
            except FichaPaciente.DoesNotExist:
                ficha = None
        except Paciente.DoesNotExist:
            error = f"No se encontró ningún paciente con el RUT: {rut_busqueda}"
    # Si viene un RUT por URL
    elif paciente_rut:
        paciente = get_object_or_404(Paciente, rut=paciente_rut)
        try:
            ficha = FichaPaciente.objects.get(id_paciente=paciente)
        except FichaPaciente.DoesNotExist:
            ficha = None
    
    return render(request, "medico_ficha.html", {
        'paciente': paciente,
        'ficha': ficha,
        'error': error
    })

def medico_historial(request, paciente_rut=None):
    paciente = None
    derivaciones = []
    error = None
    
    # Si viene un RUT por GET (búsqueda desde el formulario)
    rut_busqueda = request.GET.get('rut', '').strip()
    if rut_busqueda:
        try:
            paciente = Paciente.objects.get(rut=rut_busqueda)
            derivaciones = Derivacion.objects.filter(
                id_paciente=paciente
            ).order_by('-fecha')
        except Paciente.DoesNotExist:
            error = f"No se encontró ningún paciente con el RUT: {rut_busqueda}"
    # Si viene un RUT por URL
    elif paciente_rut:
        paciente = get_object_or_404(Paciente, rut=paciente_rut)
        derivaciones = Derivacion.objects.filter(
            id_paciente=paciente
        ).order_by('-fecha')
    
    return render(request, "medico_historial.html", {
        'paciente': paciente,
        'derivaciones': derivaciones,
        'error': error
    })

def medico_actual(request, paciente_rut=None):
    paciente = None
    derivacion_actual = None
    error = None
    
    # Si viene un RUT por GET (búsqueda desde el formulario)
    rut_busqueda = request.GET.get('rut', '').strip()
    if rut_busqueda:
        try:
            paciente = Paciente.objects.get(rut=rut_busqueda)
            # Buscar derivaciones pendientes o en revisión
            derivacion_actual = Derivacion.objects.filter(
                id_paciente=paciente,
                estado__in=['Pendiente', 'En revisión']
            ).order_by('-fecha').first()
        except Paciente.DoesNotExist:
            error = f"No se encontró ningún paciente con el RUT: {rut_busqueda}"
    # Si viene un RUT por URL
    elif paciente_rut:
        paciente = get_object_or_404(Paciente, rut=paciente_rut)
        # Buscar derivaciones pendientes o en revisión
        derivacion_actual = Derivacion.objects.filter(
            id_paciente=paciente,
            estado__in=['Pendiente', 'En revisión']
        ).order_by('-fecha').first()
    
    return render(request, "medico_actual.html", {
        'paciente': paciente,
        'derivacion': derivacion_actual,
        'error': error
    })


# PANEL COORDINADOR

def coordinador(request):
    return render(request, "coordinador.html")

def coord_derivaciones(request):
    # Obtenemos las derivaciones que no están Aceptadas o Rechazadas para gestionarlas
    derivaciones_pendientes = Derivacion.objects.exclude(estado='Aceptada').exclude(estado='Rechazada').order_by('fecha')
    return render(request, "coord_derivaciones.html", {'derivaciones': derivaciones_pendientes})

def gestionar_derivacion(request, derivacion_id, nuevo_estado):
    derivacion = get_object_or_404(Derivacion, id_derivacion=derivacion_id)
    derivacion.estado = nuevo_estado
    derivacion.save()
    return redirect('coord_derivaciones')

def coord_camas(request):
    # Obtenemos todos los hospitales con su información de camas
    hospitales = Hospital.objects.all().order_by('nombre')
    
    # Calculamos estadísticas generales
    total_camas = sum(h.camas_totales for h in hospitales)
    total_ocupadas = sum(h.camas_ocupadas for h in hospitales)
    total_disponibles = total_camas - total_ocupadas
    
    # Agregamos información calculada a cada hospital
    hospitales_info = []
    for hospital in hospitales:
        disponibles = hospital.camas_totales - hospital.camas_ocupadas
        porcentaje_ocupacion = (hospital.camas_ocupadas / hospital.camas_totales * 100) if hospital.camas_totales > 0 else 0
        
        # Determinar el estado (crítico, advertencia, normal)
        if porcentaje_ocupacion >= 90:
            estado = 'critico'
        elif porcentaje_ocupacion >= 75:
            estado = 'advertencia'
        else:
            estado = 'normal'
        
        hospitales_info.append({
            'hospital': hospital,
            'disponibles': disponibles,
            'porcentaje_ocupacion': round(porcentaje_ocupacion, 1),
            'estado': estado
        })
    
    context = {
        'hospitales_info': hospitales_info,
        'total_camas': total_camas,
        'total_ocupadas': total_ocupadas,
        'total_disponibles': total_disponibles
    }
    
    return render(request, "coord_camas.html", context)

def coord_reportes(request):
    return render(request, "coord_reportes.html")
