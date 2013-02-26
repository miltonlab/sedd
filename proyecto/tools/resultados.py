# -*- coding: utf-8 -*-

from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import PeriodoEvaluacion
from proyecto.app.models import TabulacionEvaluacion2013
from proyecto.tools.util import UnicodeWriter

import os, logging, datetime
logg = logging.getLogger('logapp')

def ejecutar(id_periodo_evaluacion):
    ahora = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M')
    root = os.path.abspath(os.path.dirname(__file__) + '../../')
    nombre_archivo = '{0}/tmp/resultados-{1}.csv'.format(root, str(ahora))
    archivo = open(nombre_archivo, mode='w')
    escritor = UnicodeWriter(archivo)
    periodoEvaluacion = PeriodoEvaluacion.objects.get(id=id_periodo_evaluacion)
    tabulacion = periodoEvaluacion.tabulacion
    if tabulacion.tipo == 'EDD2013':
        tabulacion = TabulacionEvaluacion2013(periodoEvaluacion)
    docentes_resultados = []
    areas_periodo = periodoEvaluacion.areasSGA.values_list('siglas', flat=True)
    for docente in periodoEvaluacion.periodoAcademico.docentes.all():
        carreras_areas = docente.get_carreras_areas()
        escritor.writerow(("""CEDULA, APELLIDO 1, APELLIDO 2, NOMBRE 1, NOMBRE2, AUTOEVALUACION, PAR ACADEMICO, 
                                  DIRECTIVO , HETEROEVALUACION"""))
        for carrera, area in carreras_areas:
            # peque bug
            if 'MED' not in areas_periodo and 'MED' in carrera:
                continue
            resultados = tabulacion.por_docente(area, carrera, docente.id)
            total = resultados.get('total',0)
            promedios = resultados.get('promedios', {})
            logg.info('{0} resultados: {1} - {2}'.format(docente, promedios, total))
            fila = (docente.usuario.cedula, docente.usuario.last_name, docente.usuario.first_name, 
                    str(round(promedios.get('docente', 0), 2)), str(round(promedios.get('paracademico', 0), 2)), 
                    str(round(promedios.get('directivo', 0), 2)), str(round(promedios.get('estudiante', 0), 2)), 
                    )
            docentes_resultados.append(fila)
            escritor.writerow(fila)
    # escritor.writerows(docentes_resultados)
    archivo.close()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        ejecutar( int(sys.argv[1]) )
    else:
        print "Error. Use: evaluados id_periodo_evaluacion"

