#-*- coding: utf-8 -*-

from piston.handler import BaseHandler
from piston.utils import rc
from proyecto.app.models import Configuracion
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import PeriodoEvaluacion
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import TabulacionEvaluacion2013
from proyecto.app.models import TabulacionSatisfaccion2012
from proyecto.app.models import TabulacionAdicionales2012
from proyecto.app.models import Usuario

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
            if not request.user.groups.filter(name='apiusers'):
                return {'Notificacion': 'No tiene permisos suficientes !'}
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

    def read(self, request):
        if not request.user.groups.filter(name='apiusers'):
            return {'Notificacion': 'No tiene permisos suficientes !'}

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


class ResultadosHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, id_periodo_evaluacion, dni):
        try:
            if not request.user.groups.filter(name='apiusers'):
                return {'Notificacion': 'No tiene permisos suficientes !'}
            periodo_evaluacion = PeriodoEvaluacion.objects.get(id=id_periodo_evaluacion)
            docente = DocentePeriodoAcademico.objects.get(
                usuario__cedula=dni, periodoAcademico=periodo_evaluacion.periodoAcademico)
            tabulacion = periodo_evaluacion.tabulacion
            if tabulacion.tipo == 'EDD2013':
                tabulacion = TabulacionEvaluacion2013(periodo_evaluacion)
                # Se calcula en todas las carreras del docente
                resultados_completos = tabulacion.por_docente(None, None, docente.id)
                # Se extrae solo lo necesario
                resultados = dict([(k, resultados_completos.get(k)) for k in ('promedios_componentes', 'promedios', 'total')])
            elif tabulacion.tipo == 'ESE2012':
                tabulacion = TabulacionSatisfaccion2012(periodo_evaluacion)
                resultados_completos = tabulacion.por_docente(None, None, docente.id)
                # Se extrae solo lo necesario
                resultados = dict([(k, resultados_completos.get(k)) for k in ('porcentajes', 'totales')])
            elif tabulacion.tipo == 'EAAD2012':
                tabulacion = TabulacionAdicionales2012(periodo_evaluacion)
                resultados_completos = tabulacion.por_docente(None, None, docente.id)
                resultados = {'docente' : resultados_completos['porcentaje1'],
                              'comision' : resultados_completos['porcentaje2'],
                              'global' : resultados_completos['total'] 
                              }
            return resultados
        except Exception, ex:
            return {'Error': str(ex)}
       
class ParametrosHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Configuracion

    def read(self, request):
        try:
            return Configuracion.objects.all()[0]
        except Exception, ex:
            return {'error' : str(ex)}

#class DocentePeriodoAcademicoHandler(BaseHandler):
class UsuarioHandler(BaseHandler):
    allowed_methods = ('PUT',)
    model = Usuario
    #exclude = ('periodoAcademico', 'observaciones', 'descripcion')

    def update(self, request):
        """
        TEST
        import simplejson, httplib
        con = httplib.HTTPConnection('localhost', 8000)
        con.request('PUT', '/api/docentes/actualizar',
        json.dumps({'cedula':'1101379111','nombres':'Jose Leo'}), 
        {'Content-Type':'application/json'})
        """
        try:
            print 'SEDD-API: Sincronizando usuario... CONSOLA'
            logg.info('SEDD-API: Sincronizando usuario...')
            cedula = request.data['cedula']
            usuario = Usuario.objects.get(cedula=cedula)
            usuario.nombres = request.data['nombres']
            usuario.apellidos = request.data['apellidos']
            usuario.titulo = request.data.get('titulo', '')
            usuario.email = request.data['email']
            usuario.save()
            logg.info('SEDD-API: Usuario Actualizado {0}: {1}'.format(cedula, nombres))
            return rc.ALL_OK
        except Exception, ex:
            print 'ERROR: ', str(ex)
            logg.error("SEDD-API: Error al modificar docente API Rest: ", str(ex))

