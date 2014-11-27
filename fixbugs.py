"""
Revisa todas las evaluaciones duplicadas que existan
en el periodo de evaluacion actual para eliminarlos luego.
"""
import os, sys, time, codecs
os.environ['DJANGO_SETTINGS_MODULE']='proyecto.settings'
sys.path+=[os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]]
file=codecs.open("databugs.txt",mode="w",encoding="utf-8")
from proyecto.app.models import Evaluacion, Configuracion
inicio=time.time()
# Filtrar evaluaciones por periodo de Evaluacion
evaluaciones = Evaluacion.objects.filter(cuestionario__periodoEvaluacion=Configuracion.getPeriodoEvaluacionActual())
unicos = []
repetidos = []
secciones=[]
for e in evaluaciones:
        #seccion = (e.estudianteAsignaturaDocente, e.cuestionario, e.fechaInicio, e.horaInicio)
        seccion = (e.estudianteAsignaturaDocente, e.docentePeriodoAcademico, e.parAcademico, e.directorCarrera, e.cuestionario, e.fechaInicio, e.horaInicio)
        if seccion not in secciones:
                secciones.append(seccion)
                unicos.append(e)
        else:
                repetidos.append(e)
print 'total:', len(evaluaciones)
print 'unicos: ', len(unicos)
print 'repetidos: ', len(repetidos)
print repetidos
for r in repetidos:
        file.write(r.__unicode__()+"\n")
        print 'eliminando ...'
        r.delete()
file.close()
fin=time.time()
print 'tiempo: ',(fin - inicio)
