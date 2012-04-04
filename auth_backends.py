from django.contrib.auth.models import User
from django.conf import settings
from saes.sgaws import cliente

class SGAAuthBackend(object):

    def __init__(self):
        self.sga = cliente.SGA()
        
    def authenticate(self, username=None, password=None):
        if self.sga.autenticar(username,password):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                e = self.sga.datos_estudiante(username)
                user=User()
                user.username = e['cedula']
                user.password = password
                user.first_name = e['nombres']
                user.last_name = e['apellidos']
                user.email = e['email']
            return user
        else:
            return None

    def get_user(self,id):
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
        
