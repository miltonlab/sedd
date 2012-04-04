#!/usr/bin/env python
#-*-coding:utf-8-*-
from SOAPpy import Config, HTTPTransport, SOAPAddress, WSDL
from django.conf import settings

class myHTTPTransport (HTTPTransport):
    username = None
    passwd = None

    @classmethod
    def setAuthentication(cls,u,p):
        cls.username = u
        cls.passwd = p
          
    def call(self, addr, data, namespace, soapaction=None, encoding=None,http_proxy=None, config=Config):
        if not isinstance(addr, SOAPAddress):
            addr=SOAPAddress(addr, config)
        if self.username != None:
            addr.user = self.username+":"+self.passwd
        return HTTPTransport.call(self, addr, data, namespace, soapaction,encoding, http_proxy, config)


class SGA:
    def __init__(self):
        u,p = settings.SGAWS_USER, settings.SGAWS_PASS
        wsdlFileValidacion = 'http://{0}:{1}@ws.unl.edu.ec/sgaws/wsvalidacion/soap/api.wsdl'.format(u,p)
        wsdlFilePersonal = 'http://{0}:{1}@ws.unl.edu.ec/sgaws/wspersonal/soap/api.wsdl'.format(u,p)
        myHTTPTransport.setAuthentication(settings.SGAWS_USER,settings.SGAWS_PASS)
        self.wsvalidacion = WSDL.Proxy(wsdlFileValidacion, transport=myHTTPTransport)
        self.wspersonal = WSDL.Proxy(wsdlFilePersonal, transport=myHTTPTransport)

    def autenticar(self,username,password):
        login = self.wsvalidacion.sgaws_validar_estudiante(cedula=username,clave=password)
        return True if login == 1 else False

    def datos_estudiante(self,username):
        cadena = self.wspersonal.sgaws_datos_estudiante(cedula=username)
        if 'error' in cadena.lower(): return None
        lista = cadena.replace('["','').replace('"]','').split('", "')
        estudiante = {'cedula':lista[0],'nombres':lista[1].capitalize(),'apellidos':lista[2].capitalize(),\
                      'fecha_nacimiento':lista[3],'telefono':lista[4], 'celular':lista[5],\
                      'direccion_actual':lista[6],'pais':lista[7],'ciudad':lista[8],'email':lista[9],\
                      'genero':lista[10]}
        return estudiante
        
