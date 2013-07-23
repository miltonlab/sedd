# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms.forms import NON_FIELD_ERRORS
from django.contrib import messages
from django.db.models import Q
from django.utils import simplejson
from django import forms

from proyecto.app.models import Configuracion
from proyecto.app.models import Cuestionario
from proyecto.app.models import Seccion
from proyecto.app.models import Pregunta
from proyecto.app.models import Evaluacion
from proyecto.app.models import Contestacion
from proyecto.app.models import AsignaturaDocente
from proyecto.app.models import EstudianteAsignaturaDocente
from proyecto.app.models import EstudiantePeriodoAcademico
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import DireccionCarrera
from proyecto.app.models import Asignatura
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import PeriodoEvaluacion
from proyecto.app.models import Tabulacion
from proyecto.app.models import TabulacionSatisfaccion2012
from proyecto.app.models import TabulacionAdicionales2012
from proyecto.app.models import TabulacionEvaluacion2013
from proyecto.app.models import OfertaAcademicaSGA
from proyecto.app.models import AreaSGA
from proyecto.app.forms import *
from proyecto.tools.sgaws.cliente import SGA
from proyecto.settings import SGAWS_USER, SGAWS_PASS

from datetime import datetime
from ho import pisa
import os, logging, StringIO

logg = logging.getLogger('logapp')

def portada(request):
    pea = Configuracion.getPeriodoEvaluacionActual()
    datos = dict(periodoEvaluacionActual=pea)
    return render_to_response("app/portada.html",datos)

def login(request):
    form = forms.Form()
    form.fields['username'] = forms.CharField(label="Cedula", max_length=30, 
                                              widget=forms.TextInput(attrs={'title': 'Cedula',}),
                                              error_messages={'required':'Ingrese nombre de usuario'})
    form.fields['password'] = forms.CharField(label="Clave SGA", 
                                              widget=forms.PasswordInput(attrs={'title': 'Clave SGA-UNL',}),
                                              error_messages={'required':'Ingrese el password'})
    data = dict(form=form)    
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)        
        if user is not None and user.is_active:
            auth.login(request, user)
            if not Configuracion.getPeriodoAcademicoActual() or not Configuracion.getPeriodoEvaluacionActual(): 
                return redirect('/logout')
            else:
                return redirect('/index')
        else:
            form.full_clean()
            form._errors[NON_FIELD_ERRORS] = form.error_class(['Error de usuario o contraseña'])
    data.update(csrf(request))
    return render_to_response("app/login.html",data)


def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required(login_url='/login/')
def index(request):
    periodoAcademico = Configuracion.getPeriodoAcademicoActual()
    usuario = request.user
    noEstudiante = False
    noDocente = False
    periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
    datos = dict()
    # Se obtiene solo las siglas de las areas del periodo de evaluacion actual
    areas_periodo = periodoEvaluacion.areasSGA.values_list('siglas', flat=True)

    try:
        #
        # Se trata de un ESTUDIANTE
        #
        estudiante = EstudiantePeriodoAcademico.objects.get(periodoAcademico=periodoAcademico, usuario=usuario)
        # Solo las carreras que estan dentro de las areas asignadas al presente Periodo de Evaluacion
        carreras_estudiante = estudiante.asignaturasDocentesEstudiante.filter(
            asignaturaDocente__asignatura__area__in=areas_periodo).values(
            'asignaturaDocente__asignatura__carrera','asignaturaDocente__asignatura__area').distinct()
        # Al final un diccionario de carreras del estudiante en session 
        carreras_estudiante = [ dict(num_carrera=i, nombre=c['asignaturaDocente__asignatura__carrera'],
                                     area=c['asignaturaDocente__asignatura__area'])
                                for i,c in enumerate(carreras_estudiante) ]
        request.session['estudiante'] = estudiante
        request.session['carreras_estudiante'] = carreras_estudiante
    except EstudiantePeriodoAcademico.DoesNotExist:
        noEstudiante = True
    try:
        # 
        # Se trata de un DOCENTE 
        #
        docente = DocentePeriodoAcademico.objects.get(periodoAcademico=periodoAcademico, usuario=usuario)
        request.session['docente'] = docente
        if 'ACE' in docente.get_areas():
            cuestionarios_docente = periodoEvaluacion.cuestionarios.filter(informante__tipo='DocenteIdiomas')
        else:
            cuestionarios_docente = periodoEvaluacion.cuestionarios.filter(informante__tipo='Docente')
        request.session['cuestionarios_docente'] = cuestionarios_docente
        docente_autoevaluaciones = list()
        cuestionarios_evaluados = [e.cuestionario for e in docente.evaluaciones.all()]
        for c in cuestionarios_docente:
            if c in cuestionarios_evaluados:
                docente_autoevaluaciones.append(dict(cuestionario=c, evaluado=True))
            else:
                docente_autoevaluaciones.append(dict(cuestionario=c, evaluado=False))
        request.session['docente_autoevaluaciones'] = docente_autoevaluaciones
        #
        # Se trata de un docente DIRECTOR/COORDINADOR DE CARRERA
        #
        if docente.direcciones.count() > 0:
            request.session['director_carrera'] = docente
            if 'ACE' in docente.get_areas():
                cuestionarios_directivos = periodoEvaluacion.cuestionarios.filter(informante__tipo='DirectivoIdiomas')
            else:
                cuestionarios_directivos = periodoEvaluacion.cuestionarios.filter(informante__tipo='Directivo')
            request.session['cuestionarios_directivos'] = cuestionarios_directivos
            # Se colocan las carreras en las que el docente es coordinador/director
            # El nombre de la carrera contiene también el nombre del area
            carreras_director = [ dict(num_carrera=i,
                                      nombre=dc.carrera.split('|')[0],
                                      area=dc.carrera.split('|')[1] )
                                 for i,dc in enumerate(docente.direcciones.all()) ]
            request.session['carreras_director'] = carreras_director
        #
        # Se trata de un docente que es PAR ACADEMICO
        #
        elif docente.parAcademico:
            # TODO: Codigo horrible. Refactorizar con los nuevos metodos de DocentePeriodoAcademico
            if 'ACE' in docente.get_areas():
                cuestionarios_pares_academicos = periodoEvaluacion.cuestionarios.filter(
                    informante__tipo='ParAcademicoIdiomas')
            else:
                cuestionarios_pares_academicos = periodoEvaluacion.cuestionarios.filter(
                    informante__tipo='ParAcademico')
            request.session['cuestionarios_pares_academicos'] = cuestionarios_pares_academicos
            areas_periodo = periodoEvaluacion.areasSGA.values_list('siglas', flat=True)
            carreras_pares_academicos = docente.asignaturasDocente.filter(asignatura__area__in=areas_periodo).values(
                'asignatura__carrera','asignatura__area').distinct()
            # Al final un diccionario de carreras del para academico en la session 
            carreras_pares_academicos = [ dict(num_carrera=i, nombre=c['asignatura__carrera'], 
                                               area=c['asignatura__area'])
                                          for i,c in enumerate(carreras_pares_academicos) ]
            carreras_aux = [ c['nombre'] for c in carreras_pares_academicos ]
            if docente.carrera and docente.carrera not in carreras_aux:
                # En docente solo existe el nombre de la carrera
                carreras_pares_academicos.append(dict(num_carrera=len(carreras_pares_academicos), 
                                                      nombre=docente.carrera, 
                                                      area=''))
            aux_carreras = [c['nombre'] for c in carreras_pares_academicos]
            aux_areas = [c['area'] for c in carreras_pares_academicos]
            # Por cuestiones de los Pares Academicos de Frances y Ruso
            if 'ACE' in aux_areas and 'Curso de Ingles' in aux_carreras:
                carreras_pares_academicos.append(dict(num_carrera=len(carreras_pares_academicos), 
                                                      nombre=u'Curso de Francés', 
                                                      area='ACE'))
                carreras_pares_academicos.append(dict(num_carrera=len(carreras_pares_academicos), 
                                                      nombre=u'Curso de Ruso', 
                                                      area='ACE'))
            request.session['carreras_pares_academicos'] = carreras_pares_academicos

    except DocentePeriodoAcademico.DoesNotExist:
        noDocente = True

    # El usuario no es Estudiante ni Docente en el Periodo Academico Actual
    if noEstudiante and noDocente:
        return redirect('/login/')
    return render_to_response('app/index.html', datos, context_instance=RequestContext(request))


