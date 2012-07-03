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
        self.tipo = 'InstitutoIdiomas'

class InformanteEstudianteMED(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'EstudianteMED'

class InformanteIdiomasMED(TipoInformante):
    def __init__(self):
        TipoInformante.__init__(self)
        self.tipo = 'IdiomasMED'

class Cuestionario(models.Model):
    titulo = models.CharField(max_length='100')
    encabezado = models.TextField()
    incio = models.DateTimeField('Inicio de la Encuesta')
    fin=models.DateTimeField('Finalización de la Encuesta')
    informante = models.ForeignKey(TipoInformante)
    periodoEvaluacion = models.ForeignKey('PeriodoEvaluacion', related_name='cuestionarios')
    
    def __unicode__(self):
        return self.titulo


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
        return u'{0} - {1} - {2}:{3}'.format(self.estudianteAsignaturaDocente.estudiante.cedula(),
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
    ###pregunta = models.ForeignKey('Pregunta',related_name='respuestas')

    def __unicode__(self):
        return self.texto


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
    tabulacion = models.ForeignKey('Tabulacion', related_name='periodosEvaluacion', verbose_name="Tipo Tabulación")
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

    def __unicode__(self):
        return self.nombre


class Tabulacion(models.Model):
    """
    Superclase que permite procesar la informacion generada por un
    conjunto de encuestas pertenecientes a un Periodo de Evaluación.
    """
    descripcion = models.CharField(max_length='250')
    tipo = models.CharField(max_length='20', unique=True)
    
    def __unicode__(self):
        return self.descripcion

    
class TabulacionSatisfaccion2012(Tabulacion):
    # Se hecha de menos las clases Abstractas y el polimorfismo

    def __init__(self):
        Tabulacion.__init__(self)
        self.tipo = u'ESE2012'
        self.descripcion = u'Encuesta de Satisfacción Estudiantil 2012'
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
    def por_docente(self, id_docente):
        """
        Satisfacción Estudiantil por módulo, curso, unidad o taller
        """
        periodoEvaluacion = Configuracion.getPeriodoEvaluacionActual()
        asignaturas = Evaluacion.objects.filter(
            estudianteAsignaturaDocente__asignaturaDocente__docente__id=id_docente).filter(
            cuestionario__periodoEvaluacion=periodoEvaluacion).values_list(
            'estudianteAsignaturaDocente__asignaturaDocente__asignatura__id').distinct()
        asignaturas = [tupla[0] for tupla in asignaturas]
        resultados = []
        return resultados

    # TODO: Usar carrera_id en vez de nombre_carrera
    def por_carrera(self, nombre_carrera, nombre_area):
        from django.db.models import Count
        indicadores=Pregunta.objects.filter(tipo__tipo=u'SeleccionUnica').values_list('id', flat=True)

        conteo_ms=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(ms=Count('respuesta')).filter(
            respuesta='4').order_by('pregunta')

        conteo_s=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(s=Count('respuesta')).filter(
            respuesta='3').order_by('pregunta')
        
        conteo_ps=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(ps=Count('respuesta')).filter(
            respuesta='2').order_by('pregunta')
        
        conteo_ins=Contestacion.objects.filter(evaluacion__cuestionario__periodoEvaluacion__tabulacion__tipo='ESE2012').filter(
            evaluacion__estudianteAsignaturaDocente__asignaturaDocente__asignatura__carrera=nombre_carrera).filter(
            pregunta__in=indicadores).values('pregunta').annotate(ins=Count('respuesta')).filter(
            respuesta='1').order_by('pregunta')

        lista = []
        for i in indicadores:
            conteo = {}            
            for c in conteo_ms:
                if c['pregunta'] == i:
                    conteo.update(c)
            for c in conteo_s:
                if c['pregunta'] == i:
                    conteo.update(c)
            for c in conteo_ps:
                if c['pregunta'] == i:
                    conteo.update(c)
            for c in conteo_ins:
                if c['pregunta'] == i:
                    conteo.update(c)
            lista.append(conteo)    
        return lista
        #return conteo_ms + conteo_s + conteo_ps + conteo_ins

    
        ###return {'carrera':nombre_carrera,  'MS':muy_satisfecho/float(num_respuestas)*100,  'S':satisfecho/float(num_respuestas)*100,
        ###        'PS':poco_satisfecho/float(num_respuestas)*100,  'IS':insatisfecho/float(num_respuestas)*100  }

    def por_campos(self):
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
    # Asignatura-Docente
    asignaturaDocente = models.ForeignKey('AsignaturaDocente', related_name='estudiantesAsignaturaDocente')
    matricula = models.IntegerField(blank=True, null=True)    
    estado = models.CharField(max_length='60', blank=True, null=True)
    ###?evaluacion = models.OneToOneField('Evaluacion', related_name='estudiantes', blank=True, null=True)

    def get_asignatura(self):
        return self.asignaturaDocente.asignatura

    def get_docente(self):
        return self.asignaturaDocente.docente
    
    class Meta:
        verbose_name = 'Estudiante Asignaturas'
        unique_together = ('estudiante','asignaturaDocente')

    def __unicode__(self):
        return u"{0} >> {1}".format(self.estudiante, self.asignaturaDocente)


class AsignaturaDocente(models.Model):
    asignatura = models.ForeignKey('Asignatura', related_name='docentesAsignatura')
    docente = models.ForeignKey('DocentePeriodoAcademico', related_name='asignaturasDocente')
    
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
        equivalencias = {'magister':'Mg.', 'ingeniero':'Ing.', 'ingeniera':'Ing.', 'doctor':'Dr.', 'doctora':'Dra.', 'master':'Ms.',
                         'mg.':'Mg.', 'licenciado':'Lic.', 'licenciada':'Lic.', 'economista':'Eco.', 'eco.':'Eco.', 'medico':'Dr.',
                         'dra.':'Dra.','dr.':'Dr.','lic.':'Lic.', 'licdo.':'Lic.','ing.':'Ing.', 'phd.':'Phd.',u'médico':'Dr.'
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
