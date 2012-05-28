# -*- encoding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import auth
from django.forms.forms import NON_FIELD_ERRORS

from proyecto.app.models import AsignaturaDocente
from proyecto.app.models import EstudianteAsignaturaDocente
from proyecto.app.models import EstudiantePeriodoAcademico
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import Asignatura
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import Configuracion

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
        carreras = [ dict(num_carrera=i, nombre=c['asignaturaDocente__asignatura__carrera']) for i,c in enumerate(carreras) ]
        request.session['estudiante'] = estudiante
        request.session['carreras'] = carreras
        return render_to_response("app/carreras.html", dict(title='Carreras'), context_instance=RequestContext(request))
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
    datos = dict(asignaturas=asignaturas, title='Asignaturas de su Carrera')
    return render_to_response("app/asignaturas_docentes.html", datos)


def asignaturas_docentes(request, id_asignatura):
    estudiante = request.session['estudiante']
    carrera = request.session['carrera']
    asignaturas = request.session['asignaturas']
    asignatura = Asignatura.objects.get(id=int(id_asignatura))
    request.session['asignatura'] = asignatura
    docentes =  [ da.docente for da in asignatura.docentesAsignatura.all() ]
    logg.info(docentes)
    datos = dict(asignaturas=asignaturas, seleccion=asignatura, docentes=docentes, title='Asignaturas y Docentes')
    return render_to_response("app/asignaturas_docentes.html", datos)

def encuestas(request, id_docente):
    periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
    encuestas = []
    if request.session['estudiante']:
        asignatura = request.session['asignatura']
        if asignatura.semestre == u"1":
            encuestas = [e for e in periodoEvaluacion.cuestionarios.all() if e.informante.tipo == 'EstudianteNovel']
        else:
            encuestas = [e for e in periodoEvaluacion.cuestionarios.all() if e.informante.tipo == 'Estudiante']
    datos = dict(encuestas=encuestas, title='Encuestas Disponibles')
    return render_to_response("app/encuestas.html", datos)