@login_required(login_url='/login/')
def estudiante_asignaturas_docentes(request, num_carrera):
    """ Evaluaciones de los ESTUDIANTES """
    estudiante = request.session['estudiante']
    carrera = [c['nombre'] for c in request.session['carreras_estudiante']
               if c['num_carrera'] == int(num_carrera) ][0]
    area = [c['area'] for c in request.session['carreras_estudiante']
               if c['num_carrera'] == int(num_carrera) ][0]
    request.session['carrera'] = carrera
    request.session['area'] = area
    request.session['num_carrera'] = num_carrera
    # Obtenemos los id de las AsignaturasDocente
    ids = estudiante.asignaturasDocentesEstudiante.filter(
        asignaturaDocente__asignatura__carrera=carrera, asignaturaDocente__asignatura__area=area).values_list(
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
            if a.area == 'MED':
                cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all()
                                 if c.informante.tipo == 'EstudianteMED']                                 
            elif a.area == 'ACE':
                cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'EstudianteIdiomas']
            # Modalidad Prescencial
            elif a.semestre == u"1":
                cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'EstudianteNovel']
                # Si tienen los mismos cuestionarios que el resto de semestres
                # TODO: ?
                #if len(cuestionarios) == 0:
                #    cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() 
                #                 if c.informante.tipo == 'Estudiante']
            else:
                cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'Estudiante']

            estudianteAsignaturaDocente = estudiante.asignaturasDocentesEstudiante.get(
                asignaturaDocente__asignatura=a, asignaturaDocente__docente=d
                )
            # Si ya ha contestado todos los cuestionario disponibles para el docente 'd'
            num_evaluaciones = estudianteAsignaturaDocente.evaluaciones.count()
            if num_evaluaciones > 0 and num_evaluaciones == len(cuestionarios):
                diccionario['docentes'].append(dict(docente=d, evaluado=True))
            else:
                # Si no ha contestado aun todos los cuestionario disponibles para el docente 'd'
                diccionario['docentes'].append(dict(docente=d, evaluado=False))
        asignaturas_docentes.append(diccionario)
    # Para regresar posteriormente a esta vista
    request.session['num_carrera'] = str(num_carrera)
    title = u"{0}>>{1}".format(area,carrera)
    datos = dict(asignaturas_docentes=asignaturas_docentes, title=title)
    return render_to_response("app/asignaturas_docentes.html", datos, context_instance=RequestContext(request))


def pares_academicos_docentes(request, num_carrera):
    """ El Par Academico de la Carrera elije el docente a evaluar """
    par_academico = request.session['docente']
    carrera = [c['nombre'] for c in request.session['carreras_pares_academicos']
               if c['num_carrera'] == int(num_carrera)][0]
    area = [c['area'] for c in request.session['carreras_pares_academicos']
               if c['num_carrera'] == int(num_carrera)][0]
    request.session['carrera'] = carrera
    request.session['area'] = area
    request.session['num_carrera'] = num_carrera
    # Obtenemos los id de los Docentes que dictan Asignaturas en la carrera seleccionada
    ids_docentes = AsignaturaDocente.objects.filter(
        docente__periodoAcademico=Configuracion.getPeriodoAcademicoActual(),
        asignatura__carrera=carrera,
        asignatura__area=area).values_list(
        'docente__id', flat=True).distinct()
    # Se agregan tambien los docentes que no tengan Asignaturas pero que pertenezcan a la Carrera
    docentes = DocentePeriodoAcademico.objects.filter(
        Q(periodoAcademico=Configuracion.getPeriodoAcademicoActual()) and
        (Q(id__in=ids_docentes) or Q(carrera=carrera))).order_by(
        'usuario__last_name', 'usuario__first_name')
    docentes_evaluaciones = list()
    cuestionarios_pares_a = request.session['cuestionarios_pares_academicos']
    for d in docentes:
        # Cuestionarios disponibles ya han sido evaluados? Forma pythonica de comparar, contar y sumar
        cuestionarios_evaluados = sum([e.cuestionario in cuestionarios_pares_a for e in d.evaluaciones.all()])
        # Compara cuestionarios evaluados con cuestionarios establecidos
        if cuestionarios_evaluados >= len(cuestionarios_pares_a):
            docentes_evaluaciones.append(dict(docente=d, evaluado=True))
        else:
            docentes_evaluaciones.append(dict(docente=d, evaluado=False))
    docentes_evaluaciones.sort(
        lambda x,y: cmp(x['docente'].usuario.first_name, y['docente'].usuario.first_name) or
        cmp(x['docente'].usuario.last_name, y['docente'].usuario.last_name)
        )
    title = u"{0}>>{1}".format(area, carrera)
    datos = dict(docentes_evaluaciones=docentes_evaluaciones, title=title)
    return render_to_response('app/pares_academicos_docentes.html', datos, context_instance=RequestContext(request))


