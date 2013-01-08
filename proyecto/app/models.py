# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Count
from proyecto.tools.sgaws.cliente import SGA
from proyecto import settings
from django.contrib.auth.models import User
from datetime import datetime

import logging
logg = logging.getLogger('logapp')

#===================================================================================================
#   Configuraciones
#===================================================================================================

class Configuracion(models.Model):
    """ Configuraciones Globales de la Aplicación """
    periodoAcademicoActual = models.OneToOneField('PeriodoAcademico', null=True, blank=True, verbose_name='Periodo Académico Actual')
    periodoEvaluacionActual = models.OneToOneField('PeriodoEvaluacion', null=True, blank=True, verbose_name='Periodo Evaluación Actual')

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
    # Campocombinado id_unidad:id_paralelo
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


# Todas las carreras
carreras = Asignatura.objects.values_list('carrera', 'carrera').order_by('carrera').distinct()

class DocentePeriodoAcademico(models.Model):
    usuario = models.ForeignKey('Usuario', related_name='docentePeriodosAcademicos')
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='docentes',
                                         verbose_name=u'Periodo Académico', db_column='periodo_academico_id')
    # Atributo agregado por efectos de migracion de docentes sin informacion de asignaturas
    carrera = models.CharField(max_length='500', choices=carreras, blank=True, null=True)
    migrado = models.BooleanField()
    
    class Meta:
        verbose_name = 'Docente'
        unique_together = ('usuario','periodoAcademico')

    def get_carreras(self):
        """ Devuelve una lista de String: Carreras junto con el Área a la que pertenecen """
        carreras  = AsignaturaDocente.objects.filter(
            docente_periodoAcademico=Configuracion.getPeriodoAcademicoActual(),
            docente__id=self.id).values_list('asignatura__carrera', 'asignatura__area').distinct()
        return ['|'.join(c) for c in carreras]


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


# Todas las carrera que riguen en el Periodo Académico Actual
carreras_areas = AsignaturaDocente.objects.filter(
    docente__periodoAcademico=Configuracion.getPeriodoAcademicoActual()).values_list(
    'asignatura__carrera', 'asignatura__area').order_by(
    'asignatura__carrera').distinct()
carreras_areas = [('|'.join(c),'|'.join(c)) for c in  carreras_areas]

class DireccionCarrera(models.Model):
    # Nombre de la Carrera más el Área
    carrera = models.CharField(max_length=255, choices=carreras_areas, unique=True, 
                               verbose_name=u'Carrera-Area')
    # Director o Coordinador de Carrera
    director = models.ForeignKey('DocentePeriodoAcademico', verbose_name=u"Coordinador",
                                 related_name="direcciones")
    def __unicode__(self):
        return u"Coordinación {0}".format(self.carrera)

    def get_docentes(self):
        # separa carrera y area
        ids_docentes = AsignaturaDocente.objects.filter(
            asignatura__carrera=self.carrera.split('|')[0], asignatura__area=self.carrera.split('|')[1]
            ).values_list('docente__id', flat=True).distinct()        
        docentes = DocentePeriodoAcademico.objects.filter(
            periodoAcademico=self.director.periodoAcademico, id__in=ids_docentes).order_by(
            'usuario__last_name', 'usuario__first_name')
        return docentes

    class Meta:
        verbose_name = u'Coordinación de Carrera'
        verbose_name_plural = 'Coordinaciones de Carreras'


#===================================================================================================
#   Información de Encuestas y Evaluación 
#===================================================================================================


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
        self.tipo = 'EstudianteNovel'

