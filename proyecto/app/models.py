#-*- encoding=utf8 -*-

from django.db import models
from sgaws.cliente import SGA
from django.contrib import auth
from proyecto import settings

import logging

log = logging.getLogger('logapp')


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


class Cuestionario(models.Model):
    titulo = models.CharField(max_length='100')
    encabezado = models.TextField()
    incio = models.DateTimeField('Inicio de la Encuesta')
    fin=models.DateTimeField('Finalización de la Encuesta')
    informante = models.ForeignKey(TipoInformante)
    periodoEvaluacion = models.ForeignKey('PeriodoEvaluacion', related_name='cuestionarios')
    
    def __unicode__(self):
        return self.titulo


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


class Ensayo(TipoPregunta):
    
    def __init__(self):
        TipoPregunta.__init__(self)
        self.tipo = 'Ensayo'
        self.descripcion = 'Se visualiza con un area de texto'


class Seccion(models.Model):
    titulo = models.CharField(max_length='50')
    descripcion  = models.CharField(max_length='100')
    orden = models.IntegerField()
    seccionPadre = models.ForeignKey('self', null=True, blank=True, db_column='seccion_padre_id', related_name='subsecciones', verbose_name='Sección Padre')
    cuestionario = models.ForeignKey(Cuestionario)

    def preguntas_ordenadas(self):
        return self.pregunta_set.order_by('orden')

    def __unicode__(self):
        return self.titulo

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
        return self.texto

    class Meta:
        ordering = ['orden']


class ItemPregunta(models.Model):
    texto = models.CharField(max_length='50')
    pregunta = models.ForeignKey(Pregunta, related_name='items')
    orden = models.IntegerField()

    def __unicode__(self):
        return self.texto

    class Meta:
        ordering = ['orden']


class Respuesta(models.Model):
    texto = models.CharField(max_length='100')
    fechaHora = models.DateTimeField(db_column='fecha_hora')
    itemPregunta = models.ForeignKey(ItemPregunta,db_column='item_pregunta_id', related_name='respuestas')

    def __unicode__(self):
        return self.texto


class PeriodoEvaluacion(models.Model):
    nombre = models.CharField(max_length='100')
    inicio = models.DateField()
    fin = models.DateField()
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='periodosEvaluacion')
    
    class Meta:
        ordering = ['inicio']
        verbose_name = 'Periodo Evaluación'
        verbose_name_plural = 'Periodos de Evaluación'
        

    def __unicode__(self):
        return self.nombre


#===================================================================================================
#   Información Académica
#===================================================================================================


class OfertaAcademicaSGA(models.Model):
    idSGA = models.IntegerField(verbose_name='Id_SGA', unique=True, db_column='id_sga')
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
    ofertasAcademicasSGA = models.ManyToManyField('OfertaAcademicaSGA', related_name='peridosAcademicos', blank=True, null=True)

    def cargarOfertasSGA(self):
        proxy = SGA(settings.SGAWS_USER, settings.SGAWS_PASS)
        ofertas_dict = proxy.ofertas_academicas(self.inicio, self.fin)
        ofertas = [OfertaAcademicaSGA(id_sga=oa['id'], descripcion=oa['descripcion'])  for oa in ofertas_dict]
        log.info(ofertas)
        for oa in ofertas:
            try:
                OfertaAcademicaSGA.objects.get(id_sga=oa.id_sga)
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

    def cargarInfoSGA(self):
        """
            Carga la información académica (Estudiantes, Docentes y Materias del SGA)
        """
        pass
            
    class Meta:
        ordering = ['inicio']
        verbose_name = 'Periodo Académico'
        verbose_name_plural = 'Periodos Académicos'
        
    def __unicode__(self):
        return self.nombre


class Asignatura(models.Model):
    area = models.CharField(max_length='20')
    carrera = models.CharField(max_length='100')
    semestre = models.CharField(max_length='10', verbose_name='módulo')
    paralelo = models.CharField(max_length='10')
    #TODO: agregar columna
    #seccion = models.CharField(max_length='10')
    nombre = models.TextField()
    tipo = models.CharField(max_length='15')
    creditos = models.IntegerField(verbose_name='número de créditos')
    duracion = models.FloatField(verbose_name='duración en horas')
    idSGA = models.CharField(max_length='20', db_column='id_sga')

    def getTipo(self):
        tipos = [u'taller',u'curso',u'módulo',u'modulo',u'unidad']
        l = [t for t in tipos if t in self.nombre.lower()]
        return l[0]  if l else u'otro'    

    def save(self, *args, **kwargs):
        self.tipo = self.getTipo()
        super(Asignatura, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return "{0} - {1}".format(self.idSGA, self.nombre)

    
class EstudiantePeriodoAcademico(models.Model):
    estudiante = models.ForeignKey('Usuario', related_name='estudiantePeriodosAcademicos')
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='estudiantes', verbose_name='Periodo Académico', db_column='periodo_academico_id')
    #asignaturas = models.ManytoManyField('Asignatura', through='EstudiantePeriodoAcademicoAsignatura', related_name='estudiantes')

    class Meta:
        verbose_name = 'Estudiante'

    def __repr__(self):
        return self.estudiante.__repr__()

    def __str__(self):
        return self.estudiante.__str__()


class EstudiantePeriodoAcademicoAsignatura(models.Model):
    estudiante = models.ForeignKey('EstudiantePeriodoAcademico', related_name='asignaturas')
    asignatura = models.ForeignKey('Asignatura', related_name='estudiantes')
    matricula = models.IntegerField(null=True)    
    estado = models.CharField(max_length='30', blank=True, null=True)

    class Meta:
        verbose_name = 'Asignaturas Estudiante'


class DocentePeriodoAcademico(models.Model):
    docente = models.ForeignKey('Usuario', related_name='docentePeriodosAcademicos')
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='docentes', verbose_name='Periodo Académico', db_column='periodo_academico_id')
    #asignaturas = models.ManyToManyField('Asignatura', related_name='docentes')

    class Meta:
        verbose_name = 'Docente'

    def __repr__(self):
        return self.docente.__repr__()

    def __str__(self):
        return self.docente.__str__()


class DocentePeriodoAcademicoAsignatura(models.Model):
    docente = models.ForeignKey('DocentePeriodoAcademico', related_name='asignaturas')
    asignatura = models.ForeignKey('Asignatura', related_name='docentes')

    class Meta:
        verbose_name = 'Asignaturas Docente'


#===================================================================================================
#   Autenticación
#===================================================================================================

class Usuario(auth.models.User):
    """
    Perfil de Usuario que podrá pertener a los grupos Estudiante y/o Docente
    """
    ###user = models.ForeignKey(User)
    cedula = models.CharField(max_length='15', unique=True)
    titulo = models.CharField(max_length='60', blank=True, null=True)
    tipo = models.CharField( max_length=1, choices=(('E','Estudiante'), ('D','Docente')) )

    ###pendiente
    def saveTMP(self):
        pass
    
    def __repr__(self):
        return '<[%s] %s>' % (self.cedula, self.get_full_name());

    def __str__(self):
        return self.get_full_name()
