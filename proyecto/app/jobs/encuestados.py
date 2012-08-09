# -*- coding: utf-8 -*-

import os, sys, datetime 
os.environ['DJANGO_SETTINGS_MODULE']='proyecto.settings'
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../../../'))

from proyecto.app.models import Configuracion, EstudianteAsignaturaDocente
from django_extensions.management.jobs import BaseJob


class Job(BaseJob):
    """
    Job que exporta todos los estudiantes que contestaron todas las encuestas
    en la Encuesta de Satisfacción Estudiantil 2012.
    @author: miltonlab
    @date: 08/08/2012
    """
    
    help = "Estudiantes encuestados en Periodo de Evaluación Vigente"

    def execute(self):
        ahora = datetime.datetime.now()
        ahora = ahora.strftime('%Y-%m-%d-%H:%M')
        root = os.path.abspath(os.path.dirname(__file__) + '../../../')
        archivo = open('{0}/tmp/encuestados-{1}.csv'.format(root,str(ahora)), 'w')        
        periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
        areas_siglas = [a.siglas for a in periodoEvaluacion.areasSGA.all()]
        # Todos los estudiantes de las áreas implicadas en el Periodo de Evaluación
        estudiantesAsignaturasDocentes = EstudianteAsignaturaDocente.objects.filter(
            asignaturaDocente__asignatura__area__in=areas_siglas)
        # Datos estrictamente necesarios
        cedulas_matriculas = estudiantesAsignaturasDocentes.values_list(
            'estudiante__usuario__cedula','matricula').distinct()
        # Verificación
        for cedula, matricula in cedulas_matriculas:
            if periodoEvaluacion.verificar_estudiante(cedula):
                archivo.write('{0};{1}\n'.format(cedula, matricula))
        archivo.close()
