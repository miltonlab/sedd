#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import OfertaAcademicaSGA

from sgaws.cliente import SGA
from settings import SGAWS_USER, SGAWS_PASS

import logging

log = logging.getLogger('logapp')

def cargar_ofertas_sga(request, periodoAcademicoId):
    """ Metodo invocado a través de Ajax. Recarga todas las ofertas """
    if not periodoAcademicoId:
        return HttpResponse("Falta Periodo Academico")
    try:
        proxy = SGA(SGAWS_USER, SGAWS_PASS)
        pa = PeriodoAcademico.objects.get(id=periodoAcademicoId)
        ofertas_dict = proxy.ofertas_academicas(pa.inicio, pa.fin)
        ofertas = [OfertaAcademicaSGA(idSGA=oa['id'], descripcion=oa['descripcion'])  for oa in ofertas_dict]
        for oa in ofertas:
            try:
                OfertaAcademicaSGA.objects.get(idSGA=oa.idSGA)
            except OfertaAcademicaSGA.DoesNotExist:
                oa.save()
        return HttpResponse("OK")
    except Exception, e:
        log.error("Error recargando ofertas SGA: " + str(e))
        return HttpResponse("error: "+str(e))
        
#TODO: muy pesado ejecutar en el frontal
def cargar_info_sga(request, periodoAcademicoId):
    """ Metodo invocado a través de Ajax """
    try:
        pa=PeriodoAcademico.objects.get(pk=periodoAcademicoId)
        log.info(pa + "pendiente..")
        return HttpResponse("OK")
    except Exception, e:
        log.error("Error cargando info SGA: "+str(e))
        return HttpResponse("error"+str(e))
    
