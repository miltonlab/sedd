# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.conf import settings
from proyecto.app.models import Usuario
from tools.sgaws import cliente
import logging
logg = logging.getLogger('logapp')


class SGAAuthBackend(object):

    supports_object_permissions = False
    supports_anonymous_user = False

    def __init__(self):
        self.sga = cliente.SGA(settings.SGAWS_USER, settings.SGAWS_PASS)
        
    def authenticate(self, username=None, password=None):
        if self.sga.autenticar_estudiante(username, password):
            try:
                user = Usuario.objects.get(username=username)
            except Exception, ex:
                print "Error, revise los datos y la conexion al WebService del SGA: " + str(ex)
                user = None
            except User.DoesNotExist:
                e = self.sga.datos_estudiante(username)
                user = Usuario()
                user.username = e['cedula']
                # De ser necesario metodo de autenticacion por defecto                
                user.set_password(password)
                user.first_name = e['nombres']
                user.last_name = e['apellidos']
                user.email = e['email']
                user.cedula = e['cedula']
            return user
        elif self.sga.autenticar_docente(username,password):
            try:
                user = Usuario.objects.get(username=username)
            except User.DoesNotExist:
                d = self.sga.datos_docente(username)
                user = Usuario()
                user.username = d['cedula']
                # De ser necesario metodo de autenticacion por defecto
                user.set_password(password)
                user.first_name = d['nombres']
                user.last_name = d['apellidos']
                user.cedula = d['cedula']
                user.titulo = d['titulo']
            return user
        else:
            return None

    def get_user(self,id):
        ###u=self.sga.datos_usuario(id)
        try:
            return Usuario.objects.get(pk=id)
        except User.DoesNotExist:
            return None
        """
        if u:
            user=Usuario()
            user.username = u['cedula']
            user.cedula = u['cedula']            
            user.first_name = u['nombres']
            user.last_name = u['apellidos']
            return user
        else:
            return None
        """


class DNIAuthBackend(object):
    """
    Autenticación Basada en el DNI. Debe utilizarselo en caso de
    no funcionar la conexión al WebService de autenticación del SGA.
    """
    supports_object_permissions = False

    def authenticate(self, username=None, password=None):
        if username == password:
            try:
                user = Usuario.objects.get(username=username)
            except User.DoesNotExist:
                user = None
            return user
        else:
            return None
        
    def get_user(self,id):
        try:
            return Usuario.objects.get(pk=id)
        except User.DoesNotExist:
            return None

class EmailAuthBackend(object):
    """
    Autenticación Basada en:
    usuario: email
    clave: dni
    """
    supports_object_permissions = False

    def authenticate(self, username=None, password=None):
        try:
            user = Usuario.objects.get(email=username, cedula=password)
        except User.DoesNotExist:
            user = None
        return user
        
    def get_user(self,id):
        try:
            return Usuario.objects.get(pk=id)
        except User.DoesNotExist:
            return None