def director_docentes(request, num_carrera):
    """ El  Director de Carrera elije los docentes a evaluar """
    director_carrera = request.session['director_carrera']
    carrera = [c['nombre'] for c in request.session['carreras_director']
               if c['num_carrera'] == int(num_carrera)][0]
    area = [c['area'] for c in request.session['carreras_director']
               if c['num_carrera'] == int(num_carrera)][0]
    request.session['carrera'] = carrera
    request.session['area'] = area
    request.session['num_carrera'] = num_carrera
    # Obtenemos los id de los Docentes que dictan Asignaturas en la carrera seleccionada
    ids_docentes = AsignaturaDocente.objects.filter(
        docente__periodoAcademico=Configuracion.getPeriodoAcademicoActual(),
        asignatura__carrera=carrera,
        asignatura__area=area).values_list(
        'docente__id', flat=True).distinct()
    
    # Se agregan también los docentes que no tengan Asignaturas pero que pertenezcan a la Carrera
    docentes = DocentePeriodoAcademico.objects.filter(
        Q(periodoAcademico=Configuracion.getPeriodoAcademicoActual()) and
        (Q(id__in=ids_docentes) or Q(carrera=carrera))).order_by(
        'usuario__last_name', 'usuario__first_name')
    direccion = DireccionCarrera.objects.get(carrera=u'{0}|{1}'.format(carrera, area))
    docentes_evaluaciones = list()
    cuestionarios = request.session['cuestionarios_directivos']
    for d in docentes:
        # Cuestionarios disponibles ya han sido evaluados? Forma pythonica de comparar, contar y sumar
        cuestionarios_evaluados = sum([e.cuestionario in cuestionarios for e in d.evaluaciones.all()])
        # Compara cuestionarios evaluados con cuestionarios establecidos
        if cuestionarios_evaluados >= len(cuestionarios):
            docentes_evaluaciones.append(dict(docente=d, evaluado=True))
        else:
            docentes_evaluaciones.append(dict(docente=d, evaluado=False))
    docentes_evaluaciones.sort(
        lambda x,y: cmp(x['docente'].usuario.first_name, y['docente'].usuario.first_name) or
        cmp(x['docente'].usuario.last_name, y['docente'].usuario.last_name)
        )
    title = u"{0}>>{1}".format(area, carrera)
    datos = dict(docentes_evaluaciones=docentes_evaluaciones, direccion=direccion,title=title)
    return render_to_response('app/director_docentes.html', datos, context_instance=RequestContext(request))


def encuestas(request, id_docente, id_asignatura=0, id_tinformante=0, id_cuestionario=0):
    """ 
    Lista las encuestas para los informantes en el presente periodo de evaluación
    @param id_docente: Docente a ser evaluado
    @param id_asignatura: Asignatura que dicta el docente a evaluar 
    @param id_informante: Id Tipo Informante 1 Estudiante, 5 Docente, 6 Directivo 
    @param id_cuestionario: Solo en el caso de cuestionarios para docentes
    """
    datos = dict()
    title=''
    periodoEvaluacionActual = Configuracion.getPeriodoEvaluacionActual()
    cuestionarios = []
    periodo_finalizado = False
    periodo_no_iniciado = False
    # Periodo no iniciado aun
    if periodoEvaluacionActual.noIniciado():
        periodo_no_iniciado = True
    # Periodo Vigente
    elif periodoEvaluacionActual.vigente():
        #
        # Ha ingresado como ESTUDIANTE
        #
        if id_tinformante == '1':
            estudiante = request.session['estudiante']
            # Se maneja las siglas del Area en la session
            area = request.session['area']
            carrera = request.session['carrera']
            asignaturaDocente = AsignaturaDocente.objects.get(docente__id=id_docente, asignatura__id=id_asignatura)
            estudianteAsignaturaDocente = EstudianteAsignaturaDocente.objects.get(
                estudiante=estudiante, asignaturaDocente=asignaturaDocente)
            request.session['estudianteAsignaturaDocente'] = estudianteAsignaturaDocente
            title = u"{0}>>{1}>>{2}>>{3}".format(area, carrera, asignaturaDocente.asignatura.nombre,
                                                 asignaturaDocente.docente) 
            if asignaturaDocente.asignatura.area == 'MED':
                cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all()
                                 if c.informante.tipo == 'EstudianteMED']                                 
            # Estudiante (Asignatura) del Instituto de Idiomas
            elif asignaturaDocente.asignatura.area == "ACE":
                cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all() 
                                 if c.informante.tipo == 'EstudianteIdiomas']
            # Estudiante del Primer Semestre
            elif asignaturaDocente.asignatura.semestre == u"1":
                cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all() 
                                 if c.informante.tipo == 'EstudianteNovel']
                # Si no existen cuestionarios especificos para el Primer Semestre. 
                # Se usan los mismos cuestionarios de los otros semestres
                if len(cuestionarios) == 0:
                    cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all() 
                                     if c.informante.tipo == 'Estudiante']
            # Estudiante del segundo semestre en adelante
            else:
                cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all() 
                             if c.informante.tipo == 'Estudiante']
            # Si ya ha contestado todos los cuestionario disponibles
            # Cuestionarios disponibles ya tienen su evaluación? Forma pythonica de comparar, contar y sumar
            evaluados = sum([e.cuestionario in cuestionarios for e in estudianteAsignaturaDocente.evaluaciones.all()])
            # Compara cuestionarios evaluados con cuestionarios establecidos
            if evaluados >= len(cuestionarios):
                return redirect('/estudiante/asignaturas/docentes/' + request.session['num_carrera'])
        #
        # Ha ingresado como docente y es DIRECTOR DE CARRERA
        #
        elif id_tinformante == '6': #Tambien DirectorIdiomas 
            # Se maneja las siglas del Area en la sesion
            director_carrera = request.session['director_carrera']
            area = request.session.get('area', None)
            carrera = request.session.get('carrera', None)
            docente_evaluar = DocentePeriodoAcademico.objects.get(id=id_docente)
            request.session['docente_evaluar'] = docente_evaluar
            title = u"{0}>>{1}>>Coordinador: {2}".format(area, carrera, director_carrera) 
            cuestionarios = request.session['cuestionarios_directivos']
            datos.update(dict(docente_evaluar=docente_evaluar))
            # Cuestionarios disponibles ya han sido evaluados? Forma pythonica de comparar, contar y sumar
            evaluados = sum([e.cuestionario in cuestionarios for e in docente_evaluar.evaluaciones.all()])
            # Compara cuestionarios evaluados con cuestionarios establecidos
            if evaluados >= len(cuestionarios):
                return redirect('/director/docentes/' + request.session['num_carrera'])
        #
        # Ha ingresado como docente y es PAR ACADEMICO
        #
        elif id_tinformante == '10': #Tambien ParAcademicoIdiomas
            # Se maneja las siglas del Area en la sesion
            par_academico = request.session['docente']
            area = request.session.get('area', None)
            carrera = request.session.get('carrera', None)
            docente_evaluar = DocentePeriodoAcademico.objects.get(id=id_docente)
            request.session['docente_evaluar'] = docente_evaluar
            title = u"{0}>>{1}>>Par Académico: {2}".format(area, carrera, par_academico) 
            cuestionarios = request.session['cuestionarios_pares_academicos']
            datos.update(dict(docente_evaluar=docente_evaluar))
            # Cuestionarios disponibles ya han sido evaluados? Forma pythonica de comparar, contar y sumar
            evaluados = sum([e.cuestionario in cuestionarios for e in docente_evaluar.evaluaciones.all()])
            # Compara cuestionarios evaluados con cuestionarios establecidos
            if evaluados >= len(cuestionarios):
                return redirect('/pares_academicos/docentes/' + request.session['num_carrera'])
        #
        # Es DOCENTE
        #
        elif id_tinformante == '5' and id_cuestionario: # Tambien DocenteIdiomas
            # Se filtra la peticion de encuestas de autoevaluacion de docentes desde el index
            # por este controlador para reutilizar la validación de vigencia de PeridoEvaluacion
            return redirect('/encuesta/responder/' + id_cuestionario) 
    #Si ha expirado el periodo de Evaluacion
    elif periodoEvaluacionActual.finalizado():
        periodo_finalizado = True
    datos.update(dict(cuestionarios=cuestionarios, title=title, 
                 periodo_no_iniciado=periodo_no_iniciado, periodo_finalizado=periodo_finalizado))
    return render_to_response("app/encuestas.html", datos, context_instance=RequestContext(request))


