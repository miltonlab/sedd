# -*- coding: utf-8 -*-
# Para ejecutar el modulo de manera independiente
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'proyecto.settings'

from proyecto.app.models import EstudianteAsignaturaDocente
from proyecto.app.models import EstudiantePeriodoAcademico
from proyecto.app.models import AsignaturaDocente
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import PeriodoEvaluacion
from proyecto.app.models import Asignatura
from proyecto.app.models import Usuario
from proyecto.tools.sgaws.cliente import SGA

import datetime
import proyecto.settings
import json
import logging as log


EXCLUSIONES = {'areas':('MED',),
               'modalidades':(u'semipresencial',),
               'carreras': (u'Cultura Física MED', u'Taller Educación Física', 
                            u'Curso de Computación', u'Curso de Inglés MED')
               }

def importar(periodoAcademicoId, periodoEvaluacionId=None):
    """ Importar unidades en primera instancia """
    sga = SGA(proyecto.settings.SGAWS_USER, proyecto.settings.SGAWS_PASS)    
    thetime = datetime.datetime.now().strftime("%Y-%m-%d")
    directory = os.path.abspath(os.path.dirname(__file__))
    log.basicConfig(filename= directory  + '../../tmp/sgaimporter-%s.log' % thetime,    
                    level   = log.DEBUG, 
                    datefmt = '%Y/%m/%d %I:%M:%S %p', 
                    format  = '%(asctime)s : %(levelname)s - %(message)s')
    periodoAcademico = None
    periodoEvaluacion = None
    try:
        periodoAcademico = PeriodoAcademico.objects.get(id=periodoAcademicoId)
        if periodoEvaluacionId:
            periodoEvaluacion = PeriodoEvaluacion.objects.get(id=periodoEvaluacionId)
    except PeriodoAcademico.DoesNotExist, PeriodoEvaluacion.DoesNotExist:
        log.error("Periodo Academico o  Periodo de Evaluacion no encontrados en la BD")
        return

    for oa in periodoAcademico.ofertasAcademicasSGA.all():
        rc = sga.wsinstitucional.sgaws_datos_carreras(id_oferta=oa.idSGA)
        carreras = json.loads(rc)
        if carreras[0] == '_error':
	    log.error(dict(error=carreras[1]))
	    continue
        unidades = []
        for id_carrera, carrera, modalidad, area, carrera_senescyt in carreras:
            if area in EXCLUSIONES['areas'] or modalidad in EXCLUSIONES['modalidades'] or carrera in EXCLUSIONES['carreras']:
                continue
            r_p = sga.wsinstitucional.sgaws_paralelos_carrera(id_oferta=oa.idSGA, id_carrera=id_carrera)
            js_p = json.loads(r_p)
            # Si hay paralelos en esta carrera y en esta oferta académica
            if js_p[0] != '_error':
               	paralelos_carrera = js_p[4]
                for id_paralelo, seccion, modulo, paralelo, id_modulo in paralelos_carrera:
                    # Para reutilizarlos en la creacion de las relaciones "EstudianteAsignaturaDocente"
                    asignaturas_docentes = []
                    """ Migracion de Docentes y Asignaguras """
                    r_ud = sga.wsacademica.sgaws_unidades_docentes_paralelo(id_paralelo=id_paralelo)
                    js_ud = json.loads(r_ud)
                    if js_ud[0] != '_error':
                        unidades_docentes = js_ud[6]
                        # TODO: En SGAWS se deberia quitar los datos del docente en el metodo sgaws_unidades_docentes_paralelo
                        for id_unidad, unidad, horas, creditos, obligatoria, inicio, fin, cedula, nombres, apellidos, titulo in unidades_docentes:

                            # Si se ha especificado un periodo de evaluacion
                            # se importa unicamente las unidades que se estan dictando actualmente
                            # TODO: probar snippet
                            fecha_inicio = None
                            fecha_fin = None
                            if inicio is not None and inicio != 'None':
                                fecha_inicio = datetime.datetime.strptime(inicio,'%Y-%m-%d').date()
                            if fin is not None and fin != 'None': 
                                fecha_fin = datetime.datetime.strptime(fin,'%Y-%m-%d').date()
			    """
			    TODO: fix bug
                            if fecha_inicio is not None and fecha_fin is not None:
                                # Si la unidad NO se dicta dentro del Periodo de Evaluacion no se importa
                                if periodoEvaluacion:
				    if not(fecha_inicio <= periodoEvaluacion.fin and fecha_fin >= periodoEvaluacion.inicio):
                                        continue
			    """
                            # Tratamiento de los saltos de línea dentro del nombre de la unidad
                            ###unidad = unidad.replace('\r\n',' ')[0:-1] ???
                            nombre_unidad = unidad.replace('\r\n',' ').strip()
                            # El idSGA tiene similitud con del id_horario_semana en el SGA
                            dict_unidad = dict(
                                idSGA="{0}:{1}".format(id_unidad, id_paralelo), area=area, carrera=carrera, carrera_senescyt=carrera_senescyt,
                                semestre=modulo, paralelo=paralelo, seccion=seccion, modalidad=modalidad, nombre=nombre_unidad, 
                                creditos=creditos, duracion=horas, inicio=fecha_inicio, fin=fecha_fin, periodoAcademico=periodoAcademico
                                )
                            r_d = sga.wspersonal.sgaws_datos_docente(cedula=cedula)
                            js_d = json.loads(r_d)
                            if js_d[0] != '_error':
                                titulo = js_d[3] or ''
                                email = js_d[5] or ''
                            else: 
                                email = ''
                                titulo = ''
                            dict_usuario_docente = dict(
                                username=cedula, password='', first_name=nombres.title(), last_name=apellidos.title(),
                                cedula=cedula, titulo=titulo, email=email
                                )
                            log.info(u'Datos de Unidad a crearse: {0}'.format(dict_unidad))
                            (asignatura, nueva) = Asignatura.objects.get_or_create(idSGA=dict_unidad['idSGA'],
                                                                                   defaults=dict_unidad)
                            if nueva:
                                log.info(u'Asignatura nueva: {0}'.format(asignatura))
                            (usuario, nuevo_usuario) = Usuario.objects.get_or_create(cedula=cedula, defaults=dict_usuario_docente)
                            if nuevo_usuario:
                                log.info(u'Usuario Docente creado: {0}:{1}'.format(usuario, cedula))
                            else:
                                # Actualizacion de datos del Usuario Docente SGA-SEDD
                                if not usuario.contiene(dict_usuario_docente):
                                    Usuario.objects.filter(username=usuario.username).update(**dict_usuario_docente)
                                    log.info(u'Usuario Docente editado: {0}'.format(usuario))
                            (docentePeriodoAcademico, nuevo) = DocentePeriodoAcademico.objects.get_or_create(
                                usuario=usuario, periodoAcademico=periodoAcademico)
                            (asignaturaDocente, nuevo) = AsignaturaDocente.objects.get_or_create(
                                docente=docentePeriodoAcademico, asignatura=asignatura
                                )
                            if nuevo:
                                log.info(u'AsignaturaDocente nuevo: {0}'.format(asignaturaDocente))
                            asignaturas_docentes.append(asignaturaDocente)

                    """ Migración de Estudiantes de Paralelo """ 
                    r_ep = sga.wsacademica.sgaws_estadoestudiantes_paralelo(id_paralelo=id_paralelo)
                    js_ep = json.loads(r_ep)
                    if js_ep[0] != '_error':
                        estudiantes_paralelo = js_ep[5]
                        for matricula, apellidos, nombres, cedula, estado in estudiantes_paralelo:
                            estado = estado.replace('EstadoMatricula','')
                            r_e = sga.wspersonal.sgaws_datos_estudiante(cedula=cedula)
                            js_e = json.loads(r_e)
                            if js_e[0] != '_error':
                                email = js_e[9] or ''
                            else: 
                                email = ''
                            dict_usuario_estudiante = dict(
                                username=cedula, password='', cedula=cedula, first_name=nombres.title(), last_name=apellidos.title(),
                                email=email
                                )
                            (usuario, nuevo_usuario) = Usuario.objects.get_or_create(cedula=cedula, defaults=dict_usuario_estudiante)
                            if not nuevo_usuario:
                                # Actualizacion de datos del Usuario Docente SGA-SEDD
                                if not usuario.contiene(dict_usuario_estudiante):
                                    Usuario.objects.filter(username=usuario.username).update(**dict_usuario_estudiante)
                                    log.info(u'Usuario Estudiante editado: {0}'.format(usuario))
                            
                            (estudiantePeriodoAcademico, nuevo) = EstudiantePeriodoAcademico.objects.get_or_create(
                                usuario=usuario, periodoAcademico=periodoAcademico
                                )
                            # Retomamos las asignaturas con docente extraidas en el metodo WS unidades_docentes 
                            for asignaturaDocente in asignaturas_docentes:
                                (estudianteAsignaturaDocente, nuevo) = EstudianteAsignaturaDocente.objects.get_or_create(
                                    estudiante=estudiantePeriodoAcademico, asignaturaDocente=asignaturaDocente, 
                                    defaults=dict(matricula=matricula, estado=estado)
                                    )
                                if nuevo:
                                    log.info(u'EstudianteAsignaturaDocente Nuevo: {0}'.format(estudianteAsignaturaDocente))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        importar( int(sys.argv[1]) )
        print u"Finalizada la migración de datos del SGA !!!"
    elif len(sys.argv) == 3:
        importar( int(sys.argv[1]), int(sys.argv[2]) )
        print u"Finalizada la migración de datos del SGA !!!"
    else:
        print "Error: Use sgaimporter id_periodo_academico [id_periodo_evaluacion]"
