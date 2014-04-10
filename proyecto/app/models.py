# -*- coding: utf-8 -*-

from django.db import models
from django.db import connection
from django.db.models import Q
from django.db.models import Count
from django.db.models import exceptions
from django.contrib.auth.models import User
from datetime import datetime
from ordereddict import OrderedDict
import lxml.html
import logging

from proyecto.tools.sgaws.cliente import SGA
from proyecto import settings

logg = logging.getLogger('logapp')

#===================================================================================================
#   Configuraciones
#===================================================================================================

class Configuracion(models.Model):
    """ Configuraciones Globales de la Aplicación """
    periodoAcademicoActual = models.OneToOneField('PeriodoAcademico', null=True, blank=True, 
                                                  verbose_name='Periodo Académico Actual')
    periodoEvaluacionActual = models.OneToOneField('PeriodoEvaluacion', null=True, blank=True, 
                                                   verbose_name='Periodo Evaluación Actual')

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
        verbose_name = u'Oferta Académica'
        verbose_name_plural = u'Ofertas Académicas'
    
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
           @date: 04-05-2012
        """
        nuevo = False
        if not self.pk:
            nuevo = True
        super(PeriodoAcademico, self).save(*args, **kwargs)
        if nuevo:
            try:
                self.cargarOfertasSGA()
            except Exception, ex:
                logg.error("Error al cargar ofertas academicas del SGA: {0}".format(ex))

    class Meta:
        ordering = ['inicio', 'fin']
        verbose_name = u'Periodo Académico'
        verbose_name_plural = u'Periodos Académicos'

    def rango(self):
        return '{0} / {1}'.format(self.inicio.strftime('%b %Y'), self.fin.strftime('%b %Y'))
    
    def __unicode__(self):
        return self.nombre


class Asignatura(models.Model):
    area = models.CharField(max_length='20')
    carrera = models.CharField(max_length='100')
    # Codigo de la carrera establecido por la SENESCYT
    carrera_senescyt = models.CharField(max_length='10', default='0000')
    semestre = models.CharField(max_length='10', verbose_name=u'ciclo')
    paralelo = models.CharField(max_length='50')
    seccion = models.CharField(max_length='10')
    modalidad = models.CharField(max_length='20')
    nombre = models.TextField()
    tipo = models.CharField(max_length='15')
    creditos = models.IntegerField(verbose_name=u'número de créditos')
    duracion = models.FloatField(verbose_name=u'duración en horas')
    inicio = models.DateField(null=True, verbose_name='inicia')
    fin = models.DateField(null=True, verbose_name='termina')
    # Campo combinado id_unidad:id_paralelo
    idSGA = models.CharField(max_length='15', db_column='id_sga')
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='asignaturas',
                                         verbose_name=u'Periodo Académico', db_column='periodo_academico_id')


    def esVigente(self):
        """ Determina si la asignatura se dicta dentro del Periodo de Evaluación Actual """
        periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
        if self.inicio <= periodoEvaluacion.fin and self.fin >= periodoEvaluacion.inicio:
            return True
        else:
            return False
                
    def getTipo(self):
        tipos = set([u'asignatura', u'taller', u'curso', u'módulo', u'modulo', u'unidad'])
        nombre = set(self.nombre.lower().split())
        tipo = tipos.intersection(nombre)
        #l = [t for t in tipos if t in self.nombre.lower()]
        #return l[0]  if l else u'otro'    
        return tipo.pop() if len(tipo) else 'asignatura'

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
    ###carrera = models.CharField(max_length='500', choices=carreras, blank=True, null=True)
    carrera = models.CharField(max_length='500', choices=None, blank=True, null=True)
    # Pertenece a la Comision Academica de la Carrera?
    parAcademico = models.BooleanField()
    
    class Meta:
        ordering = ['usuario__last_name', 'usuario__first_name']
        verbose_name = 'Docente'
        unique_together = ('usuario','periodoAcademico')

    def get_carreras_areas(self):
        """ Devuelve una lista de tuplas (carrera, area) pero unicamente del PeriodoAcademicoActual """
        lista_carreras_areas = []
        lista_carreras_areas_query  = AsignaturaDocente.objects.filter(
            docente__periodoAcademico=self.periodoAcademico, #Configuracion.getPeriodoAcademicoActual(),
            docente__id=self.id).values_list('asignatura__carrera', 'asignatura__area').distinct()
        lista_carreras_areas.extend(lista_carreras_areas_query)
        if self.carrera and self.carrera not in [c[0] for c in lista_carreras_areas_query]:
            lista_carreras_areas.append((self.carrera, ''))
        return lista_carreras_areas

    def get_carreras(self):
        return [c[0] for c in self.get_carreras_areas() if c[0]]

    def get_areas(self):
        return [c[1] for c in self.get_carreras_areas() if c[1]]

    def paralelos(self):
        result = self.asignaturasDocente.values_list('asignatura__area', 'asignatura__carrera',
                                            'asignatura__semestre','asignatura__paralelo',
                                            'asignatura__seccion').distinct()
        datos = [dict(zip(('area','carrera','modulo','paralelo','seccion'),r)) for r in result]
        return datos

    def get_datos_evaluadores(self, periodo_evaluacion_id):
        """
        Busca la informacion academica de todos los estudiantes que han evaluado al
        docente en un Periodo de Evaluacion dado.
        @param periodo_evaluacion_id
        @return [semestre, paralelo, nombre_asignatura]
        """
        datos = Evaluacion.objects.filter(
            cuestionario__periodoEvaluacion__id=periodo_evaluacion_id,
            estudianteAsignaturaDocente__asignaturaDocente__docente=self).values_list(
            'estudianteAsignaturaDocente__asignaturaDocente__asignatura__semestre', 
            'estudianteAsignaturaDocente__asignaturaDocente__asignatura__paralelo', 
            'estudianteAsignaturaDocente__asignaturaDocente__asignatura__nombre').order_by(
            'estudianteAsignaturaDocente__asignaturaDocente__asignatura__semestre', 
            'estudianteAsignaturaDocente__asignaturaDocente__asignatura__paralelo', 
            'estudianteAsignaturaDocente__asignaturaDocente__asignatura__nombre').distinct()
        evaluadores = [dict(semestre=d[0], paralelo=d[1], asignatura=d[2]) for d in datos]
        return evaluadores

    def cedula(self):
        return self.usuario.cedula

    def get_nombres_completos():
        return u'{0}'.format(self.usuario.get_full_name())

    def __unicode__(self):
        return u'{0} {1}'.format(self.usuario.abreviatura, self.usuario.get_full_name())


### Todas las carrera que riguen en el Periodo Académico Actual
###
# carreras_areas = AsignaturaDocente.objects.filter(
#     docente__periodoAcademico=Configuracion.getPeriodoAcademicoActual()).values_list(
#     'asignatura__carrera', 'asignatura__area').order_by(
#     'asignatura__carrera').distinct()
# carreras_areas = [('|'.join(c),'|'.join(c)) for c in  carreras_areas]

class DireccionCarrera(models.Model):
    # Nombre de la Carrera más el Área
    ###carrera = models.CharField(max_length=255, choices=carreras_areas, unique=True, 
    ###                           verbose_name=u'Carrera-Area')
    carrera = models.CharField(max_length=255, choices=None, unique=True, 
                               verbose_name=u'Carrera-Area')
    # Director o Coordinador de Carrera
    director = models.ForeignKey('DocentePeriodoAcademico', verbose_name=u"Coordinador",
                                 related_name="direcciones", null=True)
    def __unicode__(self):
        if self.director:
            return u"Coordinación {0} - {1}".format(self.carrera, self.director.periodoAcademico.rango())
        else:
            return u"Coordinación {0} - {1} << Sin Coordinador >> ".format(
                self.carrera, 
                Configuracion.objects.get(id=1).periodoAcademicoActual.rango()
                )

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
        ordering = ['carrera']
        verbose_name = u'Coordinación de Carrera'
        verbose_name_plural = 'Coordinaciones de Carreras'


#===================================================================================================
#   Informacion de Encuestas y Evaluacion 
#===================================================================================================


class TipoInformante(models.Model): 
    tipo = models.CharField(max_length='50', unique=True)
    descripcion = models.CharField(max_length='200')

    def __unicode__(self):
        return self.tipo

    class Meta:
        ordering = ['descripcion']


class Cuestionario(models.Model):
    # Nombre corto para identificacion de objeto
    nombre = models.CharField(max_length='150', default='Cuestionario Sin Nombre')
    titulo = models.CharField(max_length='255')
    encabezado = models.TextField()
    inicio = models.DateTimeField(u'Inicio de la Encuesta')
    fin=models.DateTimeField(u'Finalización de la Encuesta')
    # Obligatoriedad de todas las preguntas del cuestionario
    preguntas_obligatorias = models.BooleanField(default=True)
    # fuente de Verificación en todas las preguntas de Seleccion Unica
    fuente_verificacion = models.BooleanField(default=False, verbose_name=u'Preguntas con fuente de verificación')
    informante = models.ForeignKey(TipoInformante, null=True)
    # Generalmente de acuerdo al Tipo de Informante
    peso = models.FloatField(default=1.0)
    periodoEvaluacion = models.ForeignKey('PeriodoEvaluacion', blank=True, null=True, 
                                          related_name='cuestionarios', verbose_name=u'Periodo de Evaluación')

    def get_secciones(self):
        """ Obtiene todas las secciones. TODO: Aunque NO recursivamente """
        secciones = []
        secciones.extend(self.secciones.all())
        for s in self.secciones.all():
            secciones.extend(s.subsecciones.all())
        return secciones

    def get_preguntas(self):
        """ Obtiene todas las preguntas de todas las secciones y subsecciones """
        preguntas = []
        for s in self.secciones.all():
            # Recursividad
            preguntas.extend(s.get_preguntas())
        return preguntas

    def clonar(self):
        """
        Crea una copia de un cuestionario incluyendo todas sus secciones y todas sus
        preguntas. Teniendo en cuenta que todos los objetos involucrados seran objetos
        nuevos.
        """
        nuevo = Cuestionario()
        nuevo.nombre = u'(Clonado ID {1}) {0}'.format(self.nombre, self.id)
        nuevo.titulo = u'(Clonado ID {1}) {0}'.format(self.titulo, self.id)
        nuevo.encabezado = self.encabezado
        nuevo.inicio = datetime.now()
        nuevo.fin = datetime.now()
        # No se relacionan para mayor flexibilidad
        # Deben fijarse luego en el administrador
        nuevo.informante = self.informante
        nuevo.periodoEvaluacion = None
        nuevo.save()
        for seccion in self.secciones.all():
            nuevaSeccion = seccion.clonar()
            nuevaSeccion.cuestionario = nuevo
            nuevaSeccion.save()
        nuevo.save()    
        return nuevo

    def save(self, *args, **kwargs):
        super(Cuestionario, self).save(*args, **kwargs)
        # Agregar Fuente de verificacion a todas las preguntas de seleccion
        # del cuestinario
        # TODO: Puede que el campo Pregunta.observaciones no sirva solo para
        # determinar la Fuente de Verificacion
        for pregunta in self.get_preguntas():
            # Solo seleccion unica
            if pregunta.tipo.id == 2:
                if self.fuente_verificacion:
                    pregunta.observaciones = u'Fuente de Verificación'
                elif not self.fuente_verificacion:
                    pregunta.observaciones = u''
            pregunta.save()

    def __unicode__(self):
        return self.nombre


class FiltroPeriodoManager(models.Manager):
    """
    Query Set Manager para filtrar Contestaciones de Evaluaciones 
    segun su Periodo de Evaluacion incluyendo o excluyendo aquellas
    que se han realizado en periodos extendidos
    """
    def set_periodo_evaluacion(self, periodoEvaluacion):
        self.periodoEvaluacion = periodoEvaluacion

    def get_query_set(self):
        # No se ha fijado el Periodo de Evaluacion o se debe contabilizar evaluaciones extra
	if 'periodoEvaluacion' not in self.__dict__.keys() or self.periodoEvaluacion.contabilizar_extras:
	    return super(FiltroPeriodoManager, self).get_query_set()
        # No se debe contabilizar las evaluciones extra 
       	elif not self.periodoEvaluacion.contabilizar_extras:
            # return super(FiltroPeriodoManager, self).get_query_set().filter(
            #     evaluacion__fechaFin__lte=self.periodoEvaluacion.fin.date())
            #     evaluacion__horaFin__lte=self.periodoEvaluacion.fin.time())
            return super(FiltroPeriodoManager, self).get_query_set().extra(
                tables=['app_contestacion', 'app_evaluacion'],
                where=["""("fechaFin" || ' ' || "horaFin")::timestamp <= %s"""],
                params=[self.periodoEvaluacion.fin])       


class Contestacion(models.Model):
    pregunta = models.IntegerField()
    respuesta = models.TextField()
    # Adicionales a la respuesta propiamente establecida
    observaciones = models.TextField(null=True, blank=True)
    evaluacion = models.ForeignKey('Evaluacion', related_name='contestaciones')
    # Manejador de acuerdo al Periodo de Evaluacion
    objects = FiltroPeriodoManager()

    def get_pregunta(self):
        """ Devuelve el objeto 'pregunta' a partir del atributo id_pregunta """
        return Pregunta.objects.get(id=self.pregunta)

    class Meta:
        ordering = ['pregunta']
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
    # Evaluaciones de ESTUDIANTES, contiene implicitamente el docente evaluado
    estudianteAsignaturaDocente = models.ForeignKey('EstudianteAsignaturaDocente', related_name='evaluaciones', null=True, default=None)
    # Evaluaciones de DOCENTES. Pueden ser evaluaciones y autoevaluaciones 
    docentePeriodoAcademico = models.ForeignKey('DocentePeriodoAcademico', related_name='evaluaciones', null=True)
    # Evaluaciones de PARES ACADEMICOS # Docente Par Academico
    parAcademico = models.ForeignKey('DocentePeriodoAcademico', related_name='evaluaciones_par_academico', null=True)
    # Evaluaciones de DIRECCIONES DE CARRERA # Docente Director
    directorCarrera = models.ForeignKey('DocentePeriodoAcademico', related_name='evaluaciones_director', null=True)
    # Evaluaciones de DIRECCIONES DE CARRERA # Nombre de la Carrera mas el Area
    ###
    # carreraDirector =  models.CharField(max_length=255, choices=carreras_areas, 
    #                                     verbose_name=u'Carrera-Area', blank=True, null=True)
    carreraDirector =  models.CharField(max_length=255, choices=None, 
                                        verbose_name=u'Carrera-Area', blank=True, null=True)
    def evaluador(self):
        # Evaluacion del Estudiante a sus docentes
        if self.estudianteAsignaturaDocente:
            evaluador = self.estudianteAsignaturaDocente.estudiante
        # Evaluacion del Director de Carrera
        elif self.directorCarrera and self.docentePeriodoAcademico:
            evaluador = self.directorCarrera
        # Evaluacion del Par Academico de la Carrera
        elif self.parAcademico and self.docentePeriodoAcademico:
            evaluador = self.parAcademico
        # Autoevaluacion del docente
        elif self.docentePeriodoAcademico:
            evaluador = self.docentePeriodoAcademico
        return evaluador

    def evaluado(self):
        # Evaluacion del Estudiante a sus docentes
        if self.estudianteAsignaturaDocente:
            evaluado = self.estudianteAsignaturaDocente.asignaturaDocente.docente
        # Evaluacion del Director de la Carrera al docente
        elif self.directorCarrera and self.docentePeriodoAcademico:
            evaluado = self.docentePeriodoAcademico
        # Evaluacion del Par Academico de la Carrera al docente
        elif self.parAcademico and self.docentePeriodoAcademico:
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
    # Nombre corto para identificacion de objeto
    nombre = models.CharField(max_length='150', default=u'Sección de Cuestionario Sin Nombre')
    titulo = models.CharField(max_length='200')
    descripcion  = models.TextField(blank=True, null=True)
    orden = models.IntegerField()
    codigo = models.CharField(max_length='20', null=True, blank=True)
    ponderacion = models.FloatField(null=True, blank=True)
    # Una subseccion esta relacionada con otra Seccion en vez de un Cuestionario
    superseccion = models.ForeignKey('self', null=True, blank=True, db_column='superseccion_id',
                                     related_name='subsecciones', verbose_name=u'Sección Padre')
    # Una seccion normalmente esta relacionada con un Cuestionario
    cuestionario = models.ForeignKey(Cuestionario, related_name='secciones', null=True, blank=True)

    def get_cuestionario(self):
        """ Metodo recursivo hasta llegar a la seccion padre que tiene Cuestionario """
        if self.superseccion:
            return self.superseccion.get_cuestionario()
        elif self.cuestionario:
            return self.cuestionario
            
    def get_preguntas(self):
        """ Metodo recursivo hasta llegar a las secciones que no tiene subsecciones  """
        preguntas = []
        if self.subsecciones.count() > 0:
            for sub in self.subsecciones.all():
                preguntas.extend(sub.get_preguntas())
        preguntas.extend(self.preguntas.all())
        return preguntas

    def clonar(self):
        """
        Duplica recursivamene todo el conetenido de una Seccion incluyendo 
        subsecciones y preguntas
        """
        # Clonacion de los datos simples de la Seccion
        nuevaSeccion = Seccion()
        nuevaSeccion.nombre = u'(Seccion Clonada ) ' + self.nombre
        nuevaSeccion.titulo = self.titulo
        nuevaSeccion.descripcion = self.descripcion
        nuevaSeccion.orden = self.orden
        nuevaSeccion.codigo = self.codigo
        nuevaSeccion.ponderacion = self.ponderacion
        nuevaSeccion.save()
        # Clonacion de Preguntas con Items
        for pregunta in self.preguntas.all():
            nuevaPregunta = Pregunta()
            nuevaPregunta.codigo = pregunta.codigo
            nuevaPregunta.texto = pregunta.texto
            nuevaPregunta.descripcion = pregunta.descripcion
            nuevaPregunta.observaciones = pregunta.observaciones
            nuevaPregunta.orden = pregunta.orden
            nuevaPregunta.codigo = pregunta.codigo
            nuevaPregunta.tipo = pregunta.tipo
            nuevaPregunta.seccion = nuevaSeccion
            nuevaPregunta.save()
            for item in pregunta.items.all():
                nuevoItem = ItemPregunta()
                nuevoItem.texto = item.texto
                nuevoItem.descripcion = item.descripcion
                nuevoItem.orden = item.orden
                nuevoItem.pregunta = nuevaPregunta
                nuevoItem.save()
        for sub in self.subsecciones.all():
            # Invocacion recursiva del metodo
            nuevaSubseccion = sub.clonar()
            nuevaSubseccion.superseccion = nuevaSeccion
            nuevaSubseccion.save()
        return nuevaSeccion

    def preguntas_ordenadas(self):
        return self.pregunta_set.order_by('orden')

    def __unicode__(self):
        if self.cuestionario:
            return u'Sección  {0} '.format(self.nombre)
        elif self.superseccion:
            return u'Subsección {0} '.format(self.nombre)
        else:
            return u'ERROR Seccion %s' % self.id
        

    class Meta:
        ordering = ['orden']
        verbose_name = u'sección'
        verbose_name_plural = 'secciones'
        
class Pregunta(models.Model):
    codigo = models.CharField(max_length='20', null=True, blank=True)
    texto = models.TextField()
    descripcion = models.TextField(null=True, blank=True)
    # Observaciones adicionales a la contestacion o respuesta 
    # Se almacena solo un titulo o tema de las observaciones
    observaciones = models.CharField(max_length='70', null=True, blank=True)
    orden = models.IntegerField()
    tipo = models.ForeignKey(TipoPregunta)
    seccion = models.ForeignKey(Seccion, related_name='preguntas')

    def get_codigo(self):
        """ Devuelve el codigo de la seccion mas el de la pregunta """
        codigo_seccion = self.seccion.codigo or str(self.seccion.orden)
        codigo_pregunta = self.codigo or str(self.orden)
        return '{0}.{1}'.format(codigo_seccion, codigo_pregunta)

    def __unicode__(self):
        html = lxml.html.document_fromstring(self.texto)
        texto = u'{0}'.format(html.text_content())
        return texto

    class Meta:
        ordering = ['seccion__orden', 'orden']


class ItemPregunta(models.Model):
    # Valor para la contestación de la pregunta
    texto = models.CharField(max_length='50')
    # Notas adicionales aclaratorias para el Item de pregunta
    descripcion = models.CharField(max_length='70', null=True, blank=True)
    pregunta = models.ForeignKey(Pregunta, related_name='items')
    orden = models.IntegerField()

    def __unicode__(self):
        return self.texto

    class Meta:
        ordering = ['-orden']


class AreaSGA(models.Model):
    siglas = models.CharField(max_length='10')
    nombre = models.CharField(max_length='256') 

    def __unicode__(self):
        return self.siglas

    class Meta:
        ordering=['nombre']

 
class PeriodoEvaluacion(models.Model):
    nombre = models.CharField(max_length='100')
    titulo = models.CharField(max_length='300')
    descripcion = models.TextField(null=True)
    observaciones = models.TextField(null=True, blank=True)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    # Si se incluyen en resultados las evaluaciones extras
    contabilizar_extras = models.BooleanField(
        verbose_name="CONTABILIZAR EXTRAS", 
        help_text='Permite Contabilizar Evaluaciones Adicionales en Resultados', 
        default=False)
    periodoAcademico = models.ForeignKey('PeriodoAcademico', related_name='periodosEvaluacion', verbose_name="Periodo Académico")
    areasSGA = models.ManyToManyField(AreaSGA, related_name='periodosEvaluacion', verbose_name=u'Areas Académicas SGA')
    
    class Meta:
        ordering = ['inicio', 'fin']
        verbose_name = u'Periodo Evaluación'
        verbose_name_plural = u'Periodos de Evaluación'
        
    def noIniciado(self):
        ahora = datetime.today()
        return ahora < self.inicio
    
    def vigente(self):
        ahora = datetime.today()
        vigente = self.inicio <= ahora <= self.fin
        # Se busca si existen extensiones del Periodo de Evaluacion
        # que esten vigentes.
        if not vigente:
            extensiones_vigentes = filter(lambda e: e.vigente(), self.extensiones.all())
            vigente = len(extensiones_vigentes) > 0
        return vigente

    def finalizado(self):
        ahora = datetime.today()
        return ahora > self.fin

    def verificar_estudiante(self, cedula):
        """
        Analiza si el Estudiante a realizado todas las evaluaciones
        que le corresponden en este Periodo de Evaluación.
        """
        try:
            EstudiantePeriodoAcademico.objects.get(usuario__cedula=cedula, periodoAcademico=self.periodoAcademico)
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

    def contabilizar_evaluaciones_estudiantes(self, area, carrera, semestre=None, paralelo=None):
        """ Contabiliza evaluaciones de Estudiantes """
        consulta = EstudianteAsignaturaDocente.objects.filter(
            estudiante__periodoAcademico = self.periodoAcademico,
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

    def contabilizar_evaluadores(self):
        """ 
        Cuenta los estudiantes, pares academicos y directores que HAYAN EVALUADO
        a por lo menos un docente. No se controla haber evaluado a todos los docentes.
        """
        estudiantes = Evaluacion.objects.filter(
            cuestionario__periodoEvaluacion=self).values_list(
            'estudianteAsignaturaDocente__estudiante').distinct().count()
        docentes = Evaluacion.objects.filter(
            cuestionario__periodoEvaluacion=self, docentePeriodoAcademico__isnull=False, 
            directorCarrera__isnull=True, parAcademico__isnull=True).count()
        pares = Evaluacion.objects.filter(
            cuestionario__periodoEvaluacion=self, parAcademico__isnull=False).values(
            'parAcademico').distinct().count()
        directores = Evaluacion.objects.filter(
            cuestionario__periodoEvaluacion=self, directorCarrera__isnull=False).values(
            'directorCarrera').distinct().count()            
        return dict(estudiantes=estudiantes, docentes=docentes, pares=pares, directores=directores)

    def contabilizar_evaluados(self):
        """ 
        Cuenta los estudiantes, pares academicos y directores que HAN SIDO EVALUADOS
        """
        porEstudiantes = Evaluacion.objects.filter(
            cuestionario__periodoEvaluacion=self, estudianteAsignaturaDocente__isnull=False).values_list(
            'estudianteAsignaturaDocente__asignaturaDocente__docente').distinct().count()
        porDocentes = Evaluacion.objects.filter(
            cuestionario__periodoEvaluacion=self, docentePeriodoAcademico__isnull=False, 
            directorCarrera__isnull=True, parAcademico__isnull=True).count()
        porPares = Evaluacion.objects.filter(
            cuestionario__periodoEvaluacion=self, parAcademico__isnull=False).values(
            'docentePeriodoAcademico').distinct().count()
        porDirectores = Evaluacion.objects.filter(
            cuestionario__periodoEvaluacion=self, directorCarrera__isnull=False).values(
            'docentePeriodoAcademico').distinct().count()            
        return dict(porEstudiantes=porEstudiantes, porDocentes=porDocentes, porPares=porPares, porDirectores=porDirectores)
            
    def __unicode__(self):
        return self.nombre


class ExtensionPeriodoEvaluacion(models.Model):
    secuencia = models.IntegerField()
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    # Justificacion de la Prolongacion
    observaciones = models.TextField() 
    periodoEvaluacion = models.ForeignKey('PeriodoEvaluacion', related_name='extensiones', verbose_name="Extensión Periodo de Evaluación")

    def vigente(self):
        ahora = datetime.today()
        return self.inicio <=  ahora <= self.fin 
    
    class Meta:
        ordering = ['inicio', 'fin']
        verbose_name = u'Extensión Periodo de Evaluación'
        verbose_name_plural = u'Extensiones de Periodo de Evaluación'


# TODO: Modelar de mejor manera la funcionalidad
tipos_tabulacion = (
    (u'ESE2012', u'Tabulación Satisfacción Estudiantil 2012'),
    (u'EAAD2012', u'Tabulación Actividades Adicionales Docencia 2011-2012'),
    (u'EDD2013', u'Tabulación Evaluación del Desempeño Docente 2012-2013')
)

class Tabulacion(models.Model):
    """
    Superclase que permite procesar la informacion generada por un
    conjunto de encuestas pertenecientes a un Periodo de Evaluación.
    """
    descripcion = models.CharField(max_length='250')
    tipo = models.CharField( max_length='20', choices=tipos_tabulacion)
    periodoEvaluacion = models.OneToOneField('PeriodoEvaluacion', related_name='tabulacion', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Tabulaciones" 
        
    def __unicode__(self):
        return self.descripcion


class TabulacionEvaluacion2013:
    tipo = u'EDA2013' #TODO: Estandarizar con EDD2013
    descripcion = u'Evaluación del Desempeño Docente 2012-2013'

    def __init__(self, periodoEvaluacion=None):
        self.periodoEvaluacion = periodoEvaluacion
        self.calculos = (
            # codigo, descripcion, metodo, titulo 
            ('a', u'Resultados de la Evaluación del Desempeño Académico POR DOCENTE',
             self.por_docente, u'Evaluación del Desempeño Académico por Docente'),
            ('b', u'Resultados de la Evaluación del Desempeño Académico POR CARRERA',
            self.por_carrera, u'Evaluación del Desempeño Académico por Carrera'),
            ('c', u'Resultados de la Evaluación del Desempeño Académico POR AREA',
            self.por_area, u'Evaluación del Desempeño Académico por Area'),
            ('e', u'Listado de Docentes y Calificaciones',
            self.listado_calificaciones, u'Listado de Docentes y Calificaciones'),
            )

    def por_docente(self, siglas_area, nombre_carrera, id_docente, componente=None, formato=None):
        # Se pasa un tupla no un solo id
        return self._calcular(siglas_area, nombre_carrera, (id_docente,), componente, formato)

    def por_carrera(self, siglas_area, nombre_carrera, componente, formato=None):
        # Obtenemos los id de los Docentes que dictan Asignaturas en la carrera seleccionada
        aux_ids = AsignaturaDocente.objects.filter(
            docente__periodoAcademico=self.periodoEvaluacion.periodoAcademico,
            asignatura__carrera=nombre_carrera,
            asignatura__area=siglas_area
            ).values_list('docente__id', flat=True).distinct()
        # Se agregan tambien los docentes que no tengan Asignaturas pero que pertenezcan a la Carrera
        ids_docentes = DocentePeriodoAcademico.objects.filter(
            Q(periodoAcademico=self.periodoEvaluacion.periodoAcademico) and
            (Q(id__in=aux_ids) or Q(carrera=nombre_carrera))
            ).order_by('usuario__last_name', 'usuario__first_name').values_list(
            'id', flat=True
            )
        return self._calcular(siglas_area, nombre_carrera, ids_docentes, componente, formato)

    def por_area(self, siglas_area, componente=None, formato=None):
        # Obtenemos los id de los Docentes que dictan Asignaturas en el area seleccionada
        aux_ids = AsignaturaDocente.objects.filter(
            docente__periodoAcademico=self.periodoEvaluacion.periodoAcademico,
            asignatura__area=siglas_area
            ).values_list('docente__id', flat=True).distinct()
        # Se agregan tambien los docentes que no tengan Asignaturas pero que pertenezcan a la Carrera
        ids_docentes = DocentePeriodoAcademico.objects.filter(
            Q(periodoAcademico=self.periodoEvaluacion.periodoAcademico) and
            ( Q(id__in=aux_ids) ) # TODO: No hay el area en el atributo Carrera de DocentePeriodoAcademico
            ).order_by('usuario__last_name', 'usuario__first_name').values_list(
            'id', flat=True
            )
        return self._calcular(siglas_area, None , ids_docentes, componente, formato)


    def listado_calificaciones(self, siglas_area, nombre_carrera, formato=None):
        # Obtenemos los id de los Docentes que dictan Asignaturas en la carrera seleccionada
        aux_ids = AsignaturaDocente.objects.filter(
            docente__periodoAcademico=self.periodoEvaluacion.periodoAcademico,
            asignatura__carrera=nombre_carrera,
            asignatura__area=siglas_area
            ).values_list('docente__id', flat=True).distinct()
        # Se agregan tambien los docentes que no tengan Asignaturas pero que pertenezcan a la Carrera
        docentes = DocentePeriodoAcademico.objects.filter(
            Q(periodoAcademico=self.periodoEvaluacion.periodoAcademico) and
            (Q(id__in=aux_ids) or Q(carrera=nombre_carrera))
            ).order_by('usuario__last_name', 'usuario__first_name').all()
        listado_calificaciones = list()
        for docente in docentes:
            resultados = self.por_docente(siglas_area, nombre_carrera, docente.id, None)
            total = resultados.get('total',0)
            promedios = resultados.get('promedios', {})
            logg.info('{0} resultados: {1} - {2}'.format(docente, promedios, total))
            fila = (docente.usuario.cedula, docente.usuario.last_name, docente.usuario.first_name,  
                    str(round(promedios.get('paracademico', 0), 2)), str(round(promedios.get('directivo', 0), 2)),
                    str(round(promedios.get('docente', 0), 2)), str(round(promedios.get('estudiante', 0), 2)), 
                    )
            listado_calificaciones.append(fila)
        return dict(listado_calificaciones=listado_calificaciones)


    def _calcular(self, siglas_area, nombre_carrera, ids_docentes, componente=None, formato=None):
        """ 
        Metodo generico para calcular los resultados de acuerdo a los diferentes criterios
        Si se trata del reporte de sugerencias se salta al metodo respectivo
        # TODO: Actualmente se contabiliza los resultados en todas la carreras en las que
        	el docente dicta clases, se podria limitar realmente a la carrera especifica.
        """ 
        # Para contabilizar de acuerdo a la naturaleza del Periodo de Evaluacion
        # Proceso verificado en FiltroPeriodoManager
        Contestacion.objects.set_periodo_evaluacion(self.periodoEvaluacion)

        if formato == 'CSV':
            return self._contabilizar_respuestas(siglas_area, nombre_carrera, ids_docentes, componente)

        if componente == 'sugerencias':
            return self.extraer_sugerencias(siglas_area, nombre_carrera, ids_docentes)

        resultados_indicadores = {}
        pesos = {}
        if siglas_area == 'ACE':
            tipos = ('EstudianteIdiomas', 'DocenteIdiomas', 'ParAcademicoIdiomas', 'DirectivoIdiomas')
        else:
            tipos = ('Estudiante', 'Docente', 'ParAcademico', 'Directivo')
        if not componente:
            seccion_componente = None
        else:
            # Se pasa de string a objeto seccion para sacar datos en la plantilla
            seccion_componente = Seccion.objects.filter(cuestionario__periodoEvaluacion=self.periodoEvaluacion, codigo=componente)[0]

        # -----------------------------------------------------------------------------------
        # Promedios de cada indicador
        # -----------------------------------------------------------------------------------
        for tipo in tipos:
            cuestionario = Cuestionario.objects.get(periodoEvaluacion=self.periodoEvaluacion, informante__tipo=tipo)
            # En caso de tratarse del insituto de idiomas se generaliza el informante
            # Anecdota: Un error "simplon" que me llevo mas de dos dias encontrarlo
            informante = tipo.lower().replace('idiomas','')
            # Para los calculos finales
            pesos.update({informante : cuestionario.peso}) 
            # Solo ids 
            if not componente:
                preguntas = [p.id for p in cuestionario.get_preguntas() if p.tipo==TipoPregunta.objects.get(tipo='SeleccionUnica')]
            else:
                preguntas = [p.id for p in cuestionario.get_preguntas() if 
                             p.tipo==TipoPregunta.objects.get(tipo='SeleccionUnica') and
                             p.seccion.superseccion.codigo==componente ]
            # Solo IDs de contestaciones
            contestaciones = None
            if informante == 'estudiante':
                contestaciones = Contestacion.objects.filter(
                    evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id__in=ids_docentes, 
                    pregunta__in=preguntas).values_list('id', flat=True)
            elif informante == 'docente':
                contestaciones = Contestacion.objects.filter(
                    evaluacion__parAcademico__isnull=True, evaluacion__directorCarrera__isnull=True,
                    evaluacion__docentePeriodoAcademico__id__in=ids_docentes, pregunta__in=preguntas
                    ).values_list('id', flat=True)
            elif informante == 'paracademico':
                contestaciones = Contestacion.objects.filter(
                    evaluacion__parAcademico__isnull=False, evaluacion__directorCarrera__isnull=True,
                    evaluacion__docentePeriodoAcademico__id__in=ids_docentes, pregunta__in=preguntas
                    ).values_list('id', flat=True)
            elif informante == 'directivo':
                contestaciones = Contestacion.objects.filter(
                    evaluacion__directorCarrera__isnull=False, evaluacion__parAcademico__isnull=True,
                    evaluacion__docentePeriodoAcademico__id__in=ids_docentes, pregunta__in=preguntas
                    ).values_list('id', flat=True)
            if contestaciones:
                # Otencion de promedios por pregunta
                cursor = connection.cursor()
                cursor.execute("""SELECT pregunta, AVG(respuesta::INT) FROM app_contestacion 
                       WHERE id IN %s GROUP BY pregunta""", [tuple(contestaciones)])
                result = cursor.fetchall()
                cursor.close()
            else:
                # El informante no ha contestado el cuestionario correspondiente
                logg.warning('No hay evaluaciones del informante {0} para los docentes {1}'.format(tipo,ids_docentes))
                print "No hay contestaciones de " + tipo + ' para ' + str(ids_docentes)
                result = [(id, 0.0) for id in preguntas]

            # Diccionario a partir de lista compresa de tuplas conformadas por ids de pregunta con sus promedio
            promedios_preguntas = dict([(Pregunta.objects.get(id=id_pregunta), promedio) for id_pregunta, promedio in result])
            indicadores = {}
            # Sumatorias por pregunta
            for pregunta, promedio in promedios_preguntas.items():
                suma = indicadores.get(pregunta.seccion,0) + promedio
                indicadores.update({pregunta.seccion: suma})
            # Promedio por seccion (indicador)
            for seccion, suma in indicadores.items():
                promedio = float(suma) / float(seccion.preguntas.count())
                indicadores.update({seccion : promedio})
            # Porcentaje por seccion (indicador)
            ESCALA_MAXIMA = 4
            for seccion, promedio in indicadores.items():
                porcentaje = round((100 * promedio) / ESCALA_MAXIMA)
                indicadores.update({seccion : int(porcentaje)})
            # Genera diccionario de diccionarios
            for seccion, porcentaje in indicadores.items():
                """ 
                Los 'Objetos' Seccion son diferentes pues pertenecen a Cuestionarios diferentes
                por tal motivo se usa el codigo como clave del diccionario para sumarizar los
                porcentajes de las secciones con el mismo codigo en todos los Cuestionarios. 
                """
                indicador = resultados_indicadores.get(seccion.codigo, None)
                if not indicador:
                    # Se guarda el atributo ponderacion solo la primera vez para luego calcular
                    # Puesto que todas las secciones tienes los mismos datos 
                    indicador = {'informantes' : {}, 'ponderacion_seccion' : seccion.ponderacion}
                # Se inserta ademas el objeto Seccion el indicador para disponer de informacion extra en el template
                indicador.update({'objeto_seccion' : seccion})
                indicador['informantes'].update({ informante : porcentaje })
                resultados_indicadores.update({seccion.codigo : indicador})
                
        # -----------------------------------------------------------------------------------
        # Calculos totales en todos los indicadores de acuerdo al peso de los informantes
        # ------------------------------------------------------------------------------------
        aux_estudiante = []
        aux_docente = []
        aux_paracademico = []
        aux_directivo = []
        promedio_primaria = 0
        promedio_ponderada = 0
        # Solo el codigo de la seccion
        for seccion, resultado in resultados_indicadores.items():
            valores = resultado['informantes']
            informantes = valores.keys()
            informantes.sort()
            primaria = 0.0
            # UN solo informante Comision Academica
            if informantes == ['directivo', 'paracademico']:
                # (pdir * vdir) + (ppa * vpa)) / (pdir + ppa)
                primaria = pesos['directivo'] * valores['directivo'] +  pesos['paracademico'] * valores['paracademico']
                primaria = primaria / (pesos['directivo'] + pesos['paracademico'])
            # DOS informantes
            elif informantes == ['directivo', 'docente', 'paracademico']:
                # ((mpne + pdir * vdir) + (mpne + ppa * vpa) + (??? + pd * cd))
                mitad = pesos['estudiante'] / 2
                primaria =  (mitad / 2 + pesos['directivo']) * valores['directivo']
                primaria += (mitad / 2 + pesos['paracademico']) * valores['paracademico']
                primaria += (mitad + pesos['docente']) * valores['docente']
            elif informantes == ['directivo', 'estudiante', 'paracademico']:
                # ((mpne + pdir * vdir) + (mpne + ppa * vpa) + (??? + pd * cd))
                mitad = pesos['docente'] / 2
                primaria =  (mitad / 2 + pesos['directivo']) * valores['directivo']
                primaria += (mitad / 2 + pesos['paracademico']) * valores['paracademico']
                primaria += (mitad + pesos['estudiante']) * valores['estudiante']
            elif informantes == ['docente', 'estudiante']:
                # (mpni + pe * ve) + (mpni + pd * vd)
                mitad = (pesos['directivo'] + pesos['paracademico']) / 2
                primaria = (mitad + pesos['estudiante']) * valores['estudiante']
                primaria += (mitad + pesos['docente']) * valores['docente']
            # TRES informantes
            elif informantes == ['directivo', 'docente', 'estudiante', 'paracademico']:
                # (pe + ve) + ((pdir * vdir) + (ppa * vpa)) + (pd * vd))
                primaria = pesos['estudiante'] * valores['estudiante']
                primaria += pesos['docente'] * valores['docente']
                primaria += pesos['paracademico'] * valores['paracademico']
                primaria += pesos['directivo'] * valores['directivo']
            
            primaria = round(primaria)
            resultado.update({'primaria' : primaria})
            promedio_primaria += primaria
            ponderada = primaria * (resultado['ponderacion_seccion'] or 0.0) / 100
            promedio_ponderada += ponderada
            resultado.update({'ponderada' : ponderada})
            resultado.update({'cualitativa' : self._cualificar_valor(primaria)})
            aux_estudiante.append(valores.get('estudiante', -1))
            aux_directivo.append(valores.get('directivo', -1))
            aux_docente.append(valores.get('docente', -1))
            aux_paracademico.append(valores.get('paracademico', -1))

        # En caso de que no se tata de un componente en particular
        if  not componente:
            # Se envia a calcular los promedios por cada componente 
            promedios_componentes = self._calcular_componentes(resultados_indicadores)
        else:
            promedios_componentes = None

        aux_estudiante = [e for e in aux_estudiante if e >= 0]
        aux_docente = [e for e in aux_docente if e >= 0]
        aux_paracademico = [e for e in aux_paracademico if e >= 0]
        aux_directivo  = [e for e in aux_directivo if e >= 0]

        prom_estudiante = (sum(aux_estudiante) / float(len(aux_estudiante))) if aux_estudiante else 0
        prom_docente = (sum(aux_docente) / float(len(aux_docente))) if aux_docente else 0
        prom_paracademico = (sum(aux_paracademico) / float(len(aux_paracademico))) if aux_paracademico else 0
        prom_directivo = (sum(aux_directivo) / float(len(aux_directivo))) if aux_directivo else 0

        promedio_primaria = (promedio_primaria / len(resultados_indicadores)) if resultados_indicadores else 0
        # Solo se suma la ponderacion hasta el final
        promedios= {'estudiante' : prom_estudiante,
                    'docente' : prom_docente,
                    'paracademico' : prom_paracademico,
                    'directivo' : prom_directivo,
                    'primaria' : round(promedio_primaria,2),
                    'ponderada' : promedio_ponderada,
                    'cualitativa' : self._cualificar_valor(promedio_primaria)
                    }
        # Se ordena el diccionario por la clave (codigo del indicador)
        resultados_indicadores = OrderedDict(sorted(resultados_indicadores.items(), key=lambda i: i[0]))
        logg.info('Calculado docente: {0} promedios: {1} total: {2}'.format(ids_docentes, promedios, promedio_ponderada))
        return dict(resultados_indicadores=resultados_indicadores, promedios_componentes=promedios_componentes,
                    promedios=promedios, total=promedio_ponderada, seccion_componente=seccion_componente)


    def _calcular_componentes(self, resultados_indicadores):
        promedios_componentes = {'CPF' : {'estudiante':[], 'docente':[], 'paracademico':[], 'directivo':[],
                                          'primaria' : [], 'ponderada':[], 'cualitativa':''},
                                 'CPG' : {'estudiante':[], 'docente':[], 'paracademico':[], 'directivo':[],
                                          'primaria' : [], 'ponderada':[], 'cualitativa':''}, 
                                 'PV' : {'estudiante':[], 'docente':[], 'paracademico':[], 'directivo':[],
                                          'primaria' : [], 'ponderada':[], 'cualitativa':''},
                                 }
        for codigo_seccion, resultado in resultados_indicadores.items():
            componente = resultado['objeto_seccion'].superseccion.codigo
            promedios_componentes[componente]['estudiante'].append(resultado['informantes'].get('estudiante',-1))
            promedios_componentes[componente]['docente'].append(resultado['informantes'].get('docente',-1))
            promedios_componentes[componente]['paracademico'].append(resultado['informantes'].get('paracademico', -1))
            promedios_componentes[componente]['directivo'].append(resultado['informantes'].get('directivo',-1))
            promedios_componentes[componente]['primaria'].append(resultado.get('primaria', -1))
            promedios_componentes[componente]['ponderada'].append(resultado.get('ponderada', -1))
        for componente in ('CPF', 'CPG', 'PV'):
            for tipo_promedio in ('estudiante', 'docente', 'paracademico', 'directivo', 'primaria', 'ponderada'):
                lista = [n for n in promedios_componentes[componente][tipo_promedio] if n >= 0] 
                if tipo_promedio == 'ponderada':
                    promedio = sum(lista)
                else:
                    promedio = sum(lista)/len(lista)
                # En este momento se cambia el contenido tipo lista por un numero 
                promedios_componentes[componente][tipo_promedio] = promedio
            promedios_componentes[componente]['cualitativa'] = self._cualificar_valor(
                promedios_componentes[componente]['primaria'])
        return promedios_componentes

    def _cualificar_valor(self, valor):
        """ Se cualifica con valores enteros """
        rangos = {'IS':range(0,41), 'PS':range(41,61), 'S':range(61,81), 'D':range(81,101)}
        for k,v in rangos.items():
            if v[0] <= round(valor) <= v[-1]:
                return k
        return '-'

    def extraer_sugerencias(self, area, carrera, ids_docentes):
        sugerencias = {}
        if area == 'ACE':
            tipos = ('EstudianteIdiomas', 'DocenteIdiomas', 'ParAcademicoIdiomas', 'DirectivoIdiomas')
        else:
            tipos = ('Estudiante', 'Docente', 'ParAcademico', 'Directivo')
        for id_docente in ids_docentes:
            resultado = {}
            # Solo nombres del docente
            nombre_docente = DocentePeriodoAcademico.objects.get(id=id_docente).__unicode__()
            for tipo in tipos:
                informante = tipo.lower().replace('idiomas', '')
                # Codigo es PV, CPG o CPF
                preguntas_ensayo = Pregunta.objects.filter(
                    seccion__cuestionario__periodoEvaluacion=self.periodoEvaluacion,
                    seccion__cuestionario__informante__tipo=tipo, tipo__tipo='Ensayo'
                    ).values('id', 'seccion__codigo')
                resultado[tipo] = []
                # Contendra 3 items, uno por cada componente
                aux_contestaciones = {}
                if informante == 'estudiante':
                    for pregunta in preguntas_ensayo:
                        contestaciones = Contestacion.objects.filter(
                            evaluacion__cuestionario__informante__tipo__icontains='estudiante',
                            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente, 
                            pregunta=pregunta['id']).values_list('respuesta', flat=True)
                        aux_contestaciones[pregunta['seccion__codigo']] = contestaciones
                elif informante == 'docente':
                    for pregunta in preguntas_ensayo:
                        contestaciones = Contestacion.objects.filter(
                            evaluacion__parAcademico__isnull=True, evaluacion__directorCarrera__isnull=True,
                            evaluacion__docentePeriodoAcademico__id=id_docente, pregunta=pregunta['id']
                            ).values_list('respuesta', flat=True)
                        aux_contestaciones[pregunta['seccion__codigo']] = contestaciones
                elif informante == 'paracademico':
                    for pregunta in preguntas_ensayo:
                        contestaciones = Contestacion.objects.filter(
                            evaluacion__parAcademico__isnull=False, evaluacion__directorCarrera__isnull=True,
                            evaluacion__docentePeriodoAcademico__id=id_docente, pregunta=pregunta['id']
                            ).values_list('respuesta', flat=True)
                        aux_contestaciones[pregunta['seccion__codigo']] = contestaciones
                elif informante == 'directivo':
                    for pregunta in preguntas_ensayo:
                        contestaciones = Contestacion.objects.filter(
                            evaluacion__directorCarrera__isnull=False, evaluacion__parAcademico__isnull=True,
                            evaluacion__docentePeriodoAcademico__id=id_docente, pregunta=pregunta['id']
                            ).values_list('respuesta', flat=True)
                        aux_contestaciones[pregunta['seccion__codigo']] = contestaciones
                # Se supone que en los tres componentes hay la misma cantidad de respuestas CPF, CPG y PV
                num_contestaciones = len(aux_contestaciones.values()[0])
                for i in range(num_contestaciones):
                    aux_dict = {'CPF' : aux_contestaciones['CPF'][i], 
                                'CPG' : aux_contestaciones['CPG'][i], 
                                'PV' : aux_contestaciones['PV'][i]}
                    # Un resultado de un docente
                    resultado[tipo].append(aux_dict)
            sugerencias[nombre_docente] = resultado
        return dict(sugerencias=sugerencias)

    def _contabilizar_respuestas(self, siglas_area, nombre_carrera, ids_docentes, componente):
        """ 
        Metodo  para contar las respuestas de los informantes generado en CSV
        """ 
        if componente == 'sugerencias':
            return None
        if siglas_area == 'ACE':
            tipos = ('EstudianteIdiomas', 'DocenteIdiomas', 'ParAcademicoIdiomas', 'DirectivoIdiomas')
        else:
            tipos = ('Estudiante', 'Docente', 'ParAcademico', 'Directivo')
        if not componente:
            seccion_componente = None
        else:
            # Se pasa de string a objeto seccion para sacar datos en la plantilla
            seccion_componente = Seccion.objects.filter(cuestionario__periodoEvaluacion=self.periodoEvaluacion, codigo=componente)[0]
        resultados = []
        for tipo in tipos:
            cuestionario = Cuestionario.objects.get(periodoEvaluacion=self.periodoEvaluacion, 
                                                    informante__tipo=tipo)
            # En caso de tratarse del insituto de idiomas se generaliza el informante
            informante = tipo.lower().replace('idiomas','')
            # Solo ids de preguntas
            if not componente:
                preguntas = [p.id for p in cuestionario.get_preguntas() 
                             if p.tipo==TipoPregunta.objects.get(tipo='SeleccionUnica')]
            else:
                preguntas = [p.id for p in cuestionario.get_preguntas() if 
                             p.tipo==TipoPregunta.objects.get(tipo='SeleccionUnica') and
                             p.seccion.superseccion.codigo==componente]
            # Se inicia el QuerySet contestaciones
            if informante == 'estudiante':
                contestaciones = Contestacion.objects.filter(
                    evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id__in=ids_docentes, 
                    pregunta__in=preguntas).values_list(
                    'evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente', 
                    'evaluacion__cuestionario__informante__tipo',
                    'pregunta', 
                    'respuesta'
                    )
            elif informante == 'docente':
                contestaciones = Contestacion.objects.filter(
                    evaluacion__parAcademico__isnull=True, evaluacion__directorCarrera__isnull=True,
                    evaluacion__docentePeriodoAcademico__id__in=ids_docentes, pregunta__in=preguntas
                    ).values_list(
                    'evaluacion__docentePeriodoAcademico',
                    'evaluacion__cuestionario__informante__tipo',
                    'pregunta', 
                    'respuesta'
                    )
            elif informante == 'paracademico':
                contestaciones = Contestacion.objects.filter(
                    evaluacion__parAcademico__isnull=False, evaluacion__directorCarrera__isnull=True,
                    evaluacion__docentePeriodoAcademico__id__in=ids_docentes, pregunta__in=preguntas
                    ).values_list(
                    'evaluacion__docentePeriodoAcademico',
                    'evaluacion__cuestionario__informante__tipo',
                    'pregunta', 
                    'respuesta'
                    )
            elif informante == 'directivo':
                contestaciones = Contestacion.objects.filter(
                    evaluacion__directorCarrera__isnull=False, evaluacion__parAcademico__isnull=True,
                    evaluacion__docentePeriodoAcademico__id__in=ids_docentes, pregunta__in=preguntas
                    ).values_list(
                    'evaluacion__docentePeriodoAcademico',
                    'evaluacion__cuestionario__informante__tipo',
                    'pregunta', 
                    'respuesta'
                    )
            # Formato y orden de los datos en los QuerySet Resultantes:
            # docente_id, informante_nombre, pregunta_id, respuesta_texto, cantidad) 
            contestaciones = contestaciones.annotate(conteo=Count('respuesta')).all()
	    # En caso de generarse por Area
	    if siglas_area and not nombre_carrera:
		nombre_carrera = 'Todas'
            sublista = [[siglas_area, nombre_carrera, 
                        DocentePeriodoAcademico.objects.get(id=c[0]).usuario.last_name,
                        DocentePeriodoAcademico.objects.get(id=c[0]).usuario.first_name,
                        c[1],
                        # El atributo Pegunta.text devulve tambien el HTML de maquetacion
                        Pregunta.objects.get(id=c[2]).get_codigo(),
                        Pregunta.objects.get(id=c[2]).__unicode__(),
                        c[3],
                        str(c[4])
                        ] for c in contestaciones ]
            resultados.extend(sublista)
            # Odenar por apellido, cuestionario,pregunta
            resultados.sort(lambda r1, r2: cmp(r1[2], r2[2]) or cmp(r1[4], r2[4]) or cmp(r1[5], r2[5]))
        return dict(area=siglas_area, carrera=nombre_carrera, resultados_indicadores=resultados)


class TabulacionAdicionales2012:
    tipo = u'EAAD2012'
    descripcion = u'Evaluación Actividades Adicionales a la Docencia 2012'

    def __init__(self, periodoEvaluacion=None):
        self.periodoEvaluacion = periodoEvaluacion
        self.calculos = (
            # codigo, descripcion, metodo, titulo 
            ('a',u'Resultados de la Evaluacion de Actividades Adicionales a la Docencia POR DOCENTE',
            self.por_docente, u'Evaluación Actividades Adicionales por Docente'),
            ('b',u'Resultados de la Evaluación de Actividades Adicionales a la Docencia POR CARRERA',
             self.por_carrera, u'Evaluación Actividades Adicionales por Carrera'),
        )
        
    def por_docente(self, siglas_area, nombre_carrera, id_docente):
        """
        Resultados de la Evaluación de Actividades Adicionales a la Docencia 2012 POR DOCENTE
        """
        docente = DocentePeriodoAcademico.objects.get(id=id_docente)
        # Procesamiento de la Autoevaluacion del Docente #
        try:
            # Autoevaluacion de Actividades Adicionales del Docente
            autoevaluacion=docente.evaluaciones.get(cuestionario__periodoEvaluacion__id=2,
                                                    cuestionario__informante__tipo='Docente')
        except exceptions.MultipleObjectsReturned:
            # Existe una evaluacion duplicada
            logg.warning('Autoevaluacion duplicada docente {0} en periodo:{1}'.format(docente, 2))
            # Se toma la primera evaluacion
            autoevaluacion = docente.evaluaciones.filter(cuestionario__periodoEvaluacion__id=2,
                                                         cuestionario__informante__tipo='Docente')[0]
        except Evaluacion.DoesNotExist:
            logg.warning(u'No existe autoevaluación del docente {0} en periodo:{1}'.format(docente, 2))
            return None
        # Solo de seleccion unica
        contestaciones1 = [c for c in autoevaluacion.contestaciones.all() if Pregunta.objects.get(id=c.pregunta).tipo.id==2]
        total1 = sum([int(c.respuesta) for c in contestaciones1])
        peso = (total1 / float(len(contestaciones1))) if len(contestaciones1) > 0  else 0
        porcentaje1 = (peso * 100 / float(4))
        # Se coloca en Contestacion un objeto Pregunta en vez del id_pregunta entero
        for c in contestaciones1:
            c.pregunta = Pregunta.objects.get(id=c.pregunta)        
        # Procesamiento de la Evaluacion de la Comision Academica #
        try:
            # Evaluacion de Actividades Adicionales del Docente por parte de los Directivo
            evaluacion=docente.evaluaciones.get(cuestionario__periodoEvaluacion__id=2,
                                                    cuestionario__informante__tipo='Directivo')
        except exceptions.MultipleObjectsReturned:
            # Existe una evaluacion duplicada
            logg.warning('Evaluacion duplicada docente {0} en periodo:{1}'.format(docente, 2))
            # Se toma la primera evaluacion
            evaluacion = docente.evaluaciones.filter(cuestionario__periodoEvaluacion__id=2,
                                                         cuestionario__informante__tipo='Directivo')[0]
        except Evaluacion.DoesNotExist:
            logg.warning(u'No existe evaluación de directivos para el docente {0} en periodo:{1}'.format(docente, 2))
            return None
        # Solo de seleccion unica
        contestaciones2 = [c for c in evaluacion.contestaciones.all() if Pregunta.objects.get(id=c.pregunta).tipo.id==2]
        total2 = sum([int(c.respuesta) for c in contestaciones2])
        peso = (total2 / float(len(contestaciones2))) if len(contestaciones2) > 0 else 0
        porcentaje2 = (peso * 100 / float(4))
        # Se coloca en Contestacion un objeto Pregunta en vez del id_pregunta entero
        for c in contestaciones2:
            c.pregunta = Pregunta.objects.get(id=c.pregunta)     
        # Valor Total obtenido con  ponderacion: Docente 20%  - Comision Academica 80%
        total = (porcentaje1 * 20 / 100) + (porcentaje2 * 80 / 100) 
        contestaciones = {}
        contestaciones['secciones'] = []
        # Los dos cuestionarios tienen las mismas secciones
        # TODO: Creo que se puede mejorar el este codigo
        for s in autoevaluacion.cuestionario.secciones.all():
            seccion = {'titulo':s.titulo, 'resultados': []}
            for p in s.preguntas.all():
                l1 = [c.respuesta for c in contestaciones1 if c.pregunta.codigo == p.codigo]
                valor_docente = l1[0] if l1 else ''
                l1 = [c.observaciones for c in contestaciones1 if c.pregunta.codigo == p.codigo]
                observaciones_docente = l1[0] if l1 else ''
                l2 = [c.respuesta for c in contestaciones2 if c.pregunta.codigo == p.codigo]
                valor_comision = l2[0] if l2 else ''
                l2 = [c.observaciones for c in contestaciones2 if c.pregunta.codigo == p.codigo]
                observaciones_comision = l2[0] if l2 else ''
                porcentaje_docente = int(valor_docente)*25 if valor_docente else ''
                porcentaje_comision = int(valor_comision)*25 if valor_comision else ''
                if valor_docente or valor_comision:
                    seccion['resultados'].append({'codigo':p.codigo, 'texto':p.texto, 
                                                  'valor_comision':valor_comision, 'valor_docente':valor_docente,
                                                  'porcentaje_comision':porcentaje_comision, 'porcentaje_docente':porcentaje_docente,
                                                  'observaciones_comision':observaciones_comision, 
                                                  'observaciones_docente':observaciones_docente})
            contestaciones['secciones'].append(seccion)
        num_actividades = sum([len(s['resultados']) for s in contestaciones['secciones']])
        contestaciones['num_actividades'] = num_actividades
        return dict(contestaciones1=contestaciones1, porcentaje1=porcentaje1, 
                    contestaciones2=contestaciones2, porcentaje2=porcentaje2,
                    contestaciones=contestaciones, total=total)


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
            ('g',u'Listado de docentes de la carrera y Calificaciones',
             self.listado_calificaciones, u'Listado de Docentes y Porcentaje de Satisfacción Estudiantil'),
        )
 

    def por_docente(self, siglas_area, nombre_carrera, id_docente):
        """
        Satisfacción Estudiantil de un docente en los  módulos, cursos, unidades o talleres
        """
        if siglas_area == u'ACE':
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'EstudianteIdiomas')
        else:
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'Estudiante')        
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        # Se seleccionan solo ids para poder comparar
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)

        datos = self._contabilizar(siglas_area, nombre_carrera, indicadores, id_docente)
        conteos = datos['conteos']
        totales = datos['totales']
        porcentajes = datos['porcentajes']
        
        # conteos = self._contabilizar(siglas_area, nombre_carrera, indicadores, id_docente)['conteos']
        # totales = self._contabilizar(siglas_area, nombre_carrera, indicadores, id_docente)['totales']
        # porcentajes = self._contabilizar(siglas_area, nombre_carrera, indicadores, id_docente)['porcentajes']
            
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)
    

    # TODO: Usar carrera_id en vez de nombre_carrera?
    def por_carrera(self, siglas_area, nombre_carrera):
        # Todas las Secciones de todos los cuestionarios que pertenecen al periodo de evaluación establecido
        if siglas_area == u'ACE':
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'EstudianteIdiomas')
        else:
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'Estudiante')
        # Para asegurar que se tomen unicamente preguntas que representen indicadores ademas
        # Se seleccionan solo ids para poder comparar
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)

        datos = self._contabilizar(siglas_area, nombre_carrera, indicadores)
        conteos = datos['conteos']
        totales = datos['totales']
        porcentajes = datos['porcentajes']

        # conteos = self._contabilizar(siglas_area, nombre_carrera, indicadores)['conteos']
        # totales = self._contabilizar(siglas_area, nombre_carrera, indicadores)['totales']
        # porcentajes = self._contabilizar(siglas_area, nombre_carrera, indicadores)['porcentajes']
            
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)
    

    def por_campos(self, siglas_area, nombre_carrera, docente, seccion):
        # @param id_seccion representa el campo del cuestionario. Seccion = Campo
        if not seccion:
            return None
        # La seccion especifica del cuestionario (por Área) que corresponde
        # ya se determina en la vista anterior
        logg.info("Campo Seccion: " + str(seccion.id) + str(seccion))
        # Se tratan unicamente de preguntas abiertas
        if seccion.orden == 4:
            # Solo en el caso de otros aspectos se puede generar por docente 
            return self.por_otros_aspectos(siglas_area, nombre_carrera, docente, seccion)
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        # de que pertenezcan únicamente al campo (sección) especificado.
        # Se seleccionan solo ids para poder comparar luego
        indicadores=Pregunta.objects.filter(seccion=seccion).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)

        datos = self._contabilizar(siglas_area, nombre_carrera, indicadores)
        conteos = datos['conteos']
        totales = datos['totales']
        porcentajes = datos['porcentajes']
           
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)

    
    def por_otros_aspectos(self, siglas_area, nombre_carrera, docente, seccion):
        # Para contabilizar de acuerdo a la naturaleza del Periodo de Evaluacion
        # Proceso verificado en FiltroPeriodoManager
        Contestacion.objects.set_periodo_evaluacion(self.periodoEvaluacion)

        indicadores_otros = Pregunta.objects.filter(seccion=seccion).filter(tipo__tipo=u'Ensayo').values_list('id', flat=True)

        ### Version anterior con conteo de respuestas comunes
        # conteo=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
        #     evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
        #     evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
        #     evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
        #     pregunta__in=indicadores_otros).values('pregunta','respuesta').annotate(
        #     frecuencia=Count('respuesta')).order_by('pregunta')

        sugerencias = Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion=self.periodoEvaluacion).filter(
            evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__area=siglas_area).filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
                pregunta__in=indicadores_otros)
        # Si se pide ver sugerencias PARA UN DOCENTE en concreto
        if docente:
            sugerencias = sugerencias.filter(
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente=docente.id)
        # Se hace un join manual para obtener el texto de la pregunta desde otra tabla
        sugerencias = sugerencias.extra(
            select={'pregunta__texto' : 'select texto from app_pregunta where app_pregunta.id = app_contestacion.pregunta'}
            ).values('evaluacion__id', 'pregunta__texto','respuesta').order_by('evaluacion__id', 'pregunta__texto')

        return sugerencias
    
    def por_indicador(self,siglas_area, nombre_carrera, id_pregunta ):
        # @param id_pregunta representa el indicador del campo del cuestionario. Pregunta = Indicador
        # La pregunta especcífica del cuestionario (por Área) que corresponde
        # ya se determina en la vista anterior
        # Se selecciona unicamente el id para la comparación posterior
        indicadores = (id_pregunta, )
        datos = self._contabilizar(siglas_area, nombre_carrera, indicadores)
        conteos = datos['conteos']
        totales = datos['totales']
        porcentajes = datos['porcentajes']
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)
        

    def mayor_satisfaccion(self, siglas_area, nombre_carrera):
        """ Retorna los diez indicadores en los cuales se tiene mayor satisfaccion """
        # Todas las Secciones de todos los cuestionarios que pertenecen al periodo de evaluación establecido
        if siglas_area == u'ACE':
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'EstudianteIdiomas')
        else:
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'Estudiante')
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        # Se seleccionan solo ids para poder comparar
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)
        conteos = self._contabilizar(siglas_area, nombre_carrera, indicadores)['conteos']
        # Ordenar de mayor a menor por 'MS' luego por 'S'        
        conteos.sort(lambda c1, c2: -cmp(c1['MS'],c2['MS']) or -cmp(c1['S'],c2['S'] ))
        return dict(conteos=conteos[:10], totales=None, porcentajes=None)

        
    def mayor_insatisfaccion(self, siglas_area, nombre_carrera):
        """ Retorna los diez indicadores en los cuales se tiene mayor satisfaccion """
        # Todas las Secciones de todos los cuestionarios que pertenecen al periodo de evaluación establecido
        if siglas_area == u'ACE':
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'EstudianteIdiomas')
        else:
            secciones = Seccion.objects.filter(cuestionario__in=self.periodoEvaluacion.cuestionarios.all(),
                                               cuestionario__informante__tipo=u'Estudiante')
        # Para asegurar que se tomen unicamente preguntas que representen indicadores además
        # Se seleccionan solo ids para poder comparar
        indicadores=Pregunta.objects.filter(seccion__in=secciones).filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)
        conteos = self._contabilizar(siglas_area, nombre_carrera, indicadores)['conteos']
        # Ordenar de menor a mayor por 'INS' luego por 'PS'
        conteos.sort(lambda c1, c2: -cmp(c1['INS'], c2['INS']) or -cmp(c1['PS'], c2['PS'] ))
        return dict(conteos=conteos[:10], totales=None, porcentajes=None)

    def listado_calificaciones(self, siglas_area, nombre_carrera, formato=None):
        # Obtenemos los id de los Docentes que dictan Asignaturas en la carrera seleccionada
        aux_ids = AsignaturaDocente.objects.filter(
            docente__periodoAcademico=self.periodoEvaluacion.periodoAcademico,
            asignatura__carrera=nombre_carrera,
            asignatura__area=siglas_area
            ).values_list('docente__id', flat=True).distinct()
        # Se agregan tambien los docentes que no tengan Asignaturas pero que pertenezcan a la Carrera
        docentes = DocentePeriodoAcademico.objects.filter(
            Q(periodoAcademico=self.periodoEvaluacion.periodoAcademico) and
            (Q(id__in=aux_ids) or Q(carrera=nombre_carrera))
            ).order_by('usuario__last_name', 'usuario__first_name').all()
        listado_calificaciones = list()
        total = 0
        for docente in docentes:
            resultados = self.por_docente(siglas_area, nombre_carrera, docente.id)
            porcentajes = resultados.get('porcentajes', None)
            # El porcentaje de estudiantes que se declaran MUY SATISFECHOS Y/O SATISFECHOS
            valor = porcentajes.get('MSS', 0)
            logg.info(u'{0} ESE calificación docente: {1} - {2}'.format(docente, porcentajes, valor))
            fila = (docente.usuario.cedula, docente.usuario.last_name, docente.usuario.first_name, valor)
            listado_calificaciones.append(fila)
            total += valor
        media = float(total) / len(docentes)
        return dict(listado_calificaciones=listado_calificaciones, media=media)

    def _contabilizar(self, siglas_area, nombre_carrera, indicadores=[], id_docente=None):
        """
        @param indicadores: lista de ids de pregunta que se involucran en el conteo
        @param id_docente: para el caso unico en el que se contabiliza solo por docente
        @return conteos
        @return totales
        @return porcentajes
        """
        # Para contabilizar de acuerdo a la naturaleza del Periodo de Evaluacion
        # Proceso verificado en FiltroPeriodoManager
        Contestacion.objects.set_periodo_evaluacion(self.periodoEvaluacion)
        
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
                    # Se intercambia por el objeto completo para mayor versatilidad en las vistas
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
                evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera)
            # Filtro adicional si se trata de contabilizar por docente
            if id_docente:
                universo = universo.filter(evaluacion__estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente)
            # Se termina de contabilizar el Universo
            universo = universo.filter(pregunta__in=indicadores).count()

            totales['total'] = universo
            porcentajes = {}
            for grado in ('MS','S','PS','INS'):
                if universo is not 0:
                    numero = totales[grado] * 100 / float(universo)
                else:
                    numero = 0
                porcentajes[grado] = numero
            porcentajes['MSS'] = porcentajes['MS'] + porcentajes['S']
        # Se ordena en base al orden de la seccion y al orden de la pregunta ???
        # conteos = sorted(conteos, key=lambda conteo: conteo['pregunta'].seccion.orden and conteo['pregunta'].orden)
        return dict(conteos=conteos, totales=totales, porcentajes=porcentajes)


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
                         u'odontólogo': u'Odont.', u'odontóloga': u'Odont.', u'odontologo': u'Odont.', u'odontologa': u'Odont.', 
                         u'esp.':u'Esp.', u'Especialista':u'Esp.'  
                         }
        palabras = self.titulo.split() if self.titulo else ""
        for p in palabras:
            if p.lower() in equivalencias.keys():
                return equivalencias[p.lower()]
        return ""

    def contiene(self, diccionario):
        """ 
        Determina si los itemas de un diccionario se corresponden integramente con 
        los atributos del objeto.
        """
        if isinstance(diccionario, dict):
            s1 = set(self.__dict__.items())
            s2 = set(diccionario.items())
            return s2.issubset(s1)
        else:
            return False

    nombres = property(get_nombres, set_nombres)
    apellidos = property(get_apellidos, set_apellidos)
    abreviatura = property(get_abreviatura)

    def get_full_name(self):
	return u'{0} {1}'.format(self.last_name, self.first_name)
        
    def __unicode__(self):
        return u'{0} {1}'.format(self.cedula, self.get_full_name());

