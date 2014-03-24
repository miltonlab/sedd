
from proyecto.app.models  import PeriodoAcademico
from proyecto.app.models  import DocentePeriodoAcademico
from proyecto.app.models  import EstudiantePeriodoAcademico
from proyecto.app.models  import Asignatura
from proyecto.app.models  import AsignaturaDocente
from proyecto.app.models  import EstudianteAsignaturaDocente
from proyecto.app.models  import Usuario

import datetime
from datetime import datetime 
import codecs 

def importar_docentes(archivo):
    """
    archivo: csv
    """
    f = codecs.open(archivo, mode='rb', encoding='utf-8')
    lineas = f.readlines()
    docentes = []
    for linea in lineas:
        # Con cierta validacion
        cedula, nombres, apellidos, titulo, email, periodoAcademicoId  = linea.split(';')[:6]
        if len(cedula) == 9:
            cedula = '0' + cedula.strip()
        try:
            usuario = Usuario.objects.get(username=cedula)
        except Usuario.DoesNotExist:
            usuario = Usuario()
            usuario.username = cedula.strip()
            usuario.cedula = cedula.strip()
            usuario.first_name = nombres.strip()
            usuario.last_name = apellidos.strip()
            usuario.titulo = titulo.strip()
            usuario.email = email.strip()
            # Se graba el usuario
            usuario.save()
        try:
            periodoAcademicoId = int(periodoAcademicoId)
            periodoAcademico = PeriodoAcademico.objects.get(id=periodoAcademicoId)
        except (PeriodoAcademico.DoesNotExist, ValueError):
            periodoAcademico = None
        docente = DocentePeriodoAcademico.objects.get_or_create(usuario=usuario, periodoAcademico=periodoAcademico)
        docentes.append(docente)
    return docentes


def importar_estudiantes(archivo=None, asignatura=False):
    """
    archivo: csv
    asignatura: asignatura/paralelo
    """
    f = codecs.open(archivo, mode='rb', encoding='utf-8')
    lineas = f.readlines()
    estudiantes = []
    for linea in lineas:
        if asignatura:
            cedula, nombres, apellidos, email, periodoAcademicoId, asignatura_paralelo = linea.split(';')
        else:
            # Se toma solo los 6 primeros campos, por validacion
            cedula, nombres, apellidos, email, periodoAcademicoId = linea.split(';')[:5]
        if len(cedula) == 9:
            cedula = '0' + cedula.strip()
        try:
            usuario = Usuario.objects.get(cedula=cedula)
        except Usuario.DoesNotExist:
            usuario = Usuario()
            usuario.username = cedula.strip()
            usuario.cedula = cedula.strip()
            usuario.first_name = nombres.strip()
            usuario.last_name = apellidos.strip()
            usuario.email = email.strip()
            # Se graba el usuario
            usuario.save()
        try:
            periodoAcademicoId = int(periodoAcademicoId)
            periodoAcademico = PeriodoAcademico.objects.get(id=periodoAcademicoId)
        except (PeriodoAcademico.DoesNotExist, ValueError):
            periodoAcademico = None
        (estudiante, nuevo) = EstudiantePeriodoAcademico.objects.get_or_create(
            usuario=usuario, periodoAcademico=periodoAcademico)
        if asignatura:
            asignatura_paralelo=asignatura_paralelo.strip().replace(' ','').replace('\n','')
            #asignaturasDocente = AsignaturaDocente.objects.filter(asignatura__idSGA=idSGA).all()
            asignaturasDocente = AsignaturaDocente.objects.filter(asignatura__nombre=asignatura_paralelo).all()
            for ad in asignaturasDocente:
                ead = EstudianteAsignaturaDocente.objects.get_or_create(estudiante=estudiante, asignaturaDocente=ad)
            #estudiantes.append(dict(estudiante=estudiante, idSGA=idSGA.replace(' ','').replace('\n','')))
        else:
            estudiantes.append(estudiante)
    return estudiantes


def importar_asignaturas(archivo, docente=False):
    f = codecs.open(archivo, mode='rb', encoding='utf-8')
    lineas = f.readlines()
    asignaturas = []
    for linea in lineas:
        lista = linea.split(';')[:14]
        try:
            try:
                periodoAcademicoId = int(lista[13])
                periodoAcademico = PeriodoAcademico.objects.get(id=periodoAcademicoId)
            except PeriodoAcademico.DoesNotExist:
                periodoAcademico = None
            asignatura = Asignatura(
                area=lista[0], carrera=lista[1], semestre=lista[2], 
                paralelo=lista[3], seccion=lista[4], modalidad=lista[5],
                nombre=lista[6].strip(), tipo=lista[7], creditos=int(lista[8]), 
                duracion=float(lista[9]), inicio=datetime.strptime(lista[10],'%d/%m/%Y').date(), 
                fin=datetime.strptime(lista[11],'%d/%m/%Y').date(), 
                idSGA=lista[12].strip().replace(' ','').upper(), periodoAcademico=periodoAcademico
                )
            asignatura.save()
            if docente:
                cedula = linea.split(';')[14].replace('\n','')
                try:
                    docente = DocentePeriodoAcademico.objects.get(
                        usuario__cedula=cedula, periodoAcademico=periodoAcademico
                        )
                    # Se crea asignaturaDocente
                    (asignatura, nuevo) = AsignaturaDocente.objects.get_or_create(asignatura=asignatura, docente=docente)
                except DocentePeriodoAcademico.DoesNotExist:
                    print "Error no existe el docente {0}".format(cedula)
                    docente = None
	    asignaturas.append(asignatura)
        except ValueError, err:
            print "Error al convertir datos para Asignaturas: ",err

    return asignaturas