def encuesta_responder(request, id_cuestionario):
    datos = dict()
    cuestionario = Cuestionario.objects.get(id=id_cuestionario)
    evaluacion = Evaluacion()
    #
    # Encuesta dirigida a ESTUDIANTES
    #
    ###info_estudiante = ('EstudianteNovel', 'Estudiante', 'EstudianteMED', 'EstudianteIdiomas')
    if cuestionario.informante.tipo.startswith('Estudiante'):
        area = request.session['area']
        carrera = request.session['carrera']
        estudianteAsignaturaDocente = request.session['estudianteAsignaturaDocente']
        evaluacion.estudianteAsignaturaDocente = estudianteAsignaturaDocente
        title = u"{0}>>{1}>>{2}>>{3}".format(area, carrera, 
                                             estudianteAsignaturaDocente.asignaturaDocente.asignatura.nombre,
                                             estudianteAsignaturaDocente.asignaturaDocente.docente
                                             )
        datos.update(dict(asignaturaDocente=estudianteAsignaturaDocente.asignaturaDocente))
    #
    # Encuesta para DIRECTORES DE CARRERA
    #
    elif cuestionario.informante.tipo.startswith('Directivo'): 
        area = request.session['area']
        carrera = request.session['carrera']
        director_carrera = request.session['director_carrera']
        docente_evaluar = request.session['docente_evaluar']
        title = u"{0}>>{1}>>{2}".format(area, carrera, docente_evaluar)
        evaluacion.directorCarrera = director_carrera
        evaluacion.carreraDirector = u'{0}|{1}'.format(carrera, area)
        evaluacion.docentePeriodoAcademico = docente_evaluar
    #
    # Encuesta para PARES ACADEMICOS 
    #
    elif cuestionario.informante.tipo.startswith('ParAcademico'): 
        area = request.session['area']
        carrera = request.session['carrera']
        par_academico = request.session['docente']
        docente_evaluar = request.session['docente_evaluar']
        title = u"{0}>>{1}>>{2}".format(area, carrera, docente_evaluar)
        evaluacion.parAcademico = par_academico
        evaluacion.docentePeriodoAcademico = docente_evaluar
    #
    # Encuesta para Autoevaluacion de DOCENTES
    #
    elif cuestionario.informante.tipo.startswith('Docente'): 
        # En caso de que el docente sea a la vez director de carrera
        docente = None
        if request.session.get('director_carrera', None):
            docente = request.session['docente']
        elif request.session.get('docente', None):
            docente = request.session['docente']
        evaluacion.docentePeriodoAcademico = docente
        # Areas en las que dicta clases el docente
        areas_docente = AsignaturaDocente.objects.filter(docente=docente).values_list('asignatura__area', flat=True).distinct()
        areas_docente = ','.join(areas_docente)
        # Carreras en las que dicta clases el docente
        carreras_docente = AsignaturaDocente.objects.filter(docente=docente).values_list(
            'asignatura__carrera', flat=True).distinct()
        carreras_docente = ','.join(carreras_docente)
        request.session['areas_docente'] = areas_docente
        request.session['carreras_docente'] = carreras_docente
        title = u'{0}>>{1}>>{2}'.format(areas_docente, carreras_docente, docente)

    evaluacion.fechaInicio = datetime.now().date()
    evaluacion.horaInicio = datetime.now().time()
    evaluacion.cuestionario = cuestionario
    request.session['evaluacion'] = evaluacion
    fecha = datetime.now()
    datos.update(dict(cuestionario=cuestionario, title=title, fecha=fecha))
    # Por cuestion del formulario
    datos.update(csrf(request))    
    return render_to_response("app/encuesta_responder.html", datos, context_instance=RequestContext(request))


