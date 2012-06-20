# -*- coding: utf-8 -*-
# Para ejecutar el modulo de manerea independiente
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../../'))
print os.path.abspath(os.path.dirname(__file__) + '../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'proyecto.settings'

from proyecto.app.models import EstudianteAsignaturaDocente
from proyecto.app.models import EstudiantePeriodoAcademico
from proyecto.app.models import AsignaturaDocente
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import Asignatura
from proyecto.app.models import Usuario
from proyecto.tools.sgaws.cliente import SGA

import datetime
import proyecto.settings
import json
import logging as log


EXCLUSIONES = {'areas':('MED',), 'modalidades':('semipresencial', 'distancia')}

def importar(periodoAcademicoId, periodoEvaluacionId=None):
    """ Importar unidades en primera instancia"""
    sga = SGA(settings.SGAWS_USER, settings.SGAWS_PASS)    
    thetime = datetime.datetime.now().strftime("%Y-%m-%d")
    log.basicConfig(filename= "sgaimporter-%s.log" % thetime,
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
        print "Periodo Academico o  Periodo de Evaluacion no encontrados en la BD"
        return

    for oa in periodoAcademico.ofertasAcademicasSGA.all():
        rc = sga.wsinstitucional.sgaws_datos_carreras(id_oferta=oa.idSGA)
        carreras = json.loads(rc)
        if carreras[0] == '_error':
            return dict(error=carreras[1]) 
        unidades = []
        for id_carrera, carrera, modalidad, area in carreras:
            if area in EXCLUSIONES['areas'] or modalidad in EXCLUSIONES['modalidades']:
                continue
            r_p = sga.wsinstitucional.sgaws_paralelos_carrera(id_oferta=oa.idSGA, id_carrera=id_carrera)
            js_p = json.loads(r_p)
            # Si hay paralelos en esta carrera y en esta oferta académica
            if js_p[0] != '_error':
                paralelos_carrera = js_p[4]
                for id_paralelo, seccion, modulo, paralelo, id_modulo in paralelos_carrera:
                    # Para reutilizarlos en la creacion de las relaciones "EstudianteAsignaturaDocente"
                    asignaturas_docentes = []
                    """ Migración de Docentes y Asignaguras """
                    r_ud = sga.wsacademica.sgaws_unidades_docentes_paralelo(id_paralelo=id_paralelo)
                    js_ud = json.loads(r_ud)
                    if js_ud[0] != '_error':
                        unidades_docentes = js_ud[6]
                        for id_unidad, unidad, horas, creditos, obligatoria, inicio, fin, cedula, nombres, apellidos, titulo in unidades_docentes:
                            # Si se ha especificado un periodo de evaluacion
                            # se importa unicamente las unidades que se estan dictando actualmente
                            # TODO: probar snippet
                            #
                            # fecha_inicio = datetime.datetime.strptime(inicio,'%d/%m/%Y').date()
                            # fecha_fin = datetime.datetime.strptime(fin,'%d/%m/%Y').date()
                            # if not (periodoEvaluacion and fecha_inicio <= periodoEvaluacion.fin and fecha_fin >= periodoEvaluacion.inicio):
                            #    continue

                            # Tratamiento de los saltos de línea dentro del nombre de la unidad
                            unidad = unidad.replace('\r\n',' ')[0:-1]
                            dict_unidad = dict(
                                idSGA="{0}:{1}".format(id_unidad, id_paralelo), area=area, carrera=carrera, semestre=modulo,
                                paralelo=paralelo, seccion=seccion, nombre=unidad, creditos=creditos, duracion=horas, inicio=inicio, fin=fin
                                )
                            dict_usuario_docente = dict(
                                username=cedula, password='', first_name=nombres.title(), last_name=apellidos.title(),
                                cedula=cedula, titulo=titulo, email=''
                                )
                            (asignatura, nueva) = Asignatura.objects.get_or_create(idSGA=dict_unidad['idSGA'], defaults=dict_unidad)
                            """
                            if nueva == True:
                            log.info(u'Asignatura Creada: {0}'.format(asignatura))
                            else:
                            log.info(u'Asignatura ya existe: {0}'.format(asignatura))
                            """
                            (usuario, nuevo) = Usuario.objects.get_or_create(cedula=cedula, defaults=dict_usuario_docente)
                            """
                            if nuevo == True:
                            log.info(u'Usuario Docente Creado: {0}:{1}'.format(usuario, cedula))
                            else:
                            log.info(u'Usuario Docente ya existe: {0}:{1}'.format(usuario, cedula))
                            """
                            (docentePeriodoAcademico, nuevo) = DocentePeriodoAcademico.objects.get_or_create(usuario=usuario, periodoAcademico=periodoAcademico)
                            """
                            if nuevo == True:
                            log.info(u'DocentePeriodoAcademico Creado: {0}'.format(docentePeriodoAcademico))
                            else:
                            log.info(u'DocentePeriodoAcademico ya existe: {0}'.format(docentePeriodoAcademico))
                            """
                            (asignaturaDocente, nuevo) = AsignaturaDocente.objects.get_or_create(
                                docente=docentePeriodoAcademico, asignatura=asignatura
                                )
                            if nuevo == True:
                                log.info(u'AsignaturaDocente Creado: {0}'.format(asignaturaDocente))
                            else:
                                log.info(u'AsignaturaDocente ya existe: {0}'.format(asignaturaDocente))
                            asignaturas_docentes.append(asignaturaDocente)
                    """ Migración de Estudiantes de Paralelo """ 
                    r_ep = sga.wsacademica.sgaws_estadoestudiantes_paralelo(id_paralelo=id_paralelo)
                    js_ep = json.loads(r_ep)
                    if js_ep[0] != '_error':
                        estudiantes_paralelo = js_ep[5]
                        for matricula, apellidos, nombres, cedula, estado in estudiantes_paralelo:
                            estado = estado.replace('EstadoMatricula','')
                            dict_usuario_estudiante = dict(
                                username=cedula, password='', cedula=cedula, first_name=nombres.title(), last_name=apellidos.title(),
                                email=''
                                )
                            (usuario, nuevo) = Usuario.objects.get_or_create(cedula=cedula, defaults=dict_usuario_estudiante)
                            """
                            if nuevo == True:
                            log.info(u'Usuario Estudiante Creado: {0}:{1}'.format(usuario, cedula))
                            
                            else:
                            log.info(u'Usuario Estudiante ya existe: {0}:{1}'.format(usuario, cedula))
                            """
                            (estudiantePeriodoAcademico, nuevo) = EstudiantePeriodoAcademico.objects.get_or_create(
                                usuario=usuario, periodoAcademico=periodoAcademico
                                )
                            """
                            if nuevo == True:
                            log.info(u'EstudiantePeriodoAcademico Creado: {0}'.format(estudiantePeriodoAcademico))
                            else:
                            log.info(u'EstudiantePeriodoAcademico ya existe: {0}'.format(estudiantePeriodoAcademico))
                            """
                            # Retomamos las asignaturas con docente extraidas en el metodo WS unidades_docentes 
                            for asignaturaDocente in asignaturas_docentes:
                                (estudianteAsignaturaDocente, nuevo) = EstudianteAsignaturaDocente.objects.get_or_create(
                                    estudiante=estudiantePeriodoAcademico, asignaturaDocente=asignaturaDocente, defaults=dict(matricula=matricula, estado=estado)
                                    )
                                if nuevo == True:
                                    log.info(u'EstudianteAsignaturaDocente Creado: {0}'.format(estudianteAsignaturaDocente))
                                else:
                                    log.info(u'EstudianteAsignaturaDocente ya existe: {0}'.format(estudianteAsignaturaDocente))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        importar( int(sys.argv[1]) )
    elif len(sys.argv) == 3:
        importar( int(sys.argv[1]), int(sys.argv[2]) )
