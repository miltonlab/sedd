# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from piston.resource import Resource
from proyecto.app.api.handlers import ServicioValidadorHandler 
from proyecto.app.api.handlers import PeriodoEvaluacionHandler
from proyecto.app.api.handlers import PeriodoAcademicoHandler 

periodo_academico_handler = Resource(PeriodoAcademicoHandler)
periodo_evaluacion_handler = Resource(PeriodoEvaluacionHandler)
servicio_validador_handler = Resource(ServicioValidadorHandler)

urlpatterns = patterns('',
    url(r'^periodos_academicos/', periodo_academico_handler),
    url(r'^periodos_evaluacion/', periodo_evaluacion_handler),
    url(r'^verificar/(?P<id_periodo_evaluacion>\d{1,2})/(?P<dni>\d{8,})/', 
        servicio_validador_handler),
)