def encuesta_grabar(request):
    datos = dict(num_carrera=request.session.get('num_carrera', None))
    evaluacion = request.session.get('evaluacion', None)
    if not evaluacion:
        return render_to_response('app/encuesta_finalizada.html', datos, context_instance=RequestContext(request))     
    #
    # Encuesta dirigida a ESTUDIANTES
    #
    ###info_estudiante = ('EstudianteNovel', 'Estudiante', 'EstudianteMED', 'EstudianteIdiomas')
    if evaluacion.cuestionario.informante.tipo.startswith('Estudiante'):
    ###if request.session.get('estudianteAsignaturaDocente', None):
        estudianteAsignaturaDocente = request.session['estudianteAsignaturaDocente']
        # Si se regresa a grabar otra vez la misma encuesta
        if Evaluacion.objects.filter(estudianteAsignaturaDocente = estudianteAsignaturaDocente
                                     ).filter(cuestionario = evaluacion.cuestionario).count() > 0:
            request.session['evaluacion'] = None
            request.session['estudianteAsignaturaDocente'] = None
            return render_to_response('app/encuesta_finalizada.html',
                                  datos, context_instance=RequestContext(request))     
    #
    # Encuesta dirigida a DIRECTORES DE CARRERA 
    #
    elif evaluacion.cuestionario.informante.tipo.startswith('Directivo'):
        docente_evaluar = request.session['docente_evaluar']
        director_carrera = request.session['director_carrera']
        # Si ya ha contestado este cuestionario y se intenta grabar otra vez
        if docente_evaluar.evaluaciones.filter(cuestionario=evaluacion.cuestionario,
                                               directorCarrera=director_carrera).count() > 0:
            request.session['evaluacion'] = None
            return render_to_response('app/encuesta_finalizada.html', datos, 
                                      context_instance=RequestContext(request))     
    #
    # Encuesta dirigida a PARES ACADEMICOS 
    #
    elif evaluacion.cuestionario.informante.tipo.startswith('ParAcademico'):
        docente_evaluar = request.session['docente_evaluar']
        par_academico = request.session['docente']
        # Si ya ha contestado este cuestionario y se intenta grabar otra vez
        if docente_evaluar.evaluaciones.filter(cuestionario=evaluacion.cuestionario,
                                               parAcademico=par_academico).count() > 0:
            request.session['evaluacion'] = None
            return render_to_response('app/encuesta_finalizada.html', datos, 
                                      context_instance=RequestContext(request))     
    #
    # Encuesta dirigida a DOCENTES 
    #
    elif evaluacion.cuestionario.informante.tipo.startswith('Docente'):
        docente = request.session.get('docente', None)
        # Si ya ha contestado este cuestionario y se intenta grabar otra vez
        if docente.evaluaciones.filter(cuestionario=evaluacion.cuestionario).count() > 0:
            request.session['evaluacion'] = None
            return render_to_response('app/encuesta_finalizada.html', datos, 
                                      context_instance=RequestContext(request))     
    # Grabacion luego de las validaciones
    evaluacion.fechaFin = datetime.now().date()
    evaluacion.horaFin = datetime.now().time()
    evaluacion.save()
    for k,v in request.POST.items():
        if k.startswith('csrf'):
            continue
        if k.startswith('pregunta'):
            id_pregunta = int(k.split('-')[1])
            observaciones = None
            if Pregunta.objects.get(id=id_pregunta).observaciones:
                # Solo se graban las observaciones de las preguntas respondidas
                observaciones = request.POST['observaciones-pregunta-' + str(id_pregunta)]
            contestacion = Contestacion(pregunta=id_pregunta, respuesta=v, observaciones=observaciones)
            contestacion.evaluacion = evaluacion
            contestacion.save()
    logg.info("Nueva Evaluacion realizada: {0}".format(evaluacion))
    return render_to_response('app/encuesta_finalizada.html', datos, context_instance=RequestContext(request))


def cargar_ofertas_sga(request, periodoAcademicoId):
    """ Metodo invocado a través de Ajax. Recarga todas las ofertas """
    if not periodoAcademicoId:
        return HttpResponse("Falta Periodo Academico")
    try:
        proxy = SGA(SGAWS_USER, SGAWS_PASS)
        periodoAcademico = PeriodoAcademico.objects.get(id=periodoAcademicoId)
        ofertas_dict = proxy.ofertas_academicas(periodoAcademico.inicio, periodoAcademico.fin)
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


# =============================================================================
# Resumen de Evaluaciones en el Admin
# ==============================================================================

def resumen_evaluaciones(request):
    """
    Se invoca a través de Ajax cuendo hay un cambio en el menú del Resumen 
    """
    if request.is_ajax():
        respuesta = menu_academico_ajax(request)
        return HttpResponse(respuesta, mimetype='application/json')
    else:
        form = forms.Form()
        form.fields['periodo_academico'] = forms.ModelChoiceField(queryset=PeriodoAcademico.objects.all())
        form.fields['periodo_academico'].label = 'Periodos Academicos'
        form.fields['periodo_evaluacion'] = forms.ModelChoiceField(PeriodoEvaluacion.objects.none())
        form.fields['periodo_evaluacion'].label = 'Periodos de Evaluacion'
        form.fields['area'] = forms.ModelChoiceField(AreaSGA.objects.none())
        form.fields['carrera'] = forms.ModelChoiceField(Asignatura.objects.none())
        form.fields['semestre'] = forms.ModelChoiceField(Asignatura.objects.none())
        form.fields['paralelo'] = forms.ModelChoiceField(Asignatura.objects.none())
        periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
        datos = dict(form=form, evaluadores=periodoEvaluacion.contabilizar_evaluadores(), periodoEvaluacion=periodoEvaluacion)
        return render_to_response("admin/app/resumen_evaluaciones.html", datos)

def calcular_resumen(request):
    try:
        if request.is_ajax():
            id_periodo_evaluacion = int(request.GET['id_periodo_evaluacion'])
            area = request.GET['area']
            carrera = request.GET['carrera']
            semestre = request.GET['semestre']
            paralelo = request.GET['paralelo']
            periodoEvaluacion = PeriodoEvaluacion.objects.get(id=id_periodo_evaluacion)
            resumen = periodoEvaluacion.contabilizar_evaluaciones_estudiantes(area, carrera, semestre, paralelo)
            # Contiene: estudiantes, completados, faltantes
            return HttpResponse(simplejson.dumps(resumen), mimetype='application/json')
    except Exception, ex:
        logg.error("Error calculando resumen de evaluaciones {0}".format(ex))
        
    
