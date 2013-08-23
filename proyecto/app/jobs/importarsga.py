#encoding:utf-8

import os, sys, datetime 
os.environ['DJANGO_SETTINGS_MODULE']='proyecto.settings'
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../../../'))

from django_extensions.management.jobs import BaseJob
from proyecto.app.models import Configuracion, PeriodoAcademico
from proyecto.tools import sgaimporter

class Job(BaseJob):
    """
    Job para invocar a la herramienta que importa la información académica
    del SGA a través del uso de los WebServices
    @author: miltonlab
    @date: 08/08/2012
    """
    
    help = "Importador datos academicos de SGA UNL"

    def execute(self):
        periodoAcademico = Configuracion.getPeriodoAcademicoActual()
        #sgaimporter.importar(periodoAcademico.id)
        print periodoAcademico
