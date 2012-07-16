# -*- coding: utf-8 -*-

from django.db import models
from proyecto.tools.sgaws.cliente import SGA
from proyecto import settings
from django.contrib.auth.models import User
from datetime import datetime


class TipoInformante(models.Model): 
    # TODO: Clase Abstracta
    tipo = models.CharField(max_length='20', unique=True)
    descripcion = models.CharField(max_length='100')

    def __unicode__(self):
        return self.tipo


class InformanteDocente(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'Docente'        

    
class InformanteEstudiante(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'Estudiante'


class InformanteEstudianteNovel(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'Estudiante Novel'

class InformanteDirectivos(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'Directivos'

class InformanteInstitutoIdiomas(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'Instituto Idiomas'

class InformanteEstudianteMED(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'Estudiante MED'

class InformanteIdiomasMED(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'Idiomas MED'

class Cuestionario(models.Model):
    titulo = models.CharField(max_length='100')
    encabezado = models.TextField()
    ### TODO: revisar cambio incio por inicio
    inicio = models.DateTimeField('Inicio de la Encuesta')
    fin=models.DateTimeField('Finalización de la Encuesta')
    informante = models.ForeignKey(TipoInformante, blank=True, null=True)
    periodoEvaluacion = models.ForeignKey('PeriodoEvaluacion', blank=True, null=True, related_name='cuestionarios')
    
    def __unicode__(self):
        return self.titulo

    def clonar(self):
        numero = Cuestionario.objects.count()
        nuevo = Cuestionario()
        nuevo.titulo = u'{0} (Clonado {1})'.format(self.titulo, str(numero+1))
        nuevo.encabezado = self.encabezado
        nuevo.inicio = self.inicio
        nuevo.fin = self.fin
        # No se relacionan para mayor flexibilidad
        nuevo.informante = None
        nuevo.periodoEvaluacion = None
        nuevo.save()
        for seccion in self.secciones.all():
            nuevaSeccion = Seccion()
            nuevaSeccion.titulo = seccion.titulo
            nuevaSeccion.descripcion = seccion.descripcion
            nuevaSeccion.orden = seccion.orden
            nuevaSeccion.seccionPadre = None
            nuevaSeccion.cuestionario = nuevo 
            nuevaSeccion.save()
            for pregunta in seccion.preguntas.all():
                nuevaPregunta = Pregunta()
                nuevaPregunta.texto = pregunta.texto
                nuevaPregunta.orden = pregunta.orden
                nuevaPregunta.tipo = pregunta.tipo
                nuevaPregunta.seccion = nuevaSeccion
                nuevaPregunta.save()
                for item in pregunta.items.all():
                    nuevoItem = ItemPregunta()
                    nuevoItem.texto = item.texto
                    nuevoItem.orden = item.orden
                    nuevoItem.pregunta = nuevaPregunta
                    nuevoItem.save()
        return nuevo


class Contestacion(models.Model):
    pregunta = models.IntegerField()
    respuesta = models.TextField()
    evaluacion = models.ForeignKey('Evaluacion', related_name='contestaciones')

    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
        
    def __unicode__(self):
        return u'{0}:{1}'.format(self.pregunta, self.respuesta)
    
    
class Evaluacion(models.Model):
    fechaInicio = models.DateField()
    fechaFin = models.DateField()
    horaInicio = models.TimeField()
    horaFin = models.TimeField()
    cuestionario = models.ForeignKey('Cuestionario', related_name='evaluaciones')
    estudianteAsignaturaDocente = models.ForeignKey('EstudianteAsignaturaDocente', related_name='evaluaciones')

    class Meta:
        verbose_name_plural = 'Evaluaciones'
        
    def __unicode__(self):
        return u'{0} - {1} - {2}::{3}'.format(self.estudianteAsignaturaDocente.estudiante.cedula(),
                                           self.estudianteAsignaturaDocente.asignaturaDocente.docente.cedula(),
                                           self.fechaInicio, self.horaInicio, )
    

        
class TipoPregunta(models.Model):
    # TODO: Clase Abstracta
    tipo = models.CharField(max_length='20', unique=True)
    descripcion = models.CharField(max_length='100')

    def __unicode__(self):
        return self.tipo


class SeleccionUnica(TipoPregunta):
    def __init__(self):
        TipoPregunta.__init__(self)
        self.tipo = 'SeleccionUnica'
        self.descripcion = 'Se visualiza  radio buttons'

    def __unicode__(self):
        return u'Selección Única'
            

class Ensayo(TipoPregunta):
    def __init__(self):
        TipoPregunta.__init__(self)
        self.tipo = 'Ensayo'
        self.descripcion = 'Se visualiza con un area de texto'


class Seccion(models.Model):
    titulo = models.CharField(max_length='50')
    descripcion  = models.CharField(max_length='100')
    orden = models.IntegerField()
    seccionPadre = models.ForeignKey('self', null=True, blank=True, db_column='seccion_padre_id',
                                     related_name='subsecciones', verbose_name='Sección Padre')
    cuestionario = models.ForeignKey(Cuestionario, related_name='secciones')

    def preguntas_ordenadas(self):
        return self.pregunta_set.order_by('orden')

    def __unicode__(self):
        return u'{0} > Cuestionario: {1}'.format(self.titulo, self.cuestionario)

    class Meta:
        ordering = ['orden']
        verbose_name = 'sección'
        verbose_name_plural = 'secciones'

        
class Pregunta(models.Model):
    texto = models.TextField(max_length='100')
    orden = models.IntegerField()
    tipo = models.ForeignKey(TipoPregunta)
    seccion = models.ForeignKey(Seccion, related_name='preguntas')
    
    def __unicode__(self):
        return u'{0} > {1}'.format(self.texto, self.seccion.titulo)

    class Meta:
        ordering = ['seccion__orden','orden']


class ItemPregunta(models.Model):
    texto = models.CharField(max_length='50')
    pregunta = models.ForeignKey(Pregunta, related_name='items')
    orden = models.IntegerField()

    def __unicode__(self):
        return self.texto

    class Meta:
        ordering = ['orden']


class AreaSGA(models.Model):
    siglas = models.CharField(max_length='10')
    nombre = models.CharField(max_length='256') 

    def __unicode__(self):
        return self.siglas

    class Meta:
        ordering=['id']


class PeriodoEvaluacion(models.Model):
    nombre = models.CharField(max_length='100')
    descripcion = models.TextField(null=True)
    inicio = models.DateField()
    fin = models.DateField()
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='periodosEvaluacion', verbose_name="Periodo Académico")
    areasSGA = models.ManyToManyField(AreaSGA, related_name='periodosEvaluacion', verbose_name=u'Areas Académicas SGA')
    
    class Meta:
        ordering = ['inicio']
        verbose_name = 'Periodo Evaluación'
        verbose_name_plural = 'Periodos de Evaluación'
        
    def noIniciado(self):
        hoy = datetime.today().date()
        return hoy < self.inicio
    
    def vigente(self):
        hoy = datetime.today().date()
        return self.inicio <=  hoy <= self.fin 

    def finalizado(self):
        hoy = datetime.today().date()
        return hoy > self.fin

    def verificar_estudiante(self, cedula):
        """
        Analiza si el Estudiante a realizado todas las evaluaciones
        que le corresponden en este Periodo de Evaluación.
        """
        evaluaciones = Evaluacion.objects.filter(
            estudianteAsignaturaDocente__estudiante__usuario__cedula=cedula).filter(
            cuestionario__periodoEvaluacion=self).count()
        total = EstudianteAsignaturaDocente.objects.filter(
            estudiante__usuario__cedula=cedula).filter(
            estudiante__periodoAcademico=self.periodoAcademico).count()
        restantes = total - evaluaciones
        mensaje = "{0}: total {1}, evaluados {2}, restan {3} ".format(cedula, total, evaluaciones, restantes)
        ###logg.info(mensaje)
        ###print mensaje
        if restantes == 0:
            return True
        else:
            return False

    def contabilizar_evaluaciones(self, area, carrera, semestre=None, paralelo=None):
        consulta = EstudianteAsignaturaDocente.objects.filter(
            asignaturaDocente__asignatura__area=area,
            asignaturaDocente__asignatura__carrera=carrera)
        if semestre and semestre != '':
            consulta = consulta.filter(asignaturaDocente__asignatura__semestre=semestre)
        if paralelo and paralelo != '':
            consulta = consulta.filter(asignaturaDocente__asignatura__paralelo=paralelo)
        estudiantes = set([c.estudiante for c in consulta.all()])
        total = len(estudiantes)
        completados = 0
        faltantes = 0
        for e in estudiantes:
            if self.verificar_estudiante(e.usuario.cedula):
                completados += 1
            else:
                faltantes +=1
        return dict(estudiantes=total, completados=completados, faltantes=faltantes)
        
    def __unicode__(self):
        return self.nombre

# TODO: Modelar de mejor manera la funcionalidad
tipos_tabulacion = (
    (u'ESE2012', u'Tabulación  Satisfacción Estudiantil 2012'),
)

class Tabulacion(models.Model):
    """
    Superclase que permite procesar la informacion generada por un
    conjunto de encuestas pertenecientes a un Periodo de Evaluación.
    """
    descripcion = models.CharField(max_length='250')
    tipo = models.CharField( max_length='20', unique=True, choices= tipos_tabulacion)
    periodoEvaluacion = models.OneToOneField('PeriodoEvaluacion', related_name='tabulacion', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Tabulaciones" 
        
    def __unicode__(self):
        return self.descripcion

    
class TabulacionSatisfaccion2012:
    # Se hecha de menos las clases Abstractas y el polimorfismo
    # Esta clase no se persiste

    tipo = u'ESE2012'
    descripcion = u'Encuesta de Satisfacción Estudiantil 2012'

        
    def __init__(self, periodoEvaluacion=None):
        self.periodoEvaluacion = periodoEvaluacion
        #Tabulacion.__init__(self)
        #self.tipo = u'ESE2012'
        #self.descripcion = u'Encuesta de Satisfacción Estudiantil 2012'
        self.calculos = (
            # codigo, descripcion, metodo 
            ('a',u'La valoracion global de la Satisfacción Estudiantil por docente',
            self.por_docente),
            ('b',u'La valoracion global de la Satisfacción Estudiantil por carrera',
             self.por_carrera),
            ('c',u'La valoracion  de la Satisfacción Estudiantil en cada uno de los campos, por carrera',
             self.por_campos),
            ('d',u'La valoración Estudiantil en cada uno de los indicadores por carrera',
             self.por_indicador),
            ('e',u'Los 10 indicadores de mayor satisfacción en la Carrera',
             self.mayor_satisfaccion),
            ('f',u'Los 10 indicadores de mayor satisfacción en la Carrera',
             self.mayor_satisfaccion),
        )

  

    ###Pendiente terminar        
    def por_docente(self, nombre_area, nombre_carrera, id_docente):
        """
        Satisfacción Estudiantil de un docente en los  módulos, cursos, unidades o talleres
        """
        from django.db.models import Count
        # Todas las Secciones de todos los cuestionarios que pertenecen al periodo de evaluación establecido 
        secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all())
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)
        conteo_ms=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            # Unica diferencia con respecto al método 'por_carrera'
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(            
            pregunta__in=indicadores).values('pregunta').annotate(MS=Count('respuesta')).filter(
            respuesta='4').order_by('pregunta')
        conteo_s=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            # Unica diferencia con respecto al método 'por_carrera'
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(            
            pregunta__in=indicadores).values('pregunta').annotate(S=Count('respuesta')).filter(
            respuesta='3').order_by('pregunta')
        conteo_ps=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            # Unica diferencia con respecto al método 'por_carrera'
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(            
            pregunta__in=indicadores).values('pregunta').annotate(PS=Count('respuesta')).filter(
            respuesta='2').order_by('pregunta')
        conteo_ins=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            # Unica diferencia con respecto al método 'por_carrera'
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(            
            pregunta__in=indicadores).values('pregunta').annotate(INS=Count('respuesta')).filter(
            respuesta='1').order_by('pregunta')
        conteos = []
        for i in indicadores:
            conteo = {}            
            for c in conteo_ms:
                if c['pregunta'] == i:
                    conteo.update(c)
                    # Se intercambia por el objeto completo por versatilidad
                    conteo['pregunta'] = Pregunta.objects.get(id=i)
            for c in conteo_s:
                if c['pregunta'] == i:
                    conteo.update(c)
                    conteo['pregunta'] = Pregunta.objects.get(id=i)
            for c in conteo_ps:
                if c['pregunta'] == i:
                    conteo.update(c)
                    conteo['pregunta'] = Pregunta.objects.get(id=i)
            for c in conteo_ins:
                if c['pregunta'] == i:
                    conteo.update(c)
                    conteo['pregunta'] = Pregunta.objects.get(id=i)
            for grado in ('MS','S','PS','INS'):
                if grado not in conteo.keys():
                    conteo[grado] = 0
            conteos.append(conteo)
            totales = {}
            for grado in ('MS','S','PS','INS'):
                totales[grado] = sum([c[grado] for c in conteos])
            universo = Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
                evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
                # Unica diferencia con respecto al método 'por_carrera'
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(
                pregunta__in=indicadores).count()
            porcentajes = {}
            for grado in ('MS','S','PS','INS'):
                numero  = totales[grado] * 100 / float(universo)
                porcentajes[grado] = '%.2f'%numero
                
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)
    

    # TODO: Usar carrera_id en vez de nombre_carrera
    def por_carrera(self, nombre_area, nombre_carrera):
        from django.db.models import Count
        # Todas las Secciones de todos los cuestionarios que pertenecen al periodo de evaluación establecido 
        secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all())
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)
        conteo_ms=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(MS=Count('respuesta')).filter(
            respuesta='4').order_by('pregunta')
        conteo_s=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(S=Count('respuesta')).filter(
            respuesta='3').order_by('pregunta')
        conteo_ps=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(PS=Count('respuesta')).filter(
            respuesta='2').order_by('pregunta')
        conteo_ins=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(INS=Count('respuesta')).filter(
            respuesta='1').order_by('pregunta')
        conteos = []
        for i in indicadores:
            conteo = {}            
            for c in conteo_ms:
                if c['pregunta'] == i:
                    conteo.update(c)
                    # Se intercambia por el objeto completo por versatilidad
                    conteo['pregunta'] = Pregunta.objects.get(id=i)
            for c in conteo_s:
                if c['pregunta'] == i:
                    conteo.update(c)
                    conteo['pregunta'] = Pregunta.objects.get(id=i)
            for c in conteo_ps:
                if c['pregunta'] == i:
                    conteo.update(c)
                    conteo['pregunta'] = Pregunta.objects.get(id=i)
            for c in conteo_ins:
                if c['pregunta'] == i:
                    conteo.update(c)
                    conteo['pregunta'] = Pregunta.objects.get(id=i)
            for grado in ('MS','S','PS','INS'):
                if grado not in conteo.keys():
                    conteo[grado] = 0
            conteos.append(conteo)
            totales = {}
            for grado in ('MS','S','PS','INS'):
                totales[grado] = sum([c[grado] for c in conteos])
            universo = Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
                evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=nombre_area).filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
                pregunta__in=indicadores).count()
            porcentajes = {}
            for grado in ('MS','S','PS','INS'):
                numero  = totales[grado] * 100 / float(universo)
                porcentajes[grado] = '%.2f'%numero
                
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)
    

    def por_campos(self, nombre_area, nombre_carrera, campo):
        print 'por docente' 

    def por_indicador(self):
        print 'por docente' 

    def mayor_satisfaccion(self):
        print 'por docente' 

    def mayor_insatisfaccion(self):
        print 'por docente' 

    
