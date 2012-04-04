#-*- encoding=utf8 -*-
from django.db import models

# Create your models here.

class Area(models.Model):
    siglas = models.CharField(max_length=10, blank=True)
    nombre = models.CharField(max_length=240, blank=True)

    def __unicode__(self):
        return self.siglas;

    def __repr__(self):
        return self.siglas;
    
    class Meta:
        db_table = u'areas'
        managed = False


class Carrera(models.Model):
    nombre = models.CharField(max_length=240, blank=True)
    area = models.ForeignKey(Area)

    def __unicode__(self):
        return self.nombre;

    class Meta:
        db_table = u'carreras'
        managed = False        

class Estudiante(models.Model):
    cedula = models.CharField(max_length=15, blank=True)
    nombres = models.CharField(max_length=180, blank=True)
    apellidos = models.CharField(max_length=180, blank=True)
    carrera = models.ForeignKey(Carrera)

    def __unicode__(self):
        return '%s %s'%(self.nombres,self.apellidos);
    
    class Meta:
        db_table = u'estudiantes'
        managed = False

    
class Docente(models.Model):
    cedula = models.CharField(max_length=15, blank=False)
    nombres = models.CharField(max_length=240, blank=True)
    apellidos = models.CharField(max_length=240, blank=True)
    titulo = models.CharField(max_length=300)
    unidades = models.ManyToManyField(Estudiante, through='Unidad')

    def __unicode__(self):
        return '%s %s'%(self.nombres,self.apellidos);

    class Meta:
        db_table = u'docentes'
        managed = False


class Unidad(models.Model):
    estudiante = models.ForeignKey(Estudiante)
    docente = models.ForeignKey(Docente)
    nombre = models.CharField(max_length=600, blank=False)
    
    def __get_tipo(self):
        tipos = [u'taller',u'curso',u'módulo',u'modulo',u'unidad']
        l = [t for t in tipos if t in self.nombre.lower()]
        return l[0]  if l else u'otro'
    
    tipo = property(fget=__get_tipo,doc='Tipo de la Unidad')
    
    def __unicode__(self):
        return '%s'%(self.nombre[:20]);

    class Meta:
        db_table = u'unidades'
        managed = False        

class Encuesta(models.Model):
    nombre = models.CharField(max_length=100, blank=False)
    fecha = models.DateTimeField('fecha')

class Pregunta(models.Model):
    codigo = models.CharField(max_length=5, blank=False)
    descripcion = models.CharField(max_length=5, blank=False)
    seccion = models.IntegerField()
