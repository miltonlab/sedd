#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from SOAPpy import Config, HTTPTransport, SOAPAddress, WSDL
import json


"""
    Modulo que obtiene toda la información academica necesaria
    para diversos sistemas clientes del SGA  
    @modulo: sgaws.cliente
    @author: Silvana Pacheco, Daysi Ordoñez, Milton Labanda
    @date: Enero 2012
"""

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
    def __init__(self, sgaws_user, sgaws_pass):
        u,p = sgaws_user, sgaws_pass
        wsdlFileValidacion = 'http://{0}:{1}@ws.unl.edu.ec/sgaws/wsvalidacion/soap/api.wsdl'.format(u,p)
        wsdlFilePersonal = 'http://{0}:{1}@ws.unl.edu.ec/sgaws/wspersonal/soap/api.wsdl'.format(u,p)
        wsdlFileAcademica = 'http://{0}:{1}@ws.unl.edu.ec/sgaws/wsacademica/soap/api.wsdl'.format(u,p)
        wsdlFileInstitucional = 'http://{0}:{1}@ws.unl.edu.ec/sgaws/wsinstitucional/soap/api.wsdl'.format(u,p)
        myHTTPTransport.setAuthentication(u,p)
        self.wsvalidacion = WSDL.Proxy(wsdlFileValidacion, transport=myHTTPTransport)
        self.wspersonal = WSDL.Proxy(wsdlFilePersonal, transport=myHTTPTransport)
        self.wsacademica = WSDL.Proxy(wsdlFileAcademica, transport=myHTTPTransport)
        self.wsinstitucional = WSDL.Proxy(wsdlFileInstitucional, transport=myHTTPTransport)
    
    def autenticar_estudiante(self,username,password):
        login = self.wsvalidacion.sgaws_validar_estudiante(cedula=username,clave=password)
        return True if login == 1 else False

    def autenticar_docente(self,username,password):
        login = self.wsvalidacion.sgaws_validar_docente(cedula=username,clave=password)
        return True if login == 1 else False


    def periodo_lectivo_actual(self):
        """
        Obtiene el periodo lectivo en el año actual
        @params: nothing
        @return: periodos_lectivos [id, descripcion]
        """
        r = self.wsacademica.sgaws_periodos_lectivos()
        periodos = json.loads(r)
        anio_actual = datetime.date.today().year
        for id, descripcion in periodos:
            anios = descripcion.split('-')
            anio1 = anios[0].strip()
            anio2 = anios[1].strip()
            if anio1 == str(anio_actual):
                return dict(id=id, descripcion=descripcion)
            if anio2 == str(anio_actual):
                return dict(id=id, descripcion=descripcion)
        return dict(error='No se puede obtener el periodo actual')
        
    def ofertas_periodo_actual (self):
        """
        Obtiene las ofertas academicas que estén pertenecen al periodo actual
        @params:
        @return: ofertas_academicas [id, descripcion, fecha_inicio, fecha_fin]
        """
        periodo = self.periodo_lectivo_actual()
        r = self.wsacademica.sgaws_ofertas_academicas(id_periodo=periodo['id'])
        ofertas = json.loads(r)
        vigentes = []
        for id, descripcion, fecha_inicio, fecha_fin in ofertas:
            vigentes.append(dict(id=id, descripcion=descripcion, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin))
        return vigentes


    def ofertas_academicas_vigentes(self):
        """
        Obtiene las ofertas academicas que estén viegentes a la fecha actual
        @params:
        @return: ofertas_academicas [id, descripcion, fecha_inicio, fecha_fin]
        """
        periodo = self.periodo_lectivo_actual()
        r = self.wsacademica.sgaws_ofertas_academicas(id_periodo=periodo['id'])
        ofertas = json.loads(r)
        vigentes = []
        for id, descripcion, inicio, fin in ofertas:
            hoy = datetime.date.today()
            fecha_inicio = datetime.datetime.strptime(inicio.strip(),'%Y-%m-%d').date()
            fecha_fin = datetime.datetime.strptime(fin.strip(),'%Y-%m-%d').date()
            if fecha_inicio < hoy < fecha_fin:
                vigentes.append(dict(id=id, descripcion=descripcion, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin))
        return vigentes
        
    def ofertas_academicas(self, periodo_inicio, periodo_fin):
        """
        Obtiene las ofertas academicas que estén dentro del rango de fechas dado
        @params:
        @return: ofertas_academicas [id, descripcion, fecha_inicio, fecha_fin]
        """
        periodo = self.periodo_lectivo_actual()
        r = self.wsacademica.sgaws_ofertas_academicas(id_periodo=periodo['id'])
        ofertas_todas = json.loads(r)
        ofertas = []
        for id, descripcion, inicio, fin in ofertas_todas:
            oferta_inicio = datetime.datetime.strptime(inicio.strip(),'%Y-%m-%d').date()
            oferta_fin = datetime.datetime.strptime(fin.strip(),'%Y-%m-%d').date()
            if  oferta_inicio <= periodo_fin and oferta_fin >= periodo_inicio:
                ofertas.append(dict(id=id, descripcion=descripcion, fecha_inicio=oferta_inicio, fecha_fin=oferta_fin))
        return ofertas
        
    def datos_estudiante(self,username):
        """
        @params: cedula del estudiante
        @return: cedula, nombres, apellidos, fecha_nacimiento, telefono, celular, direccion_actual,
        pais, ciudad, email, genero
        """
        cadena = self.wspersonal.sgaws_datos_estudiante(cedula=username)
        js=json.loads(cadena)
        if js[0] == '_error':
            return js[1]
        else:
            estudiante = dict(cedula=js[0], nombres=js[1].title(), apellidos=js[2].title(),
                              fecha_nacimiento=js[3], telefono=js[4], celular=js[5], direccion_actual=js[6],
                              pais=js[7], ciudad=js[8], email=js[9], genero=js[10],
                            )
        return estudiante

    def datos_docente(self,username):
        """
        @params: cedula del docente
        @return: cedula, nombres, apellidos, titulo, tipo
        """
        cadena = self.wspersonal.sgaws_datos_docente(cedula=username)
        js=json.loads(cadena)
        if js[0] == '_error':
            return js[1]
        else:
            docente = dict(nombres=js[0].title(), apellidos=js[1].title(), cedula=js[2], titulo=js[3], tipo=js[4])
        return docente

    def datos_usuario(self,username):
        """
        @params: cedula del usuario
        @return: cedula, nombres, apellidos, tipo_usuario
        """
        cadena = self.wspersonal.sgaws_datos_usuario(cedula=username)
        js=json.loads(cadena)
        if js[0] == '_error':
            return js[1]
        else:
            usuario = dict(nombres=js[2][0].title(), apellidos=js[2][1].title(), cedula=js[2][2])
            tipo = []
            if 'Estudiante' in js:
                tipo.append('Estudiante')
            if 'Docente' in js:
                tipo.append('Docente')
            usuario.update(dict(tipo=tipo))
        return usuario

        
    def matriculas_estudiante(self,id_oferta,cedula):
        """
        @params: cedula del estudiante
        @return: matriculas [oferta, carrera, modulo, paralelo, matricula, estado]
        """
        respuesta = self.wsacademica.sgaws_carreras_estudiante(cedula=cedula)
        js = json.loads(respuesta)
        if js[0] == '_error':
            return dict(error=js[1])
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
            if js[0] == '_error':
                continue
            """ Todos los paralelos de la carrera en la que está matriculado """
            paralelos = js[4]
            """ Buscamos el paralelo que le corresponde en esta carrera """
            paralelo = None
            for p in paralelos:
                """ id_paralelo, seccion, numero_modulo, nombre_paralelo, id_modulo """
                if m['numero_modulo'] == p[2] and m['paralelo'] == p[3]:
                    paralelo = p
                    break
            """ Extraemos las unidades de su plan de estudios """
            r = self.wsacademica.sgaws_plan_estudio(id_paralelo=paralelo[0])
            js = json.loads(r)
            us = js[6]
            # Se ordenan las unidades de acuerdo a su nombre [1]
            us.sort(lambda x,y: cmp(x[1].upper(),y[1].upper()))
            for id, nombre, horas, creditos, obligatoria in us:
                unidades.append(dict(
                    id=id, carrera=js[0], modulo=js[2], paralelo=js[3],
                    seccion=js[4], unidad=nombre, creditos=creditos, horas=horas
                ))
        return unidades

    def unidades_docente(self,id_oferta, cedula):
        """ 
            @params: id_oferta, cedula del docente
            @return: unidades [carrera, modulo, paralelo, unidad, id]
        """
        r = self.wsacademica.sgaws_carga_horaria_docente(id_oferta=id_oferta, cedula=cedula)
        js = json.loads(r)
        if js[0] == '_error':
            return dict(error=js[1])
        us = js[3]
        # Se ordenan las unidades de acuerdo a su nombre [2]
        us.sort(lambda x,y: cmp(x[2].upper(),y[2].upper()))
        unidades = []
        for carrera, id, nombre, horas, modulo, paralelo in us:
            unidades.append(dict(
                carrera=carrera, modulo=modulo, paralelo=paralelo, unidad=nombre, id=id
            ))
        return unidades

    def unidades_oferta(self,id_oferta):
        """
            Consulta todas las unidades de los planes de estudio de una oferta
            @params: id de la oferta
            @return: unidades [id, carrera, numero_modulo, paralelo, seccion,
            nombre_unidad, creditos_unidad, horas]
        """
        rc = self.wsinstitucional.sgaws_datos_carreras(id_oferta=id_oferta)
        carreras = json.loads(rc)
        if carreras[0] == '_error':
            return dict(error=carreras[1]) 
        unidades = []
        for id_carrera, nombre_carrera, modalidad_carrera in carreras:
            rp = self.wsinstitucional.sgaws_paralelos_carrera(id_oferta=id_oferta, id_carrera=id_carrera)
            jsp = json.loads(rp)
            # Si hay paralelos en esta carrera y en esta oferta académica
            if jsp[0] != '_error':
                paralelos_carrera = jsp[4]
                for id_paralelo, seccion, numero_modulo, nombre_paralelo, id_modulo in paralelos_carrera:
                    ru = self.wsacademica.sgaws_plan_estudio(id_paralelo=id_paralelo)
                    # Si no hay error al obtener unidades del plan
                    jsu = json.loads(ru)
                    if jsu[0] != u'_error':
                        unidades_paralelo = jsu[6]
                        for id, nombre, horas, creditos, obligatoria in unidades_paralelo:
                            unidades.append(dict(
                                id=id, carrera=nombre_carrera, modulo=numero_modulo, paralelo=nombre_paralelo,
                                seccion=seccion, unidad=nombre, creditos=creditos, horas=horas
                            ))
        return unidades

