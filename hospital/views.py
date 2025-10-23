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
            Paciente.objects.create(
                rut=rut, nombre=nombre, edad=edad, genero=genero,
                prevision=prevision, comorbilidades=comorbilidades,
                funcionalidad=funcionalidad
            )
            return redirect('ver_fichas') # Redirige a la lista de pacientes
    return render(request, "ficha_paciente.html")

def registrar_derivacion(request):
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        paciente_rut = request.POST.get('paciente_rut')
        motivo = request.POST.get('motivo')
        prestacion = request.POST.get('prestacion')
        estado_paciente = request.POST.get('estado_paciente')
        observaciones = request.POST.get('observaciones')
        hospital = request.POST.get('hospital')

        # Buscamos al paciente por el ID que viene del <select>.
        # Usamos un bloque try-except por si algo sale mal.
        try:
            paciente = Paciente.objects.get(rut=paciente_rut)
        except Paciente.DoesNotExist:
            pacientes = Paciente.objects.all().order_by('nombre')
            return render(request, "registrar_derivacion.html", {'error': 'Paciente no válido. Por favor, seleccione uno de la lista.', 'pacientes': pacientes})

        # Creamos el objeto Derivacion y lo guardamos
        Derivacion.objects.create(
            paciente=paciente,
            motivo=motivo,
            prestacion_requerida=prestacion,
            estado_paciente=estado_paciente,
            observaciones=observaciones,
            hospital_receptor=hospital
        )
        # Redirigimos al usuario a la lista de derivaciones
        return redirect('ver_derivaciones')

    # Obtenemos todos los pacientes para mostrarlos en el dropdown
    pacientes = Paciente.objects.all().order_by('nombre')
    return render(request, "registrar_derivacion.html", {"pacientes": pacientes})

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
    derivacion = get_object_or_404(Derivacion, id=derivacion_id)

    if request.method == 'POST':
        # Obtenemos los datos del formulario de edición
        derivacion.motivo = request.POST.get('motivo')
        derivacion.prestacion_requerida = request.POST.get('prestacion')
        derivacion.estado_paciente = request.POST.get('estado_paciente')
        derivacion.observaciones = request.POST.get('observaciones')
        derivacion.hospital_receptor = request.POST.get('hospital')
        derivacion.estado = request.POST.get('estado')
        
        # Guardamos los cambios en la base de datos
        derivacion.save()

        # Redirigimos a la lista de derivaciones
        return redirect('ver_derivaciones')

    # Si es una petición GET, mostramos el formulario con los datos actuales
    return render(request, 'editar_derivacion.html', {'derivacion': derivacion})

def borrar_derivacion(request, derivacion_id):
    # Obtenemos la derivación que se va a borrar
    derivacion = get_object_or_404(Derivacion, id=derivacion_id)
    
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
        paciente.comorbilidades = request.POST.get('comorbilidades')
        paciente.funcionalidad = request.POST.get('funcionalidad')
        paciente.save()
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
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    # Verificar rol correcto
    if request.session.get('usuario_rol') != 'Médico':
        return redirect('index')
    return render(request, "medico.html")

def medico_buscar(request):
    return render(request, "medico_buscar.html")

def medico_ficha(request):
    return render(request, "medico_ficha.html")

def medico_historial(request):
    return render(request, "medico_historial.html")

def medico_actual(request):
    return render(request, "medico_actual.html")


# PANEL COORDINADOR

def coordinador(request):
    # Verificar autenticación
    if 'usuario_id' not in request.session:
        return redirect('index')
    
    # Verificar rol correcto
    if request.session.get('usuario_rol') != 'Coordinador':
        return redirect('index')
    return render(request, "coordinador.html")

def coord_derivaciones(request):
    # Obtenemos las derivaciones que no están Aceptadas o Rechazadas para gestionarlas
    derivaciones_pendientes = Derivacion.objects.exclude(estado='Aceptada').exclude(estado='Rechazada').order_by('fecha')
    return render(request, "coord_derivaciones.html", {'derivaciones': derivaciones_pendientes})

def gestionar_derivacion(request, derivacion_id, nuevo_estado):
    derivacion = get_object_or_404(Derivacion, id=derivacion_id)
    derivacion.estado = nuevo_estado
    derivacion.save()
    return redirect('coord_derivaciones')

def coord_camas(request):
    return render(request, "coord_camas.html")

def coord_reportes(request):
    return render(request, "coord_reportes.html")
