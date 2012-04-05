#!/usr/bin/env python
#-*-coding:utf-8-*-
from SOAPpy import Config, HTTPTransport, SOAPAddress, WSDL
from django.conf import settings
import json

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
        wsdlFileAcademica = 'http://{0}:{1}@ws.unl.edu.ec/sgaws/wsacademica/soap/api.wsdl'.format(u,p)
        wsdlFileInstitucional = 'http://{0}:{1}@ws.unl.edu.ec/sgaws/wsinstitucional/soap/api.wsdl'.format(u,p)
        myHTTPTransport.setAuthentication(settings.SGAWS_USER,settings.SGAWS_PASS)
        self.wsvalidacion = WSDL.Proxy(wsdlFileValidacion, transport=myHTTPTransport)
        self.wspersonal = WSDL.Proxy(wsdlFilePersonal, transport=myHTTPTransport)
        self.wsacademica = WSDL.Proxy(wsdlFileAcademica, transport=myHTTPTransport)
        self.wsinstitucional = WSDL.Proxy(wsdlFileInstitucional, transport=myHTTPTransport)

    def autenticar(self,username,password):
        login = self.wsvalidacion.sgaws_validar_estudiante(cedula=username,clave=password)
        return True if login == 1 else False

    def datos_estudiante(self,username):
        """
        @params: cedula del estudiante
        @return: cedula, nombres, apellidos, fecha_nacimiento, telefono, celular, direccion_actual,
        pais, ciudad, email, genero
        """
        cadena = self.wspersonal.sgaws_datos_estudiante(cedula=username)
        if 'error' in cadena.lower(): return None
        lista = cadena.replace('["','').replace('"]','').split('", "')
        estudiante = {'cedula':lista[0],'nombres':lista[1].capitalize(),'apellidos':lista[2].capitalize(),\
                      'fecha_nacimiento':lista[3],'telefono':lista[4], 'celular':lista[5],\
                      'direccion_actual':lista[6],'pais':lista[7],'ciudad':lista[8],'email':lista[9],\
                      'genero':lista[10]}
        return estudiante
        
    def matriculas_estudiante(self,id_oferta,cedula):
        """
        @params: cedula del estudiante
        @return: matriculas [oferta, carrera, modulo, paralelo, matricula, estado]
        """
        respuesta = self.wsacademica.sgaws_carreras_estudiante(cedula=cedula)
        js = json.loads(respuesta)
        """ id_carrera, nombre, modalidad """
        carreras = js[3]
        matriculas = []
        for c in carreras:
            respuesta = self.wsacademica.sgaws_estudiante_matriculas(id_carrera=c[0],cedula=cedula)
            """ Todas las matriculas """
            js=json.loads(respuesta)
            """ id_oferta, id_matricula, paralelo, numero_modulo, nombre_modulo, estado_matricula """
            for m in js:
                if m[0] == id_oferta:
                    matriculas.append(dict(
                        id_oferta=m[0], id_carrera=c[0], numero_modulo=m[3], paralelo=m[2],
                        id_matricula=m[1], estado_matricula=m[5].replace("EstadoMatricula","").lower()
                    ))
        return matriculas

    def unidades_estudiante(self, id_oferta, cedula):
        """
        @params: id de la oferta, cedula del estudiante
        @return: unidades [id, carrera, numero_modulo, paralelo, seccion, nombre_unidad, creditos_unidad]
        """
        matriculas = self.matriculas_estudiante(id_oferta,cedula)
        unidades = []
        for m in matriculas:
            r = self.wsinstitucional.sgaws_paralelos_carrera(id_oferta=id_oferta, id_carrera=m['id_carrera'])
            js = json.loads(r)
            """ Todos los paralelos de la carrera en la que está matriculado """
            paralelos = js[4]
            """ Buscamos el paralelo que le corresponde en esta carrera """
            paralelo = None
            for p in paralelos:
                """ id_paralelo, seccion, numero_modulo, nombre_paralelo, id_modulo """
                if m['numero_modulo'] == p[2] and m['paralelo'] == p[3]:
                    paralelo = p
                    break
            """ Ahora extraemos las unidades de su plan de estudios"""
            r = self.wsacademica.sgaws_plan_estudio(id_paralelo=paralelo[0])
            js = json.loads(r)
            us = js[6]
            # Se ordenan las unidades de acuerdo a su nombre [0]
            us.sort(lambda x,y: cmp(x[0].upper(),y[0].upper()))
            i = 0
            for u in us:
                i = i+1
                """ id, carrera, numero_modulo, paralelo, seccion, nombre_unidad, creditos_unidad """                
                unidades.append(dict(
                    id = "%s%s%s%s%s" % (id_oferta, m['id_carrera'], p[4], p[0], i),
                    carrera=js[0], modulo=js[2], paralelo=js[3],
                    seccion=js[4], unidad=u[0], creditos=u[2]
                ))
                
        return unidades

    def unidades_docente(self,id_oferta, cedula):
        r = self.wsacademica.sgaws_carga_horaria_docente(id_oferta=id_oferta, cedula=cedula)
        js = json.loads(r)
        us = js[3]
        # Se ordenan las unidades de acuerdo a su nombre [0]
        us.sort(lambda x,y: cmp(x[1].upper(),y[1].upper()))
        unidades = []
        for u in us:
            unidades.append(dict(
                carrera=u[0], unidad=u[1], modulo=u[3], paralelo=u[4]
            ))
        return unidades