#============================================================================================
# Clase con métodos de script para carga masiva datos.
# @author: miltonlab
#============================================================================================

import datetime
import logging as log

class Script:

    def __init__(self,sgaws_user, sgaws_pass):
        self.sga = SGA(sgaws_user, sgaws_pass)
        thetime = datetime.datetime.now().strftime("%Y-%m-%d")
        log.basicConfig(filename= "sgawsclient-%s.log" % thetime,
                        level   = log.DEBUG, 
                        datefmt = '%Y/%m/%d %I:%M:%S %p', 
                        format  = '%(asctime)s : %(levelname)s - %(message)s')

    #TODO: esperando cambios en el WebService por el metodo unidades_docentes
    def unidades_docentes_oferta(self,id_oferta):
        """
            Consulta todas las unidades con sus docentes de los planes de estudio de una oferta
            @params: id de la oferta
            @return: unidades_docentes [
            carrera, modulo, paralelo, seccion,
            id_unidad, unidad, horas, creditos, fecha_inicio, fecha_fin,
            cedula, nombres, apellidos, titulo
            ]
        """
        rc = self.sga.wsinstitucional.sgaws_datos_carreras(id_oferta=id_oferta)
        carreras = json.loads(rc)
        if carreras[0] == '_error':
            return dict(error=carreras[1]) 
        unidades_docentes = []
        for id_carrera, nombre_carrera, modalidad_carrera in carreras:
            log.info("unidades_docentes() Carrera: " + nombre_carrera)
            rp = self.sga.wsinstitucional.sgaws_paralelos_carrera(id_oferta=id_oferta, id_carrera=id_carrera)
            jsp = json.loads(rp)
            # Si hay paralelos en esta carrera y en esta oferta académica
            if jsp[0] != '_error':
                paralelos_carrera = jsp[4]
                for id_paralelo, seccion, numero_modulo, nombre_paralelo, id_modulo in paralelos_carrera:
                    log.info("unidades_docentes() Paralelo: " + nombre_paralelo)
                    rud = self.sga.wsacademica.sgaws_unidades_docentes_paralelo(id_paralelo=id_paralelo)
                    # Si no hay error al obtener unidades del paralelo
                    jsud = json.loads(rud)
                    if jsud[0] != u'_error':
                        u_d_paralelo = jsud[6]
                        for id_unidad, unidad, horas, creditos, obligatoria, inicio, fin, cedula, nombres, apellidos, titulo  in u_d_paralelo:
                            log.info("unidades_docentes() Unidad: " + unidad)
                            unidades_docentes.append(dict(
                                id_unidad=id_unidad, carrera=nombre_carrera, modulo=numero_modulo, paralelo=nombre_paralelo,
                                seccion=seccion, unidad=unidad, creditos=creditos, horas=horas, inicio=inicio, fin=fin,
                                cedula=cedula, nombres=nombres.title(), apellidos=apellidos.title(), titulo=titulo
                            ))
        return unidades_docentes


    def estudiantes_unidades_oferta(self, id_oferta):
        """
            Consulta todos los estudiantes con las unidades que toma en una oferta dada
            @params: id de la oferta
            @return: estudiantes_unidades [
            carrera, modulo, paralelo, seccion,
            cedula, nombres, apellidos, matricula, estado
            id_unidad, unidad,horas, creditos, obligatoria
            ]
        """
        
        # Obtiene todas las carreras vigentes en una oferta dada
        rc = self.sga.wsinstitucional.sgaws_datos_carreras(id_oferta=id_oferta)
        carreras = json.loads(rc)
        estudiantes_unidades = []        
        if carreras[0] == '_error':
            return dict(error=carreras[1])
        for id_carrera, carrera, modalidad in carreras:
            log.info("estudiantes_unidades() leyendo Carrera: " + carrera)
            # Otiene todos los paralelos de la carrera que se itera
            rp = self.sga.wsinstitucional.sgaws_paralelos_carrera(id_oferta=id_oferta, id_carrera=id_carrera)
            jsp = json.loads(rp)
            if jsp[0] != '_error':
                paralelos_carrera = jsp[4]
                for id_paralelo, seccion, modulo, paralelo, id_modulo in paralelos_carrera:
                    datos = dict(carrera=carrera, modulo=modulo, paralelo=paralelo, seccion=seccion)
                    log.info("estudiantes_unidades() leyendo Paralelo: " + paralelo)
                    ###tmp???
                    if len(paralelos_carrera) == 20:
                        break
                    
                    # Obtiene información de todos los estudiantes del paralelo que se itera
                    r_ep = self.sga.wsacademica.sgaws_estadoestudiantes_paralelo(id_paralelo=id_paralelo)
                    js_ep = json.loads(r_ep)
                    if js_ep[0] != '_error':
                        estudiantes_paralelo = js_ep[5]
                        estudiantes = []
                        for matricula, apellidos, nombres, cedula, estado in estudiantes_paralelo:
                            log.info("estudiantes_unidades() leyendo Estudiante: %s %s %s" % (cedula,nombres,apellidos) ) 
                            estado = estado.replace('EstadoMatricula','')
                            ###estudiantes.append(dict(cedula=cedula, nombres=nombres,
                            ###                        apellidos=apellidos, matricula=matricula, estado=estado))
                            datos.update(dict(cedula=cedula, nombres=nombres.title(), apellidos=apellidos.title(), matricula=matricula, estado=estado))
                            ###???
                            if len(estudiantes_paralelo) == 20:
                                break
                            
                    # Obtiene información de todas las unidades del paralelo que se itera
                    r_up = self.sga.wsacademica.sgaws_plan_estudio(id_paralelo=id_paralelo)
                    js_up = json.loads(r_up)
                    if js_up[0] != '_error':
                        unidades_paralelo = js_up[6]
                        unidades = []    
                        for id_unidad, unidad, horas, creditos, obligatoria in unidades_paralelo:
                            log.info("estudiantes_unidades() leyendo Unidad: %s" % (unidad) )             
                            #unidades.append(dict(id_unidad=id_unidad, unidad=unidad, horas=horas,
                            #                     creditos=creditos, obligatoria=obligatoria))
                            datos.update(dict(id_unidad=id_unidad, unidad=unidad, horas=horas, creditos=creditos, obligatoria=obligatoria))
                            estudiantes_unidades.append(datos)
                                        
                            ###???
                            if len(estudiantes_unidades) == 100:
                                return estudiantes_unidades
                           
        return estudiantes_unidades
