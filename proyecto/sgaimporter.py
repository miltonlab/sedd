#-*- encoding:utf-8 -*-

from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import Asignatura
from sgaws.cliente import SGA
import datetime
import settings
import json
import logging as log

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
        for id_carrera, nombre_carrera, modalidad_carrera in carreras:
            rp = sga.wsinstitucional.sgaws_paralelos_carrera(id_oferta=oa.idSGA, id_carrera=id_carrera)
            jsp = json.loads(rp)
            # Si hay paralelos en esta carrera y en esta oferta académica
            if jsp[0] != '_error':
                paralelos_carrera = jsp[4]
                for id_paralelo, seccion, numero_modulo, nombre_paralelo, id_modulo in paralelos_carrera:
                    ru = sga.wsacademica.sgaws_plan_estudio(id_paralelo=id_paralelo)
                    # Si no hay error al obtener unidades del plan
                    jsu = json.loads(ru)
                    if jsu[0] != u'_error':
                        unidades_paralelo = jsu[6]
                        for id, nombre, horas, creditos, obligatoria in unidades_paralelo:
                            unidad = dict(
                                idSGA=id, area='NN', carrera=nombre_carrera, semestre=numero_modulo, paralelo=nombre_paralelo,
                                nombre=nombre, creditos=creditos, duracion=horas
                            )
                            obj, nuevo = Asignatura.objects.get_or_create(idSGA=unidad['idSGA'], defaults=unidad)
                            if nuevo == True:
                                log.info('Agregada Asignatura: {0}:{1}'.format(id,nombre))
                            else:
                                log.info('Asignatura ya existente: {0}:{1}'.format(id,nombre))

