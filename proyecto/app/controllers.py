# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms.forms import NON_FIELD_ERRORS
from django.contrib import messages

from proyecto.app.models import Cuestionario
from proyecto.app.models import Evaluacion
from proyecto.app.models import Contestacion
from proyecto.app.models import AsignaturaDocente
from proyecto.app.models import EstudianteAsignaturaDocente
from proyecto.app.models import EstudiantePeriodoAcademico
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import Asignatura
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import OfertaAcademicaSGA
from proyecto.app.models import Configuracion

from proyecto.tools.sgaws.cliente import SGA
from proyecto.settings import SGAWS_USER, SGAWS_PASS

from datetime import datetime
from django import forms

import logging
logg = logging.getLogger('logapp')

def portada(request):
    pea = Configuracion.getPeriodoEvaluacionActual()
    datos = dict(periodoEvaluacionActual=pea)
    return render_to_response("app/portada.html",datos)

def login(request):

    form = forms.Form()
    form.fields['username'] = forms.CharField(label="Username", max_length=30, 
                                              widget=forms.TextInput(attrs={'title': 'Usuario SGA-UNL',}),
                                              error_messages={'required':'Ingrese nombre de usuario'})
    form.fields['password'] = forms.CharField(label="Password", 
                                              widget=forms.PasswordInput(attrs={'title': 'Clave del SGA-UNL',}),
                                              error_messages={'required':'Ingrese el password'})
    data = dict(form=form)    
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)        
        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('/')
        else:
            form.full_clean()
            form._errors[NON_FIELD_ERRORS] = form.error_class(['Error de usuario o contraseña'])
    data.update(csrf(request))
    return render_to_response("app/login.html",data)


def logout(request):
    auth.logout(request)
    return redirect('/portada')


@login_required(login_url='/login/')
def index(request):
    pa = Configuracion.getPeriodoAcademicoActual()
    usuario = request.user
    noEstudiante = False
    noDocente = False
    try:
        # Se trata de un Estudiante
        estudiante = EstudiantePeriodoAcademico.objects.get(periodoAcademico=pa, usuario=usuario)
        carreras_estudiante = estudiante.asignaturasDocentesEstudiante.values('asignaturaDocente__asignatura__carrera').distinct()
        # Al final un diccionario de carreras del estudiante en session 
        carreras_estudiante = [ dict(num_carrera=i, nombre=c['asignaturaDocente__asignatura__carrera'])
                     for i,c in enumerate(carreras_estudiante) ]
        request.session['estudiante'] = estudiante
        request.session['carreras_estudiante'] = carreras_estudiante
    except EstudiantePeriodoAcademico.DoesNotExist:
        noEstudiante = True
    try:
        # Se trata de un Docente 
        docente = DocentePeriodoAcademico.objects.get(periodoAcademico=pa, usuario=usuario)
        request.session['docente'] = docente
        periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
        cuestionarios_docente = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'Docente']
        request.session['cuestionarios_docente'] = cuestionarios_docente
        # Si es coordinador se colocan las carreras del docente en la session
        if docente.esCoordinador:
            carreras_docente = docente.asignaturasDocente.values('asignatura__carrera').distinct()
            carreras_docente = [ dict(num_carrera=i, nombre=c['asignatura__carrera'])
                                 for i,c in enumerate(carreras_docente) ]
            request.session['carreras_docente'] = carreras_docente
    except DocentePeriodoAcademico.DoesNotExist:
        noDocente = True

    # El usuario no es Estudiante ni Docente en el Periodo Academico Actual
    if noEstudiante and noDocente:
        return redirect('/login/')
    return render_to_response('app/index.html', context_instance=RequestContext(request))