class InformanteDirectivos(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'Directivos'

class InformanteInstitutoIdiomas(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'InstitutoIdiomas'

class InformanteEstudianteMED(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'EstudianteMED'

class InformanteIdiomasMED(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'Idiomas MED'

class Cuestionario(models.Model):
    titulo = models.CharField(max_length='100')
    encabezado = models.TextField()
    inicio = models.DateTimeField(u'Inicio de la Encuesta')
    fin=models.DateTimeField(u'Finalización de la Encuesta')
    # Obligatoriedad de todas las preguntas del cuestionario
    preguntas_obligatorias = models.BooleanField(default=True)
    informante = models.ForeignKey(TipoInformante, blank=True, null=True)
    periodoEvaluacion = models.ForeignKey('PeriodoEvaluacion', blank=True, null=True, 
                                          related_name='cuestionarios', verbose_name=u'Periodo de Evaluación'
                                          )
    
    def __unicode__(self):
        return self.titulo

    def clonar(self):
        """
        Crea una copia de un cuestionario incluyendo todas sus secciones y todas sus
        preguntas. Teniendo en cuenta que todos los objetos involucrados seran objetos
        nuevos.
        """
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
    """ 
    Delega la lógica que determina el tipo de evaluación a los controladores
    Se puede acceder a las evaluaciones y autoevaluaciones directamente
    Para acceder a las evaluaciones de los estudiantes utilizar 'estudianteAsignaturaDocente'
    """
    fechaInicio = models.DateField()
    fechaFin = models.DateField()
    horaInicio = models.TimeField()
    horaFin = models.TimeField()
    cuestionario = models.ForeignKey('Cuestionario', related_name='evaluaciones')
    # Evaluaciones de ESTUDIANTES
    estudianteAsignaturaDocente = models.ForeignKey('EstudianteAsignaturaDocente', related_name='evaluaciones', null=True, default=None)
    # Evaluaciones de DOCENTES. Pueden ser evaluaciones y autoevaluaciones 
    docentePeriodoAcademico = models.ForeignKey('DocentePeriodoAcademico', related_name='evaluaciones', null=True)
    # Evaluaciones de DIRECCIONES DE CARRERA # Docente Director
    directorCarrera = models.ForeignKey('DocentePeriodoAcademico', related_name='evaluaciones', null=True)
    # Evaluaciones de DIRECCIONES DE CARRERA # Nombre de la Carrera más el Área
    carreraDirector =  models.CharField(max_length=255, choices=carreras_areas, 
                                        verbose_name=u'Carrera-Area', blank=True, null=True)

    def evaluador(self):
        # Evaluacion del Estudiante a sus docentes
        if self.estudianteAsignaturaDocente:
            evaluador = self.estudianteAsignaturaDocente.estudiante
        # Evaluación de la Comisión Académica de la Carrera al docente
        elif self.directorCarrera and self.docentePeriodoAcademico:
            evaluador = self.directorCarrera
        # Autoevaluacion del docente
        elif self.docentePeriodoAcademico:
            evaluador = self.docentePeriodoAcademico
        return evaluador

    def evaluado(self):
        # Evaluacion del Estudiante a sus docentes
        if self.estudianteAsignaturaDocente:
            evaluado = self.estudianteAsignaturaDocente.asignaturaDocente.docente
        # Evaluación de la Comisión Académica de la Carrera al docente
        elif self.directorCarrera and self.docentePeriodoAcademico:
            evaluado = self.docentePeriodoAcademico
        # Autoevaluacion del docente
        elif self.docentePeriodoAcademico:
            evaluado = self.docentePeriodoAcademico
        return evaluado

    class Meta:
        verbose_name_plural = 'Evaluaciones'
        
    def __unicode__(self):
        return u'{0} - {1} - {2}|{3} - {4}|{5} - {6}'.format(
            self.evaluador().director.cedula() if isinstance(self.evaluador(), DireccionCarrera) else self.evaluador().cedula(), 
            self.evaluado().cedula(), 
            self.fechaInicio, self.horaInicio, self.fechaFin, self.horaFin,
            self.cuestionario.informante
            )

class Resultados(models.Model):
    """
    Clase para forzar un enlace desde al admin de la app
    """
    class Meta:
        #managed = False
        verbose_name_plural = 'Resultados'
        
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
                                     related_name='subsecciones', verbose_name=u'Sección Padre')
    cuestionario = models.ForeignKey(Cuestionario, related_name='secciones')

    def preguntas_ordenadas(self):
        return self.pregunta_set.order_by('orden')

    def __unicode__(self):
        return u'{0} > Cuestionario: {1}'.format(self.titulo, self.cuestionario.titulo)

    def __repr__(self):
         return u'{0} > Cuestionario: {1}'.format(self.titulo, self.cuestionario)

    class Meta:
        ordering = ['orden']
        verbose_name = u'sección'
        verbose_name_plural = 'secciones'

        
class Pregunta(models.Model):
    codigo = models.CharField(max_length='5', null=True, blank=True)
    texto = models.TextField()
    descripcion = models.TextField(null=True, blank=True)
    orden = models.IntegerField()
    tipo = models.ForeignKey(TipoPregunta)
    seccion = models.ForeignKey(Seccion, related_name='preguntas')
    
    def __unicode__(self):
        return u'{0}'.format(self.texto)

    def __repr__(self):
        return u'{0} > {1}'.format(self.texto, self.seccion.titulo)

    class Meta:
        ordering = ['seccion__orden','orden']


class ItemPregunta(models.Model):
    # Valor para la contestación de la pregunta
    texto = models.CharField(max_length='50')
    # Observaciones adicionales para la contestación
    descripcion = models.CharField(max_length='70', null=True, blank=True)
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
    nombre = models.CharField(max_length='300')
    descripcion = models.TextField(null=True)
    observaciones = models.TextField(null=True, blank=True)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='periodosEvaluacion', verbose_name="Periodo Académico")
    areasSGA = models.ManyToManyField(AreaSGA, related_name='periodosEvaluacion', verbose_name=u'Areas Académicas SGA')
    
    class Meta:
        ordering = ['inicio']
        verbose_name = 'Periodo Evaluación'
        verbose_name_plural = 'Periodos de Evaluación'
        
    def noIniciado(self):
        ahora = datetime.today()
        return ahora < self.inicio
    
    def vigente(self):
        ahora = datetime.today()
        return self.inicio <=  ahora <= self.fin 

    def finalizado(self):
        ahora = datetime.today()
        return ahora > self.fin

    def verificar_estudiante(self, cedula):
        """
        Analiza si el Estudiante a realizado todas las evaluaciones
        que le corresponden en este Periodo de Evaluación.
        """
        try:
            EstudiantePeriodoAcademico.objects.get(usuario__cedula=cedula)
        except EstudiantePeriodoAcademico.DoesNotExist:
            logg.error('Verificar estudiante: dni {} no existe'.format(cedula))
            return False

        evaluaciones = Evaluacion.objects.filter(
            estudianteAsignaturaDocente__estudiante__usuario__cedula=cedula).filter(
            cuestionario__periodoEvaluacion=self).count()
        total = EstudianteAsignaturaDocente.objects.filter(
            estudiante__usuario__cedula=cedula).filter(
            estudiante__periodoAcademico=self.periodoAcademico).count()
        restantes = total - evaluaciones
        mensaje = u"{0}: total {1}, evaluados {2}, restan {3} ".format(cedula, total, evaluaciones, restantes)
        logg.info(mensaje)
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
    (u'ESE2012', u'Tabulación Satisfacción Estudiantil 2012'),
    (u'EAAD2012', u'Tabulación Actividades Adicionales Docencia 2012'),
)

class Tabulacion(models.Model):
    """
    Superclase que permite procesar la informacion generada por un
    conjunto de encuestas pertenecientes a un Periodo de Evaluación.
    """
    descripcion = models.CharField(max_length='250')
    tipo = models.CharField( max_length='20', unique=True, choices=tipos_tabulacion)
    periodoEvaluacion = models.OneToOneField('PeriodoEvaluacion', related_name='tabulacion', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Tabulaciones" 
        
    def __unicode__(self):
        return self.descripcion


class TabulacionAdicionales2012:
    tipo = u'EAAD2012'
    descripcion = u'Evaluación Actividades Adicionales a la Docencia 2012'

    def __init__(self, periodoEvaluacion=None):
        self.periodoEvaluacion = periodoEvaluacion
        self.calculos = (
            # codigo, descripcion, metodo, titulo 
            ('a',u'Resultados de la Evaluación de Actividades Adicionales a la Docencia POR DOCENTE',
            self.por_docente, u'Evaluación Actividades Adicionales por Docente'),
            ('b',u'Resultados de la Evaluación de Actividades Adicionales a la Docencia POR CARRERA',
             self.por_carrera, u'Evaluación Actividades Adicionales por Carrera'),
        )
        
    def por_docente(self, siglas_area, nombre_carrera, id_docente):
        """
        Resultados de la Evaluación de Actividades Adicionales a la Docencia 2012 POR DOCENTE
        """
        pass

    def por_carrera(self, siglas_area, nombre_carrera):
        """ 
        Resultados de la Evaluación de Actividades Adicionales a la Docencia 2012 POR CARRERA
        """
        pass


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
            # codigo, descripcion, metodo, titulo 
            ('a',u'La valoracion global de la Satisfacción Estudiantil por DOCENTE',
            self.por_docente, u'Satisfacción Estudiantil por Docente'),
            ('b',u'La valoracion global de la Satisfacción Estudiantil por CARRERA',
             self.por_carrera, u'Satisfacción Estudiantil en la Carrera'),
            ('c',u'La valoracion  de la Satisfacción Estudiantil en cada uno de los CAMPOS, por carrera',
             self.por_campos, u'Satisfacción Estudiantil en Por Campos Específicos'),
            ('d',u'La valoración estudiantil en cada uno de los INDICADORES por carrera',
             self.por_indicador, u'Satisfacción Estudiantil por Indicador'),
            ('e',u'Los 10 indicadores de mayor SATISFACCIÓN en la Carrera',
             self.mayor_satisfaccion, u'Indicadores de Mayor Satisfacción'),
            ('f',u'Los 10 indicadores de mayor INSATISFACCIÓN en la Carrera',
             self.mayor_insatisfaccion, u'Indicadores de mayor Insatisfacción'),
        )
 

    # TODO: Pendiente refactorizar 
    def por_docente(self, siglas_area, nombre_carrera, id_docente):
        """
        Satisfacción Estudiantil de un docente en los  módulos, cursos, unidades o talleres
        """
        if siglas_area == u'ACE':
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'InstitutoIdiomas')
        else:
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'Estudiante')        
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        # Se seleccionan solo ids para poder comparar
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)
        conteo_ms=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            # Unica diferencia con respecto al método 'por_carrera'
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(
            # Recordatorio: 'pregunta' en Cuestionario es int no de tipo Pregunta
            pregunta__in=indicadores).values('pregunta').annotate(MS=Count('respuesta')).filter(
            respuesta='4').order_by('pregunta')
        conteo_s=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            # Unica diferencia con respecto al método 'por_carrera'
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(            
            pregunta__in=indicadores).values('pregunta').annotate(S=Count('respuesta')).filter(
            respuesta='3').order_by('pregunta')
        conteo_ps=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            # Unica diferencia con respecto al método 'por_carrera'
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(            
            pregunta__in=indicadores).values('pregunta').annotate(PS=Count('respuesta')).filter(
            respuesta='2').order_by('pregunta')
        conteo_ins=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
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
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
                # Unica diferencia con respecto al método 'por_carrera'
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(
                pregunta__in=indicadores).count()
            totales['total'] = universo
            porcentajes = {}
            for grado in ('MS','S','PS','INS'):
                if universo != 0:
                    numero  = totales[grado] * 100 / float(universo)
                else:
                    numero = 0
                porcentajes[grado] = numero
            porcentajes['MSS'] = porcentajes['MS'] + porcentajes['S']
            
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)
    

    # TODO: Usar carrera_id en vez de nombre_carrera?
    def por_carrera(self, siglas_area, nombre_carrera):
        # Todas las Secciones de todos los cuestionarios que pertenecen al periodo de evaluación establecido
        if siglas_area == u'ACE':
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'InstitutoIdiomas')
        else:
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'Estudiante')
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        # Se seleccionan solo ids para poder comparar
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)
        conteo_ms=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(MS=Count('respuesta')).filter(
            respuesta='4').order_by('pregunta')
        conteo_s=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(S=Count('respuesta')).filter(
            respuesta='3').order_by('pregunta')
        conteo_ps=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(PS=Count('respuesta')).filter(
            respuesta='2').order_by('pregunta')
        conteo_ins=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
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
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
                pregunta__in=indicadores).count()
            totales['total'] = universo
            porcentajes = {}
            for grado in ('MS','S','PS','INS'):
                if universo is not 0:
                    numero  = totales[grado] * 100 / float(universo)
                else:
                    numero = 0
                porcentajes[grado] = numero
            porcentajes['MSS'] = porcentajes['MS'] + porcentajes['S']
            
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)
    

    def por_campos(self, siglas_area, nombre_carrera, id_seccion):
        # @param id_seccion representa el campo del cuestionario. Seccion = Campo
        if id_seccion == None:
            return None
        # La sección especcífica del cuestionario (por Área) que corresponde
        # ya se determina en la vista anterior
        seccion = Seccion.objects.get(id=id_seccion)
        logg.info("Campo Seccion: " + str(seccion.id) + str(seccion))
        # Se tratan unicamente preguntas abiertas
        if seccion.orden == 4:
            return self.por_otros_aspectos(siglas_area, nombre_carrera, seccion)
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        # de que pertenezcan únicamente al campo (sección) especificado.
        # Se seleccionan solo ids para poder comparar luego
        indicadores=Pregunta.objects.filter(seccion=seccion).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)
        conteo_ms=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(MS=Count('respuesta')).filter(
            respuesta='4').order_by('pregunta')
        conteo_s=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(S=Count('respuesta')).filter(
            respuesta='3').order_by('pregunta')
        conteo_ps=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(PS=Count('respuesta')).filter(
            respuesta='2').order_by('pregunta')
        conteo_ins=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
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
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
                pregunta__in=indicadores).count()
            totales['total'] = universo            
            porcentajes = {}
            for grado in ('MS','S','PS','INS'):
                if universo is not 0:
                    numero  = totales[grado] * 100 / float(universo)
                else:
                    numero = 0
                porcentajes[grado] = numero
            porcentajes['MSS'] = porcentajes['MS'] + porcentajes['S']
            
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)

    
    def por_otros_aspectos(self, siglas_area, nombre_carrera, seccion):
        indicadores=Pregunta.objects.filter(seccion=seccion).filter(tipo__tipo=u'Ensayo').values_list('id', flat=True)

        conteo=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta','respuesta').annotate(
            frecuencia=Count('respuesta')).order_by('pregunta')
        # Para acceder a los datos del objeto pregunta en el template
        for c in conteo:
            c['pregunta'] = Pregunta.objects.get(id=c['pregunta'])
        return conteo
    
    def por_indicador(self,siglas_area, nombre_carrera, id_pregunta ):
        # @param id_pregunta representa el indicador del campo del cuestionario. Pregunta = Indicador
        # La pregunta especcífica del cuestionario (por Área) que corresponde
        # ya se determina en la vista anterior
        # Se selecciona unicamente el id para la comparación posterior
        indicadores = (id_pregunta, )
        conteo_ms=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(MS=Count('respuesta')).filter(
            respuesta='4').order_by('pregunta')
        conteo_s=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(S=Count('respuesta')).filter(
            respuesta='3').order_by('pregunta')
        conteo_ps=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(PS=Count('respuesta')).filter(
            respuesta='2').order_by('pregunta')
        conteo_ins=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
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
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
                pregunta__in=indicadores).count()
            totales['total'] = universo
            porcentajes = {}
            for grado in ('MS','S','PS','INS'):
                if universo is not 0:
                    numero = totales[grado] * 100 / float(universo)
                else:
                    numero = 0
                porcentajes[grado] = numero
            porcentajes['MSS'] = porcentajes['MS'] + porcentajes['S']
            
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)
        

    def mayor_satisfaccion(self, siglas_area, nombre_carrera):
        # Todas las Secciones de todos los cuestionarios que pertenecen al periodo de evaluación establecido
        if siglas_area == u'ACE':
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'InstitutoIdiomas')
        else:
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'Estudiante')
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        # Se seleccionan solo ids para poder comparar
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)
        conteo_ms=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(MS=Count('respuesta')).filter(
            respuesta='4').order_by('pregunta')
        conteo_s=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(S=Count('respuesta')).filter(
            respuesta='3').order_by('pregunta')
        conteo_ps=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(PS=Count('respuesta')).filter(
            respuesta='2').order_by('pregunta')
        conteo_ins=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(INS=Count('respuesta')).filter(
            respuesta='1').order_by('pregunta')
        conteos = []
        # Se contabiliza por cada pregunta
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
        # Ordenar de mayor a menor por 'MS' luego por 'S'        
        conteos.sort(lambda c1, c2: -cmp(c1['MS'],c2['MS']) or -cmp(c1['S'],c2['S'] ))
        return dict(conteos=conteos[:10], totales=None, porcentajes=None)

        
    def mayor_insatisfaccion(self, siglas_area, nombre_carrera):
        # Todas las Secciones de todos los cuestionarios que pertenecen al periodo de evaluación establecido
        if siglas_area == u'ACE':
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'InstitutoIdiomas')
        else:
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'Estudiante')
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        # Se seleccionan solo ids para poder comparar
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)
        conteos = self._contabilizar(siglas_area, nombre_carrera, indicadores)
        # Ordenar de mayor a menor por 'INS' luego por 'PS'
        conteos.sort(lambda c1, c2: -cmp(c1['INS'], c2['INS']) or -cmp(c1['PS'], c2['PS'] ))
        return dict(conteos=conteos[:10], totales=None, porcentajes=None)

    
    def _contabilizar(self, siglas_area, nombre_carrera, indicadores=[], id_docente=None):
        """
        @param indicadores: lista de ids de pregunta que se involucran en el conteo
        @param id_docente: para el caso único en el que no se contabiliza en toda la carrera
        """
        conteo_ms=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(MS=Count('respuesta')).filter(
            respuesta='4').order_by('pregunta')
        conteo_s=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(S=Count('respuesta')).filter(
            respuesta='3').order_by('pregunta')
        conteo_ps=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(PS=Count('respuesta')).filter(
            respuesta='2').order_by('pregunta')
        conteo_ins=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(INS=Count('respuesta')).filter(
            respuesta='1').order_by('pregunta')
        if id_docente:
            conteo_ms = conteo_ms.filter(evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente)
            conteo_s = conteo_s.filter(evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente)
            conteo_ps = conteo_ps.filter(evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente)
            conteo_ins = conteo_ins.filter(evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente)
        conteos = []
        # Se contabiliza por cada pregunta
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
        return conteos



#===================================================================================================
#   Autenticación y Usuarios
#===================================================================================================

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
        equivalencias = {u'magister':u'Mg.', u'magíster':u'Mg.', u'ing.':u'Ing.', u'ingeniero':u'Ing.', u'ingeniera':u'Ing.',
                         u'Ing.':u'Ing.', u'doctor':u'Dr.', u'doctora':u'Dra.', u'master':u'Ms.',
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