def menu_academico_ajax(request):
    """
    Funcionalidad reutilizada cuando se necesita informacion académica jerárquica
    estructurada en (PeriodoAcademico, PeriodoEvaluacion, AreaSGA, carrera, semestre,
    paralelo). Utilizado generalmente en menus de reportes.
    TODO: Analizar el parametro 'siguiente' en otros casos para crear un componente mas independiente.
    """
    try:
        id_campo = request.GET['id']
        valor_campo = request.GET['valor']
        campo_siguiente = request.GET.get('siguiente',None) 
        if valor_campo == '':
            return HttpResponse('{"id": "", "valores": []}', mimetype="JSON")
        id = ""
        valores = []

        if id_campo == 'id_periodo_academico':
            request.session['periodoAcademico'] = PeriodoAcademico.objects.get(id=int(valor_campo))                
            id = 'id_periodo_evaluacion'
            objetos = PeriodoEvaluacion.objects.filter(periodoAcademico__id=int(valor_campo)).all()
            valores = [dict(id=o.id, valor=o.nombre) for o in objetos]
        elif id_campo == 'id_periodo_evaluacion':
            request.session['periodoEvaluacion'] = PeriodoEvaluacion.objects.get(id=int(valor_campo))
            id = 'id_area'
            objetos = PeriodoEvaluacion.objects.get(id=int(valor_campo)).areasSGA.all()
            valores = [dict(id=o.siglas, valor=o.nombre) for o in objetos]
        elif id_campo == 'id_area':
            # request.session['area'] = AreaSGA.objects.get(siglas=valor_campo)
            request.session['area'] = valor_campo
            id = 'id_carrera'
            objetos = EstudianteAsignaturaDocente.objects.filter(
                estudiante__periodoAcademico=request.session['periodoAcademico']).filter(
                asignaturaDocente__asignatura__area=valor_campo).values_list(
                'asignaturaDocente__asignatura__carrera', flat=True).distinct()
            objetos = sorted(objetos)
            for o in objetos:
                carrera = o.encode('utf-8') if isinstance(o, unicode) else o
                valores.append(dict(id=carrera, valor=carrera))
        elif id_campo == 'id_carrera':
            # Dos bifuraciones dependiendo del menú
            request.session['carrera'] = valor_campo
            id = campo_siguiente
            if campo_siguiente == 'id_semestre':
                objetos = EstudianteAsignaturaDocente.objects.filter(
                    estudiante__periodoAcademico=request.session['periodoAcademico']).filter(
                    asignaturaDocente__asignatura__area=request.session['area']).filter(
                    asignaturaDocente__asignatura__carrera=valor_campo).values_list(
                    'asignaturaDocente__asignatura__semestre', flat=True).distinct()
                objetos = sorted(objetos)
                for o in objetos:
                    semestre = o.encode('utf-8') if isinstance(o, unicode) else o
                    valores.append(dict(id=semestre, valor=semestre))
            elif campo_siguiente == 'id_docente':
                objetos = AsignaturaDocente.objects.filter(
                    docente__periodoAcademico=request.session['periodoAcademico']).filter(
                    asignatura__area=request.session['area']).filter(
                    asignatura__carrera=valor_campo)
                docentes = set([o.docente for o in objetos])
                valores = [dict(id=d.id, valor=d.__unicode__()) for d in docentes]
                
        elif id_campo == 'id_semestre':
            request.session['semestre'] = valor_campo
            id = 'id_paralelo'
            objetos = EstudianteAsignaturaDocente.objects.filter(
                estudiante__periodoAcademico=request.session['periodoAcademico']).filter(
                asignaturaDocente__asignatura__area=request.session['area']).filter(
                asignaturaDocente__asignatura__carrera=request.session['carrera']).filter(
                asignaturaDocente__asignatura__semestre=valor_campo).values_list(
                'asignaturaDocente__asignatura__paralelo', flat=True).distinct()
            objetos = sorted(objetos)
            for o in objetos:
                paralelo = o.encode('utf-8') if isinstance(o, unicode) else o
                valores.append(dict(id=paralelo, valor=paralelo))

        resultado = {'id':id, 'valores':valores}
        return simplejson.dumps(resultado)
    except Exception, ex:
        logg.error("Error en menu_academico_ajax: " + str(ex))
        return ""
    
    
# ==============================================================================
# Calcular y mostrar resultados de evaluaciones
# ==============================================================================

def resultados_carrera(request, num_carrera):
    datos = dict()
    try:
        # Carreras cuya direccion esta a cargo del docente
        # Almacenadas en la vista previa 'index'
        carreras_director = request.session['carreras_director']
        for cd in carreras_director:
            if cd['num_carrera'] == int(num_carrera):
                carrera = cd['nombre']
                area_siglas = cd['area']
                break
        else:
            logg.error('No hay carreras para este docente director')
        request.session['carrera'] = carrera
        request.session['area'] = area_siglas
        # Objeto AreaSGA 
        area = AreaSGA.objects.get(siglas=area_siglas)
        periodoAcademico = Configuracion.getPeriodoAcademicoActual()
        # Periodos de Evaluacion del Periodo Academico Actual 
        periodosEvaluacion = area.periodosEvaluacion.filter(periodoAcademico=periodoAcademico)
        form = forms.Form()
        # Selecciona solo los peridos de evaluacion en los que se encuentra el area del docente director
        form.fields['periodo_academico'] = forms.ModelChoiceField(
            queryset=PeriodoAcademico.objects.all()
            )
        form.fields['periodo_academico'].label = u'Periodo Académico'
        form.fields['periodo_evaluacion'] = forms.ModelChoiceField(
            queryset=PeriodoEvaluacion.objects.none()
            )
        form.fields['periodo_evaluacion'].label = 'Periodo de Evaluación'
        datos = dict(form=form, title='>> Coordinador Carrera ' + carrera )
    except Exception, ex:
        logg.error("Error :" + str(ex))
    return render_to_response("app/menu_resultados_carrera.html", datos, context_instance=RequestContext(request))


def menu_resultados_carrera(request, id_periodo_evaluacion):
    """
    Genera el menu de opciones para reportes de acuerdo al periodo de evaluacion
    y su tipo de tabulacion especificamente. Llamado con Ajax.
    """
    try:
        periodoEvaluacion=PeriodoEvaluacion.objects.get(id=id_periodo_evaluacion)
        tabulacion = Tabulacion.objects.get(periodoEvaluacion=periodoEvaluacion)
        # Para los Docentes Coordinadores de Carrera 
        if request.session.has_key('carreras_director'):
            carrera = request.session['carrera']
            area = request.session['area']
        # Para la Comision de Evaluacion (Administracion)
        else:
            area = request.GET['area']
            carrera = request.GET['carrera']
        # Especifico para el Tipo de Tabulacion - Periodo de Evaluacion
        if tabulacion.tipo == 'ESE2012':
            tabulacion = TabulacionSatisfaccion2012(periodoEvaluacion)
            form = ResultadosESE2012Form(tabulacion, area, carrera)
            formulario_formateado = render_to_string("admin/app/formulario_ese2012.html", dict(form=form))
        elif tabulacion.tipo == 'EAAD2012': 
            tabulacion = TabulacionAdicionales2012(periodoEvaluacion)
            form = ResultadosEAAD2012Form(tabulacion, area, carrera)            
            formulario_formateado = render_to_string("admin/app/formulario_eaad2012.html", dict(form=form))
        elif tabulacion.tipo == 'EDD2013':
            tabulacion = TabulacionEvaluacion2013(periodoEvaluacion)
            form = ResultadosEDD2013Form(tabulacion, area, carrera)
            formulario_formateado = render_to_string("admin/app/formulario_edd2013.html", dict(form=form))
        return HttpResponse(formulario_formateado)
    except PeriodoEvaluacion.DoesNotExist:
        logg.error(u"No Existe el Periodo de Evaluación: {0}".format(id_periodo_evaluacion))
    except Exception, ex:
        logg.error('Error en vista menu_resultados_carrera: ' + str(ex))
        

