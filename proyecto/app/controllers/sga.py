#-*- encoding: utf-8 -*-
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import OfertaAcademicaSGA

import logging

log = logging.getLogger('logapp')

def cargar_ofertas_sga(request, periodoAcademicoId):
    """ Metodo invocado a través de Ajax """    
    try:
        pa=PeriodoAcademico.objects.get(pk=periodoAcademicoId)
        pa.cargarOfertasSGA()
        messages.info(request, "Se recargaron con éxito las Ofertas Académicas")
        log.info("Ofertas Recargadas en el Perido " + str(pa))
        return HttpResponse("OK")
    except Exception, e:
        log.error("Error recargando ofertas SGA: " + str(e))
        return HttpResponse("error"+str(e))
        
    
def cargar_info_sga(request, periodoAcademicoId):
    """ Metodo invocado a través de Ajax """
    try:
        pa=PeriodoAcademico.objects.get(pk=periodoAcademicoId)
        log.info(pa + "pendiente..")
        return HttpResponse("OK")
    except Exception, e:
        log.error("Error cargando info SGA: "+str(e))
        return HttpResponse("error"+str(e))
    