#===================================================================================================
#   Información Académica
#===================================================================================================


class OfertaAcademicaSGA(models.Model):
    idSGA = models.IntegerField(verbose_name='Id_SGA', unique=True, db_column='id_sga', null=True, blank=True)
    descripcion = models.CharField(max_length='100', verbose_name='Descripción')

    class Meta:
        verbose_name = 'Oferta Académica'
        verbose_name_plural = 'Ofertas Académicas'
    
    def __unicode__(self):
        return self.descripcion


class PeriodoAcademico(models.Model):
    nombre = models.CharField(max_length='50')
    inicio = models.DateField()
    fin = models.DateField()
    periodoLectivo = models.CharField(max_length=100,db_column='periodo_lectivo')
    ofertasAcademicasSGA = models.ManyToManyField('OfertaAcademicaSGA', related_name='peridosAcademicos', blank=True, null=True, verbose_name='Ofertas SGA')

    def cargarOfertasSGA(self):
        proxy = SGA(settings.SGAWS_USER, settings.SGAWS_PASS)
        ofertas_dict = proxy.ofertas_academicas(self.inicio, self.fin)
        ofertas = [OfertaAcademicaSGA(idSGA=oa['id'], descripcion=oa['descripcion'])  for oa in ofertas_dict]
        for oa in ofertas:
            try:
                OfertaAcademicaSGA.objects.get(idSGA=oa.idSGA)
            except OfertaAcademicaSGA.DoesNotExist:
                # Se agregan solo en el caso que no existan aún la oferta académica
                oa.periodoAcademico = self
                oa.save()

    def save(self, *args, **kwargs):
        """
           Cada vez que se crea un nuevo Periodo Académico se consultan las ofertas academicas del SGA para adherirlas.
           Luego se pueden eliminar desde la aplicación de administración.
           @author: Milton Labanda
           @date: 04-05-2012
        """
        nuevo = False
        if not self.pk:
            nuevo = True
        super(PeriodoAcademico, self).save(*args, **kwargs)
        if nuevo:
            self.cargarOfertasSGA()
            
    class Meta:
        ordering = ['inicio']
        verbose_name = 'Periodo Académico'
        verbose_name_plural = 'Periodos Académicos'
        
    def __unicode__(self):
        return self.nombre