def mostrar_resultados(request):
    """
    Controlador que procesa los resultados de los diferentes tipos de Evaluaciones
    TODO: Generalizar cuando hayan grupos de evaluaciones concenientes a un mismo tipo
    """
    if not (request.POST.has_key('periodo_evaluacion') and request.POST.has_key('opciones')):
        return HttpResponse("<h2> Tiene que elegir las Opciones de Resultados </h2>")
    id_periodo = request.POST['periodo_evaluacion']
    if id_periodo == '':
        return HttpResponse("<h2> Tiene que elegir el Periodo de Evaluación </h2>")
    # Se obtiene la opcion generica para cualquier tipo de evaluacion
    opcion = request.POST['opciones']
    # Formato de presentacion de resultados
    formato = request.POST['formato']
    periodoEvaluacion=PeriodoEvaluacion.objects.get(id=int(id_periodo))
    tabulacion = periodoEvaluacion.tabulacion
    resultados = {}
    # Codigo de la carrera de acuerdo la SENESCYT
    carrera_senescyt = AsignaturaDocente.objects.filter(
        docente__periodoAcademico=tabulacion.periodoEvaluacion.periodoAcademico,
        asignatura__area=request.session['area'], asignatura__carrera=request.session['carrera']
        ).distinct().values_list('asignatura__carrera_senescyt', flat=True)[0]

    # Encuesta de Satisfaccion Estudiantil 2012 / 2013
    # ------------------------------------------------------------------------
    if tabulacion.tipo == 'ESE2012':
        tabulacion = TabulacionSatisfaccion2012(periodoEvaluacion)
        metodo =  [c[2] for c in tabulacion.calculos if c[0] == opcion][0]
        titulo = u'<h3 style="margin-bottom: 3px;"> {0} </h3> {1} <br/> <b> {2} </b> <br/>'.format(
            tabulacion.periodoEvaluacion.titulo, request.session['area'], request.session['carrera'])
        titulo += [c[3] for c in tabulacion.calculos if c[0] == opcion][0]
        # Por docente
        if opcion == 'a':
            id_docente = request.POST['docentes']
            if id_docente != '':
                titulo += u': <b>{0}</b>'.format(DocentePeriodoAcademico.objects.get(id=int(id_docente)))
                resultados = metodo(request.session['area'], request.session['carrera'], int(id_docente))
        # Por campos
        elif opcion == 'c':
            id_seccion = request.POST['campos']
            id_docente = request.POST['docentes']
            if id_seccion:
                seccion = Seccion.objects.get(id=int(id_seccion))
                titulo += u': <b>{0}</b>'.format(seccion.titulo)
                docente = None
                if id_docente:
                    docente = DocentePeriodoAcademico.objects.get(id=id_docente)
                    titulo += u'<br/> <b>{0}</b>'.format(docente)
                resultados = metodo(request.session['area'], request.session['carrera'], docente, seccion)
                if seccion.orden == 4:
                    datos = dict(resultados=resultados, titulo=titulo)
                    return render_to_response('app/imprimir_otros_ese2012.html', datos,
                                              context_instance=RequestContext(request));
        # Por indicadores
        elif opcion == 'd':
            id_pregunta = request.POST['indicadores']
            if id_pregunta != '':
                titulo += u': <b>{0}</b>'.format(Pregunta.objects.get(id=int(id_pregunta)).texto)
                resultados = metodo(request.session['area'], request.session['carrera'], int(id_pregunta))
        # Para el resto de casos
        else:
            resultados = metodo(request.session['area'], request.session['carrera'])
        if resultados:
            resultados['titulo'] = titulo
        if opcion == 'g':
            # Listado de Docentes con calificaciones 
            plantilla = 'app/imprimir_calificaciones_ese2013.html'
        else:
            plantilla = 'app/imprimir_resultados_ese2012.html'

    # Evaluacion de Actividades Adiconales a la Docencia 2011 - 2012
    # -----------------------------------------------------------------------
    if tabulacion.tipo == 'EAAD2012':
        # Nombre completo del Area para su presentacion en el reporte
        area = AreaSGA.objects.get(siglas=request.session['area']).nombre
        carrera = request.session['carrera']
        tabulacion = TabulacionAdicionales2012(periodoEvaluacion)
        metodo =  [c[2] for c in tabulacion.calculos if c[0] == opcion][0]
        if opcion == 'a':
            id_docente = request.POST['docentes']
            if id_docente != '':
                docente = DocentePeriodoAcademico.objects.get(id=int(id_docente))
                # Referencia a lo que devuelve el metodo especifico invocado sobre la instancia de Tabulacion 
                resultados = metodo(request.session['area'], request.session['carrera'], int(id_docente))
        elif opcion == 'z':
            pass
        # Para el resto de casos
        else:
            resultados = metodo(request.session['area'], request.session['carrera'])
        if resultados:
            resultados['docente'] = docente
            resultados['carrera'] = carrera
            resultados['area'] = area
        plantilla = 'app/imprimir_resultados_eaad2012.html'

    # Evaluacion del Desempenio Docente 2012 - 2013
    # ----------------------------------------------------------------------------
    if tabulacion.tipo == 'EDD2013':
        if opcion in ('c', 'd') and not request.user.is_staff:
            return HttpResponse("<h2> Ud no tiene permisos para revisar este reporte </h2>")
        codigos_filtro = {'a' : '', 'b' : 'CPF', 'c' : 'CPG', 'd' : 'PV', 'e' : 'sugerencias'}
        objeto_area = AreaSGA.objects.get(siglas=request.session['area'])
        # Nombre completo del Area para su presentacion en el reporte
        area = objeto_area.nombre
        area_siglas = request.session['area']
        carrera = request.session['carrera']
        tabulacion = TabulacionEvaluacion2013(periodoEvaluacion)
        if opcion !=  'd':
            metodo =  [c[2] for c in tabulacion.calculos if c[0] == opcion][0] 
        filtro = request.POST['filtros']
        filtro = codigos_filtro[filtro]
        if opcion == 'a':
            id_docente = request.POST['docentes']
            if id_docente != '':
                docente = DocentePeriodoAcademico.objects.get(id=int(id_docente))
                # Referencia a lo que devuelve el metodo especifico invocado sobre la instancia de Tabulacion 
                resultados = metodo(request.session['area'], request.session['carrera'], int(id_docente), filtro)
                resultados['docente'] = docente
                resultados['carrera'] = carrera
                resultados['area'] = objeto_area.nombre
        elif opcion == 'b':
            # Por Carrera
            resultados = metodo(request.session['area'], request.session['carrera'], filtro)
            resultados['carrera'] = carrera
            resultados['area'] = objeto_area.nombre
        elif opcion == 'c':
            # Por Area
            resultados = metodo(request.session['area'], filtro)
            resultados['area'] = objeto_area.nombre
        elif opcion == 'd':
            # Consolidado de Docentes por carrera
            area = request.session['area']
            carrera = request.session['carrera']
            contenido = generar_consolidado_edd2013(area, carrera, filtro, tabulacion)
            if formato == 'HTML':
                return HttpResponse(contenido)
            elif formato == 'PDF':
                archivo_pdf = generar_pdf(contenido)
                response = HttpResponse(archivo_pdf, mimetype='application/pdf')
                filename = "Consolidado_{0}".format("Carrera")
                response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
                return response
        elif opcion == 'e':
            # Listado de Docentes con calificaciones
            # clave: listado_calificaciones
            resultados = metodo(request.session['area'], request.session['carrera'])
            resultados['carrera'] = carrera
            resultados['area'] = objeto_area.nombre
        # Para el resto de casos
        #else:
            #resultados = metodo(request.session['area'], request.session['carrera'], filtro)

        # Posicion para ubicar el promedio por componente en la plantilla
        if resultados.get('promedios_componentes', None) and objeto_area.id == 6:
            # Si se trata del Instituto de Idiomas
            resultados['promedios_componentes']['CPF'].update({'fila' : 8})
            resultados['promedios_componentes']['CPG'].update({'fila' : 23})
            resultados['promedios_componentes']['PV'].update({'fila' : 29})
        elif resultados.get('promedios_componentes', None):
            # Para el resto de Areas
            resultados['promedios_componentes']['CPF'].update({'fila' : 10})
            resultados['promedios_componentes']['CPG'].update({'fila' : 27})
            resultados['promedios_componentes']['PV'].update({'fila' : 33})

        if filtro == 'sugerencias':
            # Reporte de sugerencias
            plantilla = 'app/imprimir_sugerencias_edd2013.html'
        else:
            if opcion == 'e':
                # Listado de Docentes con calificaciones para la SENESCYT
                plantilla = 'app/imprimir_calificaciones_edd2013.html'
            else:
                plantilla = 'app/imprimir_resultados_edd2013.html'

    resultados['titulo'] = u"Acta de Resultados de la {0}".format(tabulacion.periodoEvaluacion.titulo)
    # Obtenido al inicio de la bifurcacion
    resultados['carrera_senescyt'] = carrera_senescyt


    if formato == 'HTML':
        return render_to_response(plantilla, resultados, context_instance=RequestContext(request));
    elif formato == 'PDF':
        contenido = render_to_string(plantilla, resultados)
        archivo_pdf = generar_pdf(contenido)
        response = HttpResponse(archivo_pdf, mimetype='application/pdf')
        filename = "Reporte"
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        return response 


