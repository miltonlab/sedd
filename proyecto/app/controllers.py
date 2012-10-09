# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms.forms import NON_FIELD_ERRORS
from django.contrib import messages

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
from proyecto.app.models import Asignatura
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import PeriodoEvaluacion
from proyecto.app.models import Tabulacion
from proyecto.app.models import TabulacionSatisfaccion2012
from proyecto.app.models import OfertaAcademicaSGA
from proyecto.app.models import AreaSGA
from proyecto.app.forms import ResultadosESE2012Form
from proyecto.app.forms import ResultadosForm

from proyecto.tools.sgaws.cliente import SGA
from proyecto.settings import SGAWS_USER, SGAWS_PASS

from datetime import datetime
from django import forms
from django.utils import simplejson

import logging
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
    try:
        # Se obtiene solo las siglas de las areas del periodo de evaluación
        areas_periodo = periodoEvaluacion.areasSGA.values_list('siglas', flat=True)
        # Se trata de un Estudiante
        estudiante = EstudiantePeriodoAcademico.objects.get(periodoAcademico=periodoAcademico, usuario=usuario)
        # solo las carreras que están dentro de las areas asignadas al periodo de evaluación
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
        # Se trata de un Docente 
        docente = DocentePeriodoAcademico.objects.get(periodoAcademico=periodoAcademico, usuario=usuario)
        request.session['docente'] = docente
        periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
        cuestionarios_docente = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'Docente']
        request.session['cuestionarios_docente'] = cuestionarios_docente
        # Si es coordinador se colocan las carreras del docente en la session
        if docente.esCoordinador:
            carreras_docente = docente.asignaturasDocente.values('asignatura__carrera','asignatura__area').distinct()
            carreras_docente = [ dict(num_carrera=i, nombre=c['asignatura__carrera'],area=c['asignatura__area'])
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
            elif a.area == "ACE":
                cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'InstitutoIdiomas']
            # Modalidad Presecial
            elif a.semestre == u"1":
                cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'EstudianteNovel']
                # Si tienen los mismos cuestionarios que el resto de semestres
                if len(cuestionarios) == 0:
                    cuestionarios = [c for c in periodoEvaluacion.cuestionarios.all() 
                                 if c.informante.tipo == 'Estudiante']
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


def encuestas(request, id_asignatura, id_docente):
    # Se maneja las siglas del Area en la sesion
    area = request.session['area']
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
            if asignaturaDocente.asignatura.area == 'MED':
                cuestionarios = [c for c in periodoEvaluacionActual.cuestionarios.all()
                                 if c.informante.tipo == 'EstudianteMED']                                 
            
            # Estudiante (Asignatura) del Instituto de Idiomas
            elif asignaturaDocente.asignatura.area == "ACE":
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
    title = u"{0}>>{1}>>{2}>>{3}".format(area,carrera, asignaturaDocente.asignatura.nombre, asignaturaDocente.docente) 
    datos = dict(cuestionarios=cuestionarios, title=title, 
                 periodo_no_iniciado=periodo_no_iniciado, periodo_finalizado=periodo_finalizado)
    return render_to_response("app/encuestas.html", datos, context_instance=RequestContext(request))


def encuesta_responder(request, id_cuestionario):
    area = request.session['area']
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
    title = u"{0}>>{1}>>{2}>>{3}".format(area,carrera,
                                        estudianteAsignaturaDocente.asignaturaDocente.asignatura.nombre,
                                        estudianteAsignaturaDocente.asignaturaDocente.docente)
    fecha = datetime.now()
    # Para una mejor extraccion de los datos de la asignatura se agrega el ultimo elemento
    datos = dict(cuestionario=cuestionario, title=title, 
                 asignaturaDocente=estudianteAsignaturaDocente.asignaturaDocente,
                 fecha=fecha)
    # Por cuestion del formulario
    datos.update(csrf(request))    
    return render_to_response("app/encuesta_responder.html", datos, context_instance=RequestContext(request))


def encuesta_grabar(request):
    evaluacion = request.session['evaluacion']
    estudianteAsignaturaDocente = request.session['estudianteAsignaturaDocente']
    datos = dict(num_carrera=request.session['num_carrera'])
    # Si se regresa a grabar otra vez la misma encuesta
    if not evaluacion or Evaluacion.objects.filter(
        estudianteAsignaturaDocente = estudianteAsignaturaDocente).filter(
        cuestionario = evaluacion.cuestionario).count() > 0:
        request.session['evaluacion'] = None
        request.session['estudianteAsignaturaDocente'] = None
        return render_to_response('app/encuesta_finalizada.html',
                                  datos, context_instance=RequestContext(request))     
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
        datos = dict(form=form)
        return render_to_response("admin/app/resumen_evaluaciones.html", datos)

