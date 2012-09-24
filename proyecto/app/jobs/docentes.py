# -*- coding: utf-8 -*-

import os, sys, datetime 
os.environ['DJANGO_SETTINGS_MODULE']='proyecto.settings'
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../../../'))

from django_extensions.management.jobs import BaseJob
from proyecto.app.models import Configuracion, AsignaturaDocente, DocentePeriodoAcademico
from tools.util import UnicodeWriter


class Job(BaseJob):
    """
    Job que exporta todos los docentes con información de asignaturas y
    cantidad de Estudiantes que los evaluan
    @author: miltonlab
    @date: 21-09-2012
    run:  python manage.py runjob docentes
    """
    
    help = "Docentes con información de Asignaturas"

    def execute(self):
        periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()        
        rs=AsignaturaDocente.objects.filter(docente__periodoAcademico=periodoEvaluacion).values_list(
            'asignatura__area', 'asignatura__carrera', 'docente',
            'asignatura__semestre', 'asignatura__paralelo', 'asignatura__seccion',
            'asignatura__nombre', 'id').order_by('asignatura__area', 'asignatura__carrera',
                                                 'docente', 'asignatura__semestre', 'asignatura__paralelo',
                                                 'asignatura__seccion', 'asignatura__nombre') 
        rs2 = list()
        for t in rs:
            l = list(t)
            # Se cambia el id del docente por su representacion en unicode
            l[2] = DocentePeriodoAcademico.objects.get(id=l[2]).__unicode__()
            # Se cambia el id de la AsignaturaDocente por la cantidad de estudiantes que la toman
            l[7] = str(AsignaturaDocente.objects.get(id=l[7]).estudiantesAsignaturaDocente.count())
            rs2.append(tuple(l))
        root = os.path.abspath(os.path.dirname(__file__) + '../../../')            
        f = open('{0}/tmp/docentes.csv'.format(root), 'wb')
        w = UnicodeWriter(f, delimiter=';')
        w.writerow((u'Área', u'Carrera', u'Docente', u'Módulo', u'Paralelo', u'Sección', u'Asignatura/Unidad/Momento/Modulo/Taller', u'No Estudiantes'))
        w.writerows(rs2)
        f.close()
