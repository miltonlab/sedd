from django.contrib.auth.models import User
from django.conf import settings
from proyecto.app.models import Usuario

from sgaws import cliente

class SGAAuthBackend(object):

    def __init__(self):
        self.sga = cliente.SGA(settings.SGAWS_USER, settings.SGAWS_PASS)
        
    def authenticate(self, username=None, password=None):
        if self.sga.autenticar_estudiante(username,password):
            try:
                #user = User.objects.get(username=username)
                user = Usuario.objects.get(username=username)
            except User.DoesNotExist:
                e = self.sga.datos_estudiante(username)
                #user=User()
                user = Usuario()
                user.username = e['cedula']
                user.password = password
                user.first_name = e['nombres']
                user.last_name = e['apellidos']
                user.email = e['email']
                user.cedula = e['cedula']
                #user.usuario = Usuario(cedula=e['cedula'])
            return user
        elif self.sga.autenticar_docente(username,password):
            try:
                #user = User.objects.get(username=username)
                user = Usuario.objects.get(username=username)
            except User.DoesNotExist:
                d = self.sga.datos_docente(username)
                #user=User()
                user = Usuario()
                user.username = d['cedula']
                user.password = password
                user.first_name = d['nombres']
                user.last_name = d['apellidos']
                user.cedula = d['cedula']
                user.titulo = d['titulo']
                #user.usuario = Usuario(cedula=d['cedula'], titulo=d['titulo'])
            return user
        else:
            return None

    def get_user(self,id):
        ###pendiente revisar para docente
        e=self.sga.datos_estudiante(id)
        if e:
            user=User()
            user.username = e['cedula']
            user.first_name = e['nombres']
            user.last_name = e['apellidos']
            user.email = e['email']
            return user
        else:
            return None
        
