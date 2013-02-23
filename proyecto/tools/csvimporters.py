
from proyecto.app.models  import PeriodoAcademico
from proyecto.app.models  import DocentePeriodoAcademico
from proyecto.app.models  import EstudiantePeriodoAcademico
from proyecto.app.models  import Asignatura
from proyecto.app.models  import Usuario
import datetime
from datetime import datetime 
import codecs 

def importar_docentes(archivo, paralelo=False):
    f = codecs.open(archivo, mode='rb', encoding='utf-8')
    lineas = f.readlines()
    docentes = []
    for linea in lineas:
        # Con cierta validacion
        cedula, nombres, apellidos, titulo, email, periodoAcademicoId  = linea.split(';')[:6]
        try:
            usuario = Usuario.objects.get(cedula=cedula)
        except Usuario.DoesNotExist:
            usuario = Usuario()
            usuario.username = cedula
            usuario.cedula = cedula
            usuario.first_name = nombres
            usuario.last_name = apellidos
            usuario.titulo = titulo
            usuario.email = email
        try:
            periodoAcademicoId = int(periodoAcademicoId)
            periodoAcademico = PeriodoAcademico.objects.get(id=periodoAcademicoId)
        except (PeriodoAcademico.DoesNotExist, ValueError):
            periodoAcademico = None
        docente = DocentePeriodoAcademico(usuario=usuario, periodoAcademico=periodoAcademico)
        docentes.append(docente)
    return docentes


def importar_estudiantes(archivo=None, paralelo=False):
    f = codecs.open(archivo, mode='rb', encoding='utf-8')
    lineas = f.readlines()
    estudiantes = []
    for linea in lineas:
        if paralelo:
            cedula, nombres, apellidos, titulo, email, periodoAcademicoId, paralelo  = linea.split(';')
        else:
            # Se toma solo los 6 primeros campos, por validacion
            cedula, nombres, apellidos, titulo, email, periodoAcademicoId = linea.split(';')[:6]
        try:
            usuario = Usuario.objects.get(cedula=cedula)
        except Usuario.DoesNotExist:
            usuario = Usuario()
            usuario.username = cedula
            usuario.cedula = cedula
            usuario.first_name = nombres
            usuario.last_name = apellidos
            usuario.titulo = titulo
            usuario.email = email
        try:
            periodoAcademicoId = int(periodoAcademicoId)
            periodoAcademico = PeriodoAcademico.objects.get(id=periodoAcademicoId)
        except (PeriodoAcademico.DoesNotExist, ValueError):
            periodoAcademico = None
        estudiante = EstudiantePeriodoAcademico(usuario=usuario, periodoAcademico=periodoAcademico)
        if paralelo:
            estudiantes.append(dict(estudiante=estudiante, paralelo=paralelo))
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
                nombre=lista[6], tipo=lista[7], creditos=int(lista[8]), 
                duracion=float(lista[9]), inicio=datetime.strptime(lista[10],'%d/%m/%Y').date(), 
                fin=datetime.strptime(lista[11],'%d/%m/%Y').date(), 
                idSGA=lista[12].replace(' ','').upper(), periodoAcademico=periodoAcademico
                )
            if docente:
                cedula = lista[13]
                docente = DocentePeriodoAcademico.objects.get(
                    usuario__cedula=cedula, periodoAcademico=periodoAcademico
                    )
                asignaturas.append(dict(asignatura=asignatura, docente=docente))
            else:
                asignaturas.append(asignatura)
        except ValueError, err:
            print "Error al convertir datos para Asignaturas: ",err

    return asignaturas