def calcular_resumen(request):
    if request.is_ajax():
        id_periodo_evaluacion = int(request.GET['id_periodo_evaluacion'])
        area = request.GET['area']
        carrera = request.GET['carrera']
        semestre = request.GET['semestre']
        paralelo = request.GET['paralelo']
        periodoEvaluacion = PeriodoEvaluacion.objects.get(id=id_periodo_evaluacion)
        resumen = periodoEvaluacion.contabilizar_evaluaciones(area, carrera, semestre, paralelo)
        # Contiene: estudiantes, completados, faltantes
        return HttpResponse(simplejson.dumps(resumen), mimetype='application/json')        
        
    
def menu_academico_ajax(request):
    """
    Funcionalidad reutilizada cuando se necesita información académica jerárquica
    estructurada en (PeriodoAcademico, PeriodoEvaluacion, AreaSGA, carrera, semestre,
    paralelo). Utilizado generalmente en menus de reportes.
    TODO: Analizar el parámetro 'siguiente' en más casos para crear un componente más independiente.
    """
    try:
        id_campo = request.GET['id']
        valor_campo = request.GET['valor']
        campo_siguiente = request.GET['siguiente']
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
            for o in objetos:
                carrera = o.encode('utf-8') if isinstance(o, unicode) else o
                valores.append(dict(id=carrera, valor=carrera))
        elif id_campo == 'id_carrera':
            request.session['carrera'] = valor_campo
            id = campo_siguiente
            if campo_siguiente == 'id_semestre':
            ###id = 'id_semestre'
                objetos = EstudianteAsignaturaDocente.objects.filter(
                    estudiante__periodoAcademico=request.session['periodoAcademico']).filter(
                    asignaturaDocente__asignatura__area=request.session['area']).filter(
                    asignaturaDocente__asignatura__carrera=valor_campo).values_list(
                    'asignaturaDocente__asignatura__semestre', flat=True).distinct()
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
            for o in objetos:
                paralelo = o.encode('utf-8') if isinstance(o, unicode) else o
                valores.append(dict(id=paralelo, valor=paralelo))

        resultado = {'id':id, 'valores':valores}
        return simplejson.dumps(resultado)
    except Exception, ex:
        logg.error("error ajax: " + str(ex))
        return ""
    
    
# ==============================================================================
# Calcular y mostrar resultados de evaluaciones
# ==============================================================================

def resultados_carrera(request, id_docente):
    """
    Consulta los docnetes que pertenece a la misma carrera del docente coordinador (id_docente)
    """
    try:
        periodoAcademico = Configuracion.getPeriodoAcademicoActual()
        area_siglas, carrera = AsignaturaDocente.objects.filter(
                docente__id=id_docente, docente__periodoAcademico=periodoAcademico).distinct(
                ).values_list('asignatura__area','asignatura__carrera')[0]
        area = AreaSGA.objects.get(siglas=area_siglas)
        request.session['carrera'] = carrera
        request.session['area'] = area_siglas
        periodosEvaluacion = area.periodosEvaluacion.filter(periodoAcademico=periodoAcademico)
        # Ids de los docentes de la carrera
        form = forms.Form()
        # Selecciona solo los peridos de evaluacion en los que se encuentra el area del docente
        # y a su vez que estén dentro del periodo académico actual.  
        form.fields['periodo_evaluacion'] = forms.ModelChoiceField(
            queryset=area.periodosEvaluacion.filter(periodoAcademico=periodoAcademico)
            )
        form.fields['periodo_evaluacion'].label = 'Periodo de Evaluación'
        ### ids_docentes = set([ad.docente.id for ad in AsignaturaDocente.objects.filter(
        #    asignatura__carrera=carrera, asignatura__area=area)])
        ### form.fields['docente'] = forms.ModelChoiceField(queryset=DocentePeriodoAcademico.objects.filter(id__in=ids_docentes))        
        datos = dict(form=form, title='>> Coordinador Carrera ' + carrera )
    except Exception, ex:
        logg.error("Error :", str(ex))
    return render_to_response("app/menu_resultados_carrera.html", datos, context_instance=RequestContext(request))


