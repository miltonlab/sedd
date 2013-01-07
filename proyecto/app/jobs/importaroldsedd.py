# -*- coding: utf-8 -*-

from django_extensions.management.jobs import BaseJob
import os, sys, datetime

os.environ['DJANGO_SETTINGS_MODULE']='proyecto.settings'
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../../../'))
from proyecto.app.models import PeriodoAcademico, DocentePeriodoAcademico, Usuario
import proyecto.settings as confs
import logging

import MySQLdb as mysql

logg = logging.getLogger('logapp')
# carreras : {(id_area, id_carrera): nombre_carrera}
carreras = {(1, 1): u'Cultura F\xedsica', 
            (1, 2): u'Inform\xe1tica Educativa',
            (1, 3): u'Comunicaci\xf3n Social',
            (1, 4): u'Psicolog\xeda Infantil y Educaci\xf3n Parvularia',
            (1, 5): u'M\xfasica',
            (1, 6): u'Idioma Ingl\xe9s',
            (1, 7): u'Educaci\xf3n B\xe1sica',
            (1, 8): u'Dise\xf1o de Interiores y Decoraci\xf3n de Ambientes',
            (1, 9): u'Psicolog\xeda Educativa y Orientaci\xf3n',
            (1, 10): u'Psicorrehabilitacion y Educaci\xf3n Especial',
            (1, 11): u'Lengua Castellana y Literatura',
            (1, 13): u'Artes Pl\xe1sticas',
            (1, 14): u'Qu\xedmica y Biolog\xeda',
            (1, 15): u'F\xedsico Matem\xe1ticas',
            (1, 17): u'Educaci\xf3n B\xe1sica (Extensi\xf3n)',
            (2, 1): u'Medicina Humana',
            (2, 2): u'Enfermer\xeda',
            (2, 3): u'Odontolog\xeda',
            (2, 4): u'Psicolog\xeda Cl\xednica',
            (2, 5): u'Radiolog\xeda e Imagen Diagn\xf3stica',
            (2, 6): u'Laboratorio Cl\xednico',
            (3, 1): u'Derecho',
            (3, 2): u'Economia',
            (3, 3): u'Ingenier\xeda en Contabilidad y Auditor\xeda',
            (3, 4): u'Trabajo Social',
            (3, 5): u'Ingenier\xeda en Administraci\xf3n Tur\xedstica',
            (3, 6): u'Ingenier\xeda en Banca y Finanzas',
            (3, 7): u'Administraci\xf3n de Empresas',
            (3, 8): u'Administraci\xf3n P\xfablica',
            (3, 10): u'Derecho (extension)',
            (4, 1): u'Producci\xf3n Educaci\xf3n y Extensi\xf3n Agropecuarias',
            (4, 2): u'Ingenier\xeda Forestal',
            (4, 3): u'Manejo y Conservaci\xf3n del Medio Ambiente',
            (4, 4): u'Ingenier\xeda Agron\xf3mica',
            (4, 5): u'Medicina Veterinaria y Zootecnia',
            (4, 6): u'Ingenier\xeda Agr\xedcola',
            (5, 2): u'Ingenier\xeda en Geolog\xeda Ambiental y Ordenamiento Territorial',
            (5, 3): u'Ingenier\xeda en Electromec\xe1nica',
            (5, 4): u'Ingenier\xeda en Sistemas',
            (5, 5): u'Ingenier\xeda en Electr\xf3nica y Telecomunicaciones',
            (5, 6): u'Tecnolog\xeda en Electricidad y Control Industrial',
            (6, 138): u'Curso de Ingles',
            (6, 139): u'Curso de Franc\xe9s',
            (6, 141): u'Curso de Ruso'
        }

class Job(BaseJob):
    """
    Tarea para importar docentes de la Base de Datos del Antiguo Sitema de Evaluacion de Docentes
    @author: miltonlab
    @date: 31/12/2012
    """
    help = "Importador de docentes oldsedd."
    
    def execute(self):
        # Periodo en el sistema antiguo
        anio = 2012
        # Id Periodo en el sistema SEDD
        id_periodo = 1
        periodoAcademico = PeriodoAcademico.objects.get(id=id_periodo)        
        sql = "select distinct ced_doc, nom_doc, apel_doc, tit_doc, c.id_area, c.id_car, c.des_car from dicta{0} as u join (docente{1} as d, carrera as c) on (u.id_doc = d.id_doc and u.id_area = c.id_area and u.id_car = c.id_car) order by c.id_area, c.id_car".format(anio, anio)
        conexion = mysql.Connection(confs.OLD_HOST, confs.OLD_USER, confs.OLD_PASS, confs.OLD_DBNAME)
        cursor = conexion.cursor()
        cursor.execute(sql)
        rows  = cursor.fetchall()
        nuevos = []
        for row in rows:
            cedula = row[0]
            carrera = carreras.get((row[4], row[5]), None)
            try:
                DocentePeriodoAcademico.objects.get(periodoAcademico__id=id_periodo, 
                                                    usuario__cedula=cedula)
            except DocentePeriodoAcademico.DoesNotExist:
                dict_usuario = dict(username=cedula, password='', first_name=row[1].decode('latin1').title(),
                                    last_name=row[2].decode('latin1').title(), cedula=cedula, 
                                    titulo=row[3].decode('latin1'), email='')
                logg.info('Usuario a migrar: {0}'.format(dict_usuario))
                (usuario, nuevo) = Usuario.objects.get_or_create(cedula=cedula, defaults=dict_usuario)
                if not carrera:
                    logg.info('Carrera del sistema anterior no encontrada: {0}, {1}, {2}'.
                             format(row[4], row[5], row[6]))
                    continue
                docente = DocentePeriodoAcademico(usuario=usuario, periodoAcademico=periodoAcademico, carrera=carrera, migrado=True)
                docente.save()
                logg.info('Migrado el docente {0}'.format(docente))
                nuevos.append(docente)
        cursor.close()
        conexion.close()

if __name__ == '__main__':
    j=Job()
    j.execute()