class Asignatura(models.Model):
    area = models.CharField(max_length='20')
    #TODO: experimento
    #area = models.CharField(max_length='20', choices=[(a,a) for a in Asignatura.objects.values('area').distinct()] )
    carrera = models.CharField(max_length='100')
    semestre = models.CharField(max_length='10', verbose_name='módulo')
    paralelo = models.CharField(max_length='50')
    seccion = models.CharField(max_length='10')
    nombre = models.TextField()
    tipo = models.CharField(max_length='15')
    creditos = models.IntegerField(verbose_name='número de créditos')
    duracion = models.FloatField(verbose_name='duración en horas')
    inicio = models.DateField(null=True, verbose_name='inicia')
    fin = models.DateField(null=True, verbose_name='termina')
    # Campo combinado id_unidad:id_paralelo
    idSGA = models.CharField(max_length='15', db_column='id_sga')

    def esVigente(self):
        """ Determina si la asignatura se dicta dentro del Periodo de Evaluación Actual """
        periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
        if self.inicio <= periodoEvaluacion.fin and self.fin >= periodoEvaluacion.inicio:
            return True
        else:
            return False
                
    def getTipo(self):
        tipos = [u'taller',u'curso',u'módulo',u'modulo',u'unidad']
        l = [t for t in tipos if t in self.nombre.lower()]
        return l[0]  if l else u'otro'    

    def save(self, *args, **kwargs):
        self.tipo = self.getTipo()
        super(Asignatura, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return u"{0} - {1}".format(self.idSGA, self.nombre)

    
class EstudiantePeriodoAcademico(models.Model):
    usuario = models.ForeignKey('Usuario', related_name='estudiantePeriodosAcademicos')
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='estudiantes',
                                         verbose_name='Periodo Académico', db_column='periodo_academico_id')

    class Meta:
        verbose_name = 'Estudiante'
        unique_together = ('usuario', 'periodoAcademico')

    def cedula(self):
        return self.usuario.cedula
    
    def paralelos(self):
        consulta = self.asignaturasDocentesEstudiante.values_list('asignaturaDocente__asignatura__area',
                                                                  'asignaturaDocente__asignatura__carrera',
                                                                  'asignaturaDocente__asignatura__semestre',
                                                                  'asignaturaDocente__asignatura__paralelo',
                                                                  'asignaturaDocente__asignatura__seccion',).distinct()
        # Se construye una lista de diccionarios
        datos = [dict(zip(('area','carrera','modulo','paralelo','seccion'),r)) for r in consulta]
        return datos

    def __unicode__(self):
        return self.usuario.get_full_name()
    