@login_required(login_url='/login/')
def estudiante_asignaturas_docentes(request, num_carrera):
    estudiante = request.session['estudiante']
    carrera = [c['nombre'] for c in request.session['carreras_estudiante']
               if c['num_carrera'] == int(num_carrera) ][0]
    request.session['carrera'] = carrera
    # Obtenemos los id de las AsignaturasDocente
    ids = estudiante.asignaturasDocentesEstudiante.filter(
        asignaturaDocente__asignatura__carrera=carrera).values_list(
        'asignaturaDocente__id', flat=True).distinct()
    asignaturasDocentes = AsignaturaDocente.objects.filter(id__in=ids).order_by('asignatura__nombre')
    # Solo asignaturas distintas
    asignaturas = set([ad.asignatura for ad in asignaturasDocentes])
    asignaturas_docentes = []
    # Objetos para renderizarlos en la vista
    periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
    for a in asignaturas:
        diccionario = {}
        diccionario['asignatura'] = a
        diccionario['docentes'] = []
        # Una asignatura puede tener mas de un docente
        docentes = [ad.docente for ad in asignaturasDocentes if ad.asignatura == a]
        for d in docentes:
            if a.semestre == u"1":
                cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'EstudianteNovel']
            else:
                cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'Estudiante']
            estudianteAsignaturaDocente = estudiante.asignaturasDocentesEstudiante.get(
                asignaturaDocente__asignatura=a, asignaturaDocente__docente=d
                )
            # Si ya ha contestado todos los cuestionario disponibles para el docente 'd'
            if estudianteAsignaturaDocente.evaluaciones.count() == len(cuestionarios):
                diccionario['docentes'].append(dict(docente=d, evaluado=True))
            else:
            # Si no ha contestado aun todos los cuestionario disponibles para el docente 'd'
                diccionario['docentes'].append(dict(docente=d, evaluado=False))
        asignaturas_docentes.append(diccionario)
    # Para regresar posteriormente a esta vista
    request.session['num_carrera'] = str(num_carrera)
    title = u"{0}".format(carrera)
    datos = dict(asignaturas_docentes=asignaturas_docentes, title=title)
    return render_to_response("app/asignaturas_docentes.html", datos, context_instance=RequestContext(request))


def encuestas(request, id_asignatura, id_docente):
    carrera = request.session['carrera']
    estudiante = request.session['estudiante']
    asignaturaDocente = AsignaturaDocente.objects.get(docente__id=id_docente, asignatura__id=id_asignatura)
    estudianteAsignaturaDocente = EstudianteAsignaturaDocente.objects.get(
        estudiante=estudiante, asignaturaDocente=asignaturaDocente
        )
    request.session['estudianteAsignaturaDocente'] = estudianteAsignaturaDocente
    periodoEvaluacionActual = Configuracion.getPeriodoEvaluacionActual()
    cuestionarios = []
    periodo_finalizado = False
    periodo_no_iniciado = False

    # Periodo no iniciado aun
    if periodoEvaluacionActual.noIniciado():
        periodo_no_iniciado = True
    # Periodo Vigente
    elif periodoEvaluacionActual.vigente():
        if request.session['estudiante']:
            # Estudiante (Asignatura) del Instituto de Idiomas
            if asignaturaDocente.asignatura.area == "ACE":
                cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all() 
                                 if c.informante.tipo == 'InstitutoIdiomas']
            # Estudiante del Primer Semestre
            elif asignaturaDocente.asignatura.semestre == u"1":
                cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all() 
                                 if c.informante.tipo == 'EstudianteNovel']
                # Si los cuestionarios son los mismos para todos los semestres
                if len(cuestionarios) == 0:
                    cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all() 
                                 if c.informante.tipo == 'Estudiante']
            # Estudiante del segundo semestre en adelante
            else:
                cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all() 
                             if c.informante.tipo == 'Estudiante']
        # Si ya ha contestado todos los cuestionario disponibles
        if len(cuestionarios) > 0 and estudianteAsignaturaDocente.evaluaciones.count() == len(cuestionarios):
            return redirect('/estudiante/asignaturas/docentes/' + request.session['num_carrera'])
        if len(cuestionarios) == 1:
            return redirect('/encuesta/responder/' + str(cuestionarios[0].id))
    #Si ha expirado el periodo de Evaluacion
    elif periodoEvaluacionActual.finalizado():
        periodo_finalizado = True
    title = u"{0} >> {1} >> {2}".format(carrera, asignaturaDocente.asignatura.nombre, asignaturaDocente.docente) 
    datos = dict(cuestionarios=cuestionarios, title=title, 
                 periodo_no_iniciado=periodo_no_iniciado, periodo_finalizado=periodo_finalizado)
    return render_to_response("app/encuestas.html", datos, context_instance=RequestContext(request))