def generar_consolidado_edd2013(siglas_area, nombre_carrera, filtro, tabulacion):
    if siglas_area and nombre_carrera:
        objeto_area = AreaSGA.objects.get(siglas=siglas_area)
        aux_ids = AsignaturaDocente.objects.filter(
            docente__periodoAcademico=tabulacion.periodoEvaluacion.periodoAcademico,
            asignatura__carrera=nombre_carrera,
            asignatura__area=siglas_area
            ).values_list('docente__id', flat=True).distinct()
        # Se agregan tambien los docentes que no tengan Asignaturas pero que pertenezcan a la Carrera
        ids_docentes = DocentePeriodoAcademico.objects.filter(
            Q(periodoAcademico=tabulacion.periodoEvaluacion.periodoAcademico) and
            (Q(id__in=aux_ids) or Q(carrera=nombre_carrera))
            ).order_by('usuario__last_name', 'usuario__first_name').values_list(
            'id', flat=True
            )
        contenido = ''
        if filtro == 'sugerencias':
            # Se trata de reporte de sugerencias
            plantilla = 'app/imprimir_sugerencias_edd2013.html'
        else:
            plantilla = 'app/imprimir_resultados_edd2013.html'
        for id_docente in ids_docentes:
            docente = DocentePeriodoAcademico.objects.get(id=int(id_docente))
            # Referencia a lo que devuelve el metodo 'por_docente'  invocado sobre la instancia de Tabulacion 
            resultados = tabulacion.calculos[0][2](siglas_area, nombre_carrera, int(id_docente), filtro)
            resultados['docente'] = docente
            resultados['carrera'] = nombre_carrera
            resultados['area'] = objeto_area.nombre
            # Posicion para ubicar el promedio por componente en la plantilla
            if resultados.get('promedios_componentes', None) and objeto_area.id == 6:
                # Si se trata del Instituto de Idiomas
                resultados['promedios_componentes']['CPF'].update({'fila' : 8})
                resultados['promedios_componentes']['CPG'].update({'fila' : 23})
                resultados['promedios_componentes']['PV'].update({'fila' : 29})
            elif resultados.get('promedios_componentes', None):
                # Para el resto de Areas
                resultados['promedios_componentes']['CPF'].update({'fila' : 10})
                resultados['promedios_componentes']['CPG'].update({'fila' : 27})
                resultados['promedios_componentes']['PV'].update({'fila' : 33})
            aux = render_to_string(plantilla, resultados)
            contenido += aux
    return contenido
    
def generar_pdf(contenido):
    """ 
    Toma como parametro un contenido string, lo transforma a PDF 
    y devuelve el resultado en un archivo.
    """
    #stringIO = StringIO(contenido.encode('UTF-8'))
    tmpdir = os.path.abspath(os.path.dirname(__file__) + '../../tmp/')
    #archivo = open('%s%s' % (tmpdir, nombre_pdf), 'wb')
    archivo = StringIO.StringIO()
    pisa.CreatePDF(contenido.encode('UTF-8'), archivo)
    archivo.seek(0)
    #pdf = pisaDocument(stringIO, archivo)
    #archivo.close()
    return archivo

def resultados(request):
    """
    Manejo de resultados para los administradores
    """
    datos = dict(form=ResultadosForm())
    return render_to_response('admin/app/menu_resultados.html', datos, context_instance=RequestContext(request))
    