class EstudianteAsignaturaDocente(models.Model):
    estudiante = models.ForeignKey('EstudiantePeriodoAcademico', related_name='asignaturasDocentesEstudiante')
    asignaturaDocente = models.ForeignKey('AsignaturaDocente', related_name='estudiantesAsignaturaDocente',
                                          verbose_name='Asignatura - Docente')
    matricula = models.IntegerField(blank=True, null=True)    
    estado = models.CharField(max_length='60', blank=True, null=True)

    def get_area(self):
        return self.asignaturaDocente.asignatura.area
    get_area.short_description = 'Area'
        
    def get_carrera(self):
        return self.asignaturaDocente.asignatura.carrera[:60]
    get_carrera.short_description = 'Carrera'
    
    def get_semestre(self):
        return self.asignaturaDocente.asignatura.semestre
    get_semestre.short_description = 'Semestre'

    def get_paralelo(self):
        return self.asignaturaDocente.asignatura.paralelo
    get_paralelo.short_description = 'Paralelo'
    
    def get_nombre_corto(self):
        return self.__unicode__()[:60]
    get_nombre_corto.short_description = 'Nombre'

    def get_asignatura(self):
        return self.asignaturaDocente.asignatura
        
    # Campos para adicionar en el Admin a través del formulario  EstudianteAsignaturaDocenteAdminForm
    carrera = property(get_carrera,)
    semestre = property(get_semestre,)
    paralelo = property(get_paralelo,)
    
    class Meta:
        verbose_name = 'Estudiante Asignaturas'
        verbose_name_plural = 'Estudiantes y Asignaturas'
        unique_together = ('estudiante','asignaturaDocente')

    def __unicode__(self):
        return u"{0} >> {1}".format(self.estudiante, self.asignaturaDocente)


