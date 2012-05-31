# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import auth
from django.forms.forms import NON_FIELD_ERRORS

from proyecto.app.models import Cuestionario
from proyecto.app.models import Evaluacion
from proyecto.app.models import Contestacion
from proyecto.app.models import AsignaturaDocente
from proyecto.app.models import EstudianteAsignaturaDocente
from proyecto.app.models import EstudiantePeriodoAcademico
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import Asignatura
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import Configuracion

from datetime import datetime
import logging
logg = logging.getLogger('logapp')

def index(request):
    return HttpResponse("<h3>Bienvenido al Sistema de Evaluacion de la UNL</h3>")

def login(request):
    from django import forms
    form = forms.Form()
    form.fields['username'] = forms.CharField(label="Username", max_length=30,
                                              error_messages={'required':'Ingrese nombre de usuario'})
    form.fields['password'] = forms.CharField(label="Password", widget=forms.PasswordInput,
                                              error_messages={'required':'Ingrese el password'})
    data = dict(form=form)    
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)        
        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('/carreras')
        else:
            form.full_clean()
            form._errors[NON_FIELD_ERRORS] = form.error_class(['Error de usuario o contraseña'])
    data.update(csrf(request))
    return render_to_response("app/login.html",data)
        

def carreras(request):
    pa = Configuracion.getPeriodoAcademicoActual()
    usuario = request.user
    try:
        logg.info(usuario)
        estudiante = EstudiantePeriodoAcademico.objects.get(periodoAcademico=pa, usuario=usuario)
        carreras = estudiante.asignaturasDocentesEstudiante.values('asignaturaDocente__asignatura__carrera').distinct()
        # Al final un diccionario de carreras en session 
        carreras = [ dict(num_carrera=i, nombre=c['asignaturaDocente__asignatura__carrera'])
                     for i,c in enumerate(carreras) ]
        request.session['estudiante'] = estudiante
        request.session['carreras'] = carreras
        if len(carreras) == 1:
            return redirect('/carrera/asignaturas/0')
        datos = dict(title=estudiante)
        return render_to_response("app/carreras.html", datos, context_instance=RequestContext(request))
    except EstudiantePeriodoAcademico.DoesNotExist:
        try:
            docente = DocentePeriodoAcademico.objects.get(periodoAcademico=pa, usuario=usuario)
            return HttpResponse('Ud es docente en el presente periodo')
        except DocentePeriodoAcademico.DoesNotExist:
            return HttpResponse('Fin')


def carrera_asignaturas(request, num_carrera):
    estudiante = request.session['estudiante']
    carrera = [c['nombre'] for c in request.session['carreras']
               if c['num_carrera'] == int(num_carrera) ][0]
    request.session['carrera'] = carrera
    logg.info(carrera)
    ids = estudiante.asignaturasDocentesEstudiante.filter(
        asignaturaDocente__asignatura__carrera=carrera).values_list(
        'asignaturaDocente__asignatura__id', flat=True).distinct()
    asignaturas = Asignatura.objects.filter(id__in=ids).order_by('nombre')
    request.session['asignaturas'] = asignaturas
    # Para regresar a esta vista
    request.session['num_carrera'] = str(num_carrera)
    title = u"{0}".format(carrera)
    datos = dict(asignaturas=asignaturas, title=title)
    return render_to_response("app/asignaturas_docentes.html", datos)


def asignaturas_docentes(request, id_asignatura):
    estudiante = request.session['estudiante']
    carrera = request.session['carrera']
    asignaturas = request.session['asignaturas']
    asignatura = Asignatura.objects.get(id=int(id_asignatura))
    request.session['asignatura'] = asignatura
    docentes =  [ da.docente for da in asignatura.docentesAsignatura.all() ]
    logg.info(docentes)
    title = u"{0} >> {1}".format(carrera, asignatura.nombre)
    datos = dict(asignaturas=asignaturas, seleccion=asignatura, docentes=docentes, title=title)
    return render_to_response("app/asignaturas_docentes.html", datos)

def encuestas(request, id_docente):
    docente = DocentePeriodoAcademico.objects.get(id=id_docente)
    # Recuperamos objetos de la sesion fijada en vistas anteriores
    carrera = request.session['carrera']
    asignatura = request.session['asignatura']
    estudiante = request.session['estudiante']
    asignaturaDocente = AsignaturaDocente.objects.get(docente__id=id_docente, asignatura=asignatura)
    estudianteAsignaturaDocente = EstudianteAsignaturaDocente.objects.get(
        estudiante=estudiante, asignaturaDocente=asignaturaDocente)
    request.session['estudianteAsignaturaDocente'] = estudianteAsignaturaDocente
    periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
    cuestionarios = []
    if request.session['estudiante']:
        asignatura = request.session['asignatura']
        if asignatura.semestre == u"1":
            cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() if c.informante.tipo == 'EstudianteNovel']
        else:
            cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() if c.informante.tipo == 'Estudiante']
    # Si ya ha contestado todos los cuestionario disponibles
    if estudianteAsignaturaDocente.evaluaciones.count() == len(cuestionarios):
        return redirect('/carrera/asignaturas/' + request.session['num_carrera'])
    if len(cuestionarios) == 1:
        return redirect('/encuesta/responder/' + str(cuestionarios[0].id))
    title = u"{0} >> {1} >> {2}".format(carrera, asignatura.nombre, asignaturaDocente.docente) 
    datos = dict(cuestionarios=cuestionarios, title=title)
    return render_to_response("app/encuestas.html", datos)


def encuesta_responder(request, id_cuestionario):
    carrera = request.session['carrera']
    estudianteAsignaturaDocente = request.session['estudianteAsignaturaDocente']
    cuestionario = Cuestionario.objects.get(id=id_cuestionario)
    # Si ya ha contestado el cuestionario
    if estudianteAsignaturaDocente.evaluaciones.filter(cuestionario=cuestionario).count() > 0:
        return redirect('/carrera/asignaturas/' + request.session['num_carrera'])
    evaluacion = Evaluacion()
    evaluacion.fechaInicio = datetime.now().date()
    evaluacion.horaInicio = datetime.now().time()
    evaluacion.cuestionario = cuestionario
    evaluacion.estudianteAsignaturaDocente = estudianteAsignaturaDocente
    request.session['evaluacion'] = evaluacion
    title = u"{0} >> {1} >> {2}".format(carrera,
                                        estudianteAsignaturaDocente.asignaturaDocente.asignatura.nombre,
                                        estudianteAsignaturaDocente.asignaturaDocente.docente)

    datos = dict(cuestionario=cuestionario, title=title)
    # Por cuestion del formulario
    datos.update(csrf(request))    
    return render_to_response("app/encuesta_responder.html", datos)


def encuesta_grabar(request):
    evaluacion = request.session['evaluacion']
    ###estudianteAsignaturaDocente = request.session['estudianteAsignaturaDocente']
    ###evaluacion.estudianteAsignaturaDocente = estudianteAsignaturaDocente
    evaluacion.fechaFin = datetime.now().date()
    evaluacion.horaFin = datetime.now().time()
    evaluacion.save()
    for k,v in request.POST.items():
        if k.startswith('csrf'):
            continue
        id_pregunta = int(k.split('-')[1])
        contestacion = Contestacion(pregunta = id_pregunta, respuesta=v)
        contestacion.evaluacion = evaluacion
        contestacion.save()
    return HttpResponse('Encuesta Conestada !!! Gracias')
