#-*- encoding:utf-8 -*-

from proyecto.app.models import EstudiantePeriodoAcademicoAsignatura
from proyecto.app.models import EstudiantePeriodoAcademico
from proyecto.app.models import DocentePeriodoAcademicoAsignatura
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import Asignatura
from proyecto.app.models import Usuario
from sgaws.cliente import SGA

import datetime
import settings
import json
import logging as log

EXCLUSIONES = {'areas':('MED',), 'modalidades':('semipresencial', 'distancia')}

def importar(periodoAcademicoId):
    """ Importar unidades en primera instancia"""
    sga = SGA(settings.SGAWS_USER, settings.SGAWS_PASS)    
    thetime = datetime.datetime.now().strftime("%Y-%m-%d")
    log.basicConfig(filename= "sgaimporter-%s.log" % thetime,
                    level   = log.DEBUG, 
                    datefmt = '%Y/%m/%d %I:%M:%S %p', 
                    format  = '%(asctime)s : %(levelname)s - %(message)s')
    pa = PeriodoAcademico.objects.get(id=periodoAcademicoId)
    for oa in pa.ofertasAcademicasSGA.all():
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
                    # Para reutilizarlos en la relacion con estudiantes
                    asignaturas = []
                    """ Migración de Docentes y Asignaguras """
                    r_ud = sga.wsacademica.sgaws_unidades_docentes(id_paralelo=id_paralelo)
                    js_ud = json.loads(r_ud)
                    if js_ud[0] != '_error':
                        unidades_docentes = js_ud[6]
                        for id_unidad, unidad, horas, creditos, obligatoria, cedula, nombres, apellidos, titulo in unidades_docentes:
                            dict_unidad = dict(
                                idSGA="{0}:{1}".format(id_unidad, id_paralelo), area=area, carrera=carrera, semestre=modulo,
                                paralelo=paralelo, seccion=seccion, nombre=unidad, creditos=creditos, duracion=horas
                            )
                            dict_usuario_docente = dict(
                                username=cedula, password='', first_name=nombres.title(), last_name=apellidos.title(),
                                cedula=cedula, titulo=titulo, email=''
                            )
                            (asignatura, nueva) = Asignatura.objects.get_or_create(idSGA=dict_unidad['idSGA'], defaults=dict_unidad)
                            asignaturas.append(asignatura)
                            if nueva == True:
                                log.info(u'Asignatura Creada: {0}'.format(asignatura))
                            else:
                                log.info(u'Asignatura ya existe: {0}'.format(asignatura))
                            (usuario, nuevo) = Usuario.objects.get_or_create(cedula=cedula, defaults=dict_usuario_docente)
                            if nuevo == True:
                                log.info(u'Usuario Docente Creado: {0}:{1}'.format(usuario, cedula))
                            else:
                                log.info(u'Usuario Docente ya existe: {0}:{1}'.format(usuario, cedula))
                            (docentePeriodoAcademico, nuevo) = DocentePeriodoAcademico.objects.get_or_create(docente=usuario, periodoAcademico=pa)
                            if nuevo == True:
                                log.info(u'DocentePeriodoAcademico Creado: {0}'.format(docentePeriodoAcademico))
                            else:
                                log.info(u'DocentePeriodoAcademico ya existe: {0}'.format(docentePeriodoAcademico))
                            (docentePeriodoAcademicoAsignatura, nuevo) = DocentePeriodoAcademicoAsignatura.objects.get_or_create(
                                docente=docentePeriodoAcademico, asignatura=asignatura
                            )
                            if nuevo == True:
                                log.info(u'DocentePeriodoAcademicoAsignatura Creado: {0}'.format(docentePeriodoAcademicoAsignatura))
                            else:
                                log.info(u'DocentePeriodoAcademicoAsignatura ya existe: {0}'.format(docentePeriodoAcademicoAsignatura))
                        
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
                            if nuevo == True:
                                log.info(u'Usuario Estudiante Creado: {0}:{1}'.format(usuario, cedula))
                            else:
                                log.info(u'Usuario Estudiante ya existe: {0}:{1}'.format(usuario, cedula))
                            (estudiantePeriodoAcademico, nuevo) = EstudiantePeriodoAcademico.objects.get_or_create(
                                estudiante=usuario, periodoAcademico=pa
                            )
                            if nuevo == True:
                                log.info(u'EstudiantePeriodoAcademico Creado: {0}'.format(estudiantePeriodoAcademico))
                            else:
                                log.info(u'EstudiantePeriodoAcademico ya existe: {0}'.format(estudiantePeriodoAcademico))
                            # Retomamos las agisnaturas extraidas en el metodo WS unidades_docentes
                            for asignatura in asignaturas:
                                (estudiantePeriodoAcademicoAsignatura, nuevo) = EstudiantePeriodoAcademicoAsignatura.objects.get_or_create(
                                    estudiante=estudiantePeriodoAcademico, asignatura=asignatura, defaults=dict(matricula=matricula, estado=estado)
                                )
                                if nuevo == True:
                                    log.info(u'EstudiantePeriodoAcademicoAsignatura Creado: {0}'.format(estudiantePeriodoAcademicoAsignatura))
                                else:
                                    log.info(u'EstudiantePeriodoAcademicoAsignatura ya existe: {0}'.format(estudiantePeriodoAcademicoAsignatura))