class AsignaturaDocente(models.Model):
    asignatura = models.ForeignKey('Asignatura', related_name='docentesAsignatura')
    docente = models.ForeignKey('DocentePeriodoAcademico', related_name='asignaturasDocente')

    def get_idSGA(self):
        return self.asignatura.idSGA

    def get_carrera(self):
        return self.asignatura.carrera[:60]
    get_carrera.short_description = 'Carrera'
    
    def get_semestre(self):
        return self.asignatura.semestre
    get_semestre.short_description = 'Semestre'
    
    def get_paralelo(self):
        return self.asignatura.paralelo
    get_paralelo.short_description = 'Paralelo'
    
    def get_nombre_corto(self):
        ancho = 60
        s = self.__unicode__()
        return s[:ancho]
    get_nombre_corto.short_description = 'Nombre'

    # Campos para adicionar en el Admin a través del formulario  EstudianteAsignaturaDocenteAdminForm
    carrera = property(get_carrera,)
    semestre = property(get_semestre,)
    paralelo = property(get_paralelo,)
    
    class Meta:
        verbose_name = 'Asignatura Docente'
        verbose_name_plural = 'Asignaturas y Docentes'
        unique_together = ('docente','asignatura')

    def __unicode__(self):
        return u"{0} >> {1}".format(self.docente, self.asignatura.nombre)


