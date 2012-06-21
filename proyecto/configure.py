# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'proyecto.settings'
from proyecto.app.models import EstudiantePeriodoAcademico
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import Asignatura
from proyecto.app.models import Usuario
from proyecto.app.models import User

if proyecto.settings.DEBUG:
    print " * Advertencia: Deshabilite el modo depuracion"
elif not proyecto.settings.SGAWS_USER or not proyecto.settings.SGAWS_PASS:
    print " * Advertencia: No existe el usuario de los Servicios Web del SGA"
elif not proyecto.settings.DATABASES['default']['NAME'] or not proyecto.settings.DATABASES['default']['USER'] or
not proyecto.settings.DATABASES['default']['PASSWORD']:
    print " * Advertencia: Datos de conexion a la BD incompletos"
elif not EstudiantePeriodoAcademico.objects.count() > 10 or not DocentePeriodoAcademico.objects.count() > 10 or
not Asignatura.objects.count() > 10:
    print " * Advertencia: Al parecer no ha importado la informacion del SGA aun"
else:
    print " Exito!!!, puede configurar su servidor de produccion"
    # Eliminar Evaluaciones si existen
    if Evaluacion.objects.count() > 0:
        for e in Evaluacion.objects.all():
            e.delete()
    try:
        # Eliminar usuarios de prueba
        Usuario.objects.get(username='demo').delete()
        User.objects.get(username='admin').delete()
    except Exception:
        pass
        
