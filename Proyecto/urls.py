from django.contrib import admin
from django.urls import path
from hospital import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # login
    path("", views.index, name="index"),
    path("login", views.login, name="login"),

    # Panel Coordinador 
    path("coordinador/", views.coordinador, name="coordinador"),
    path("coordinador/derivaciones", views.coord_derivaciones, name="coord_derivaciones"),
    path('coordinador/derivacion/gestionar/<int:derivacion_id>/<str:nuevo_estado>/', views.gestionar_derivacion, name='gestionar_derivacion'),
    path("coordinador/camas", views.coord_camas, name="coord_camas"),
    path("coordinador/reportes", views.coord_reportes, name="coord_reportes"),

    # Panel Médico 
    path("medico/", views.medico, name="medico"),
    path("medico/buscar", views.medico_buscar, name="medico_buscar"),
    path("medico/ficha", views.medico_ficha, name="medico_ficha"),
    path("medico/historial", views.medico_historial, name="medico_historial"),
    path("medico/actual", views.medico_actual, name="medico_actual"),

    # Panel TENS 
    path("tens/", views.tens, name="tens"),
    path("tens/ficha", views.ficha_paciente, name="ficha_paciente"),
    path("tens/fichas", views.ver_fichas, name="ver_fichas"),
    path('tens/ficha/editar/<str:paciente_rut>/', views.editar_paciente, name='editar_paciente'),
    path('tens/ficha/borrar/<str:paciente_rut>/', views.borrar_paciente, name='borrar_paciente'),
    path("tens/derivacion", views.registrar_derivacion, name="registrar_derivacion"),
    path("tens/derivaciones", views.ver_derivaciones, name="ver_derivaciones"),
    path('tens/derivacion/editar/<int:derivacion_id>/', views.editar_derivacion, name='editar_derivacion'),
    path('tens/derivacion/borrar/<int:derivacion_id>/', views.borrar_derivacion, name='borrar_derivacion'),
]
