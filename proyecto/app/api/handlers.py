#encoding:utf-8

from piston.handler import BaseHandler
from proyecto.app.models import PeriodoAcademico, PeriodoEvaluacion
import logging
logg = logging.getLogger('logapp')


class ServicioValidadorHandler(BaseHandler):
    allowed_methods = ('GET',)

    # GET
    def read(self, request, id_periodo_evaluacion, dni):
        """ 
        Verifica si un estudiante ha aplicado todas las encuestas 
        en el periodo de evaluacion.
        """
        try:
            periodo_evaluacion = PeriodoEvaluacion.objects.get(id=id_periodo_evaluacion)
            resultado = periodo_evaluacion.verificar_estudiante(dni)
            return resultado
        except Exception:
            logg.error('Error en consulta al API verificar_estudiante periodo: {0}, dni: {1}',format(
                    id_periodo_evaluacion, dni))
            return False

    
class PeriodoEvaluacionHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = PeriodoEvaluacion
    exclude = ('periodoAcademico', 'observaciones', 'descripcion')

    # GET
    def read(self, request):
        """ Lee todos los Periodos de Evaluacion que existen en la BD """
        periodos = PeriodoEvaluacion.objects.all()
        return periodos


class PeriodoAcademicoHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = PeriodoAcademico
    #exclude = ('periodoAcademico', 'observaciones', 'descripcion')
    # GET
    def read(self, request):
        """ Lee todos los Periodos Academicos que existen en la BD """
        periodos = PeriodoAcademico.objects.all()
        return periodos