class DocentePeriodoAcademico(models.Model):
    usuario = models.ForeignKey('Usuario', related_name='docentePeriodosAcademicos')
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='docentes', verbose_name='Periodo Académico', db_column='periodo_academico_id')
    esCoordinador = models.BooleanField()
    
    
    class Meta:
        verbose_name = 'Docente'
        unique_together = ('usuario','periodoAcademico')

    def paralelos(self):
        result = self.asignaturasDocente.values_list('asignatura__area', 'asignatura__carrera',
                                            'asignatura__semestre','asignatura__paralelo',
                                            'asignatura__seccion').distinct()
        datos = [dict(zip(('area','carrera','modulo','paralelo','seccion'),r)) for r in result]
        return datos

    
    def cedula(self):
        return self.usuario.cedula
        
    def __unicode__(self):
        return u'{0} {1}'.format(self.usuario.abreviatura, self.usuario.get_full_name())


#===================================================================================================
#   Autenticación y Usuarios
#===================================================================================================

# from django.contrib.auth.models

class Usuario(User):
    """
    Perfil de Usuario que podrá pertener a los grupos Estudiante y/o Docente
    """
    cedula = models.CharField(max_length='15', unique=True)
    titulo = models.CharField(max_length='100', blank=True, null=True)

    def get_nombres(self):
        return self.first_name

    def set_nombres(self, nombres):
        self.first_name = nombres

    def get_apellidos(self):
        return self.last_name

    def set_apellidos(self, apellidos):
        self.last_name = apellidos

    def get_abreviatura(self):
        equivalencias = {u'magister':u'Mg.', u'ingeniero':u'Ing.', u'ingeniera':u'Ing.', u'doctor':u'Dr.', u'doctora':u'Dra.', u'master':u'Ms.',
                         u'mg.':u'Mg.', u'licenciado':u'Lic.', u'licenciada':u'Lic.', u'economista':u'Eco.', u'eco.':u'Eco.', u'medico':u'Dr.',
                         u'dra.':u'Dra.',u'dr.':u'Dr.',u'lic.':u'Lic.', u'licdo.':u'Lic.',u'ing.':u'Ing.', u'phd.':u'Phd.',u'médico':u'Dr.',
                         u'odontólogo': u'Odont.', u'odontóloga': u'Odont.', u'odontologo': u'Odont.', u'odontologa': u'Odont.'  
                         }
        palabras = self.titulo.split() if self.titulo else ""
        for p in palabras:
            if p.lower() in equivalencias.keys():
                return equivalencias[p.lower()]
        return ""
        
    nombres = property(get_nombres, set_nombres)
    apellidos = property(get_apellidos, set_apellidos)
    abreviatura = property(get_abreviatura)
        
    def __repr__(self):
        return u'<[{0}] {1}>'.format(self.cedula, self.get_full_name());

    def __unicode__(self):
        return self.get_full_name()



class Configuracion(models.Model):
    """ Configuraciones Globales de la Aplicación """
    periodoAcademicoActual = models.OneToOneField(PeriodoAcademico, null=True, blank=True, verbose_name='Periodo Académico Actual')
    periodoEvaluacionActual = models.OneToOneField(PeriodoEvaluacion, null=True, blank=True, verbose_name='Periodo Evaluación Actual')

    @classmethod
    def getPeriodoAcademicoActual(self):
        return Configuracion.objects.get(id=1).periodoAcademicoActual
    
    @classmethod
    def getPeriodoEvaluacionActual(self):
        return Configuracion.objects.get(id=1).periodoEvaluacionActual
    
    class Meta:
        verbose_name = u'Configuraciones'
        verbose_name_plural = u'Configuraciones'

    def __unicode__(self):
        return u"Configuraciones de la Aplicación"