def menu_resultados_carrera(request, id_periodo_evaluacion):
    """
    Genera el menú de opciones para reportes de acuerdo al periodo de evaluacion
    y su tipo de tabulación especificamente. Llamado con Ajax.
    """
    try:
        periodoEvaluacion=PeriodoEvaluacion.objects.get(id=id_periodo_evaluacion)
        tabulacion = Tabulacion.objects.get(periodoEvaluacion=periodoEvaluacion)
        if tabulacion.tipo == 'ESE2012':
            tabulacion = TabulacionSatisfaccion2012(periodoEvaluacion)
            # TODO: Un docente puede ser coordinador de mas de un carrera ?
            area = ''
            carrera = ''
            # Para los Docentes Coordinadores de Carrera 
            if request.session.has_key('carreras_docente'):
                carreras_docente = request.session['carreras_docente']
                carrera = carreras_docente[0]['nombre']
                area = carreras_docente[0]['area']
            # Para la Comisión de Evaluación
            else:
                area = request.GET['area']
                carrera = request.GET['carrera']
            form = ResultadosESE2012Form(tabulacion, area, carrera)
            formulario_formateado = render_to_string("admin/app/formulario_ese2012.html", dict(form=form))
            #return HttpResponse(form.as_table())
            return HttpResponse(formulario_formateado)
        
    except PeriodoEvaluacion.DoesNotExist:
        logg.error(u"No Existe el Periodo de Evaluación: {0}".format(id_periodo_evaluacion))
    except Exception, ex:
        logg.error('Error: '+str(ex))
        

def mostrar_resultados(request):
    if not (request.POST.has_key('periodo_evaluacion') and request.POST.has_key('opciones')):
        return HttpResponse("<h2> Tiene que elegir las Opciones de Resultados </h2>")
    id_periodo = request.POST['periodo_evaluacion']
    if id_periodo == '':
        return HttpResponse("<h2> Tiene que elegir el Periodo de Evaluación </h2>")
    opcion = request.POST['opciones']
    periodoEvaluacion=PeriodoEvaluacion.objects.get(id=int(id_periodo))
    tabulacion = periodoEvaluacion.tabulacion
    if tabulacion.tipo == 'ESE2012':
        # Tipo específico de Tabulación
        tabulacion = TabulacionSatisfaccion2012(periodoEvaluacion)
        metodo =  [c[2] for c in tabulacion.calculos if c[0] == opcion][0]
        titulo = request.session['area'] + '<br/> <b>' + request.session['carrera'] + '</b><br/>'
        titulo += [c[3] for c in tabulacion.calculos if c[0] == opcion][0]
        # Por docente
        resultados = {}
        if opcion == 'a':
            id_docente = request.POST['docentes']
            if id_docente != '':
                titulo += u': <b>{0}</b>'.format(DocentePeriodoAcademico.objects.get(id=int(id_docente)))
                resultados = metodo(request.session['area'], request.session['carrera'], int(id_docente))
        elif opcion == 'c':
            id_seccion = request.POST['campos']
            if id_seccion != '':
                seccion = Seccion.objects.get(id=int(id_seccion))
                titulo += u': <b>{0}</b>'.format(seccion.titulo)
                resultados = metodo(request.session['area'], request.session['carrera'], int(id_seccion))
                if seccion.orden == 4:
                    datos = dict(resultados=resultados, titulo=titulo)
                    return render_to_response('app/imprimir_otros_ese2012.html', datos,
                                              context_instance=RequestContext(request));
        elif opcion == 'd':
            id_pregunta = request.POST['indicadores']
            if id_pregunta != '':
                titulo += u': <b>{0}</b>'.format(Pregunta.objects.get(id=int(id_pregunta)).texto)
                resultados = metodo(request.session['area'], request.session['carrera'], int(id_pregunta))
        # Para el resto de casos
        else:
            resultados = metodo(request.session['area'], request.session['carrera'])
        resultados['titulo'] = titulo

        return render_to_response('app/imprimir_resultados_ese2012.html', resultados,
                                  context_instance=RequestContext(request));


def resultados(request):
    """
    Manejo de resultados para los administradores
    """
    datos = dict(form=ResultadosForm())
    return render_to_response('admin/app/menu_resultados.html', datos, context_instance=RequestContext(request))
    