def encuesta_responder(request, id_cuestionario):
    carrera = request.session['carrera']
    estudianteAsignaturaDocente = request.session['estudianteAsignaturaDocente']
    cuestionario = Cuestionario.objects.get(id=id_cuestionario)
    # Si ya ha contestado este cuestionario
    if estudianteAsignaturaDocente.evaluaciones.filter(cuestionario=cuestionario).count() > 0:
        return redirect('/estudiante/asignaturas/docentes/' + request.session['num_carrera'])
    evaluacion = Evaluacion()
    evaluacion.fechaInicio = datetime.now().date()
    evaluacion.horaInicio = datetime.now().time()
    evaluacion.cuestionario = cuestionario
    evaluacion.estudianteAsignaturaDocente = estudianteAsignaturaDocente
    request.session['evaluacion'] = evaluacion
    title = u"{0} >> {1} >> {2}".format(carrera,
                                        estudianteAsignaturaDocente.asignaturaDocente.asignatura.nombre,
                                        estudianteAsignaturaDocente.asignaturaDocente.docente)
    fecha = datetime.now()
    # Para una mejor extraccioon de los datos de la asignatura se agrega el ultimo elemento
    datos = dict(cuestionario=cuestionario, title=title, 
                 asignaturaDocente=estudianteAsignaturaDocente.asignaturaDocente,
                 fecha=fecha)
    # Por cuestion del formulario
    datos.update(csrf(request))    
    return render_to_response("app/encuesta_responder.html", datos, context_instance=RequestContext(request))


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

    return render_to_response('app/encuesta_finalizada.html', context_instance=RequestContext(request))


def cargar_ofertas_sga(request, periodoAcademicoId):
    """ Metodo invocado a través de Ajax. Recarga todas las ofertas """
    if not periodoAcademicoId:
        return HttpResponse("Falta Periodo Academico")
    try:
        proxy = SGA(SGAWS_USER, SGAWS_PASS)
        pa = PeriodoAcademico.objects.get(id=periodoAcademicoId)
        ofertas_dict = proxy.ofertas_academicas(pa.inicio, pa.fin)
        ofertas = [OfertaAcademicaSGA(idSGA=oa['id'], descripcion=oa['descripcion'])  for oa in ofertas_dict]
        for oa in ofertas:
            try:
                OfertaAcademicaSGA.objects.get(idSGA=oa.idSGA)
            except OfertaAcademicaSGA.DoesNotExist:
                oa.save()
        return HttpResponse("OK")
    except Exception, e:
        log.error("Error recargando ofertas SGA: " + str(e))
        return HttpResponse("error: "+str(e))
        
# TODO: muy pesado ejecutar como tarea 'crontab'
def cargar_info_sga(request, periodoAcademicoId):
    """ Metodo invocado a través de Ajax """
    try:
        pa=PeriodoAcademico.objects.get(pk=periodoAcademicoId)
        log.info(pa + "pendiente..")
        return HttpResponse("OK")
    except Exception, e:
        log.error("Error cargando info SGA: "+str(e))
        return HttpResponse("error"+str(e))


def resultados_carrera(request, id_docente):
    #field_carrera = forms.ModelChoiceField(queryset = Asignatura.objects.values_list('carrera').distinct())
    carrera = AsignaturaDocente.objects.filter(docente__id=9).distinct().values_list('asignatura__carrera')[0][0]
    ids = set([ad.docente.id for ad in AsignaturaDocente.objects.filter(asignatura__carrera=carrera)])
    form = forms.Form()
    form.fields['docentes'] = forms.ModelChoiceField(queryset=DocentePeriodoAcademico.objects.filter(id__in=ids))
    from proyecto.app.forms import ResultadosESEForm
    datos = dict(form=form, form2=ResultadosESEForm(),title='>> Comision Academica de la Carrera ' + carrera)
    return render_to_response("app/resultados_carrera.html", datos, context_instance=RequestContext(request))
    
