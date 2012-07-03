# -*- coding: utf-8 -*-

from django.contrib import admin
from proyecto.app import models

import logging
logg = logging.getLogger('logapp')


class ItemPreguntaEnLinea(admin.StackedInline):
    model = models.ItemPregunta
    extra = 1

class PreguntaAdmin(admin.ModelAdmin):
    inlines = [ItemPreguntaEnLinea]
    fields = ('texto','orden','tipo','seccion')

    # Sobreescrito
    def save_model(self, request, obj, form, change):
        if change:
            obj.save()
            return
        # request es un objeto de tipo WSGIRequest
        tipo = request.POST['tipo']
        # Tipo de pregunta:  SeleccionUnica
        if tipo=='2':
            longitud = request.POST['longitud']
            numeracion = request.POST['numeracion']
            if longitud == '' or numeracion == '':
                return
            # Si se trata de una pregunta de Selección por predeterminada
            obj.save()
            longitud = int(longitud)
            if numeracion == '1':
                for n in range(1, longitud+1):
                    item = models.ItemPregunta(texto=str(n), pregunta=obj, orden=n)
                    item.save()
            elif numeracion.lower() == 'a':
                for i,n in enumerate(letters):
                    item = models.ItemPregunta(texto=n, pregunta=obj, orden=i)
                    item.save()
        # Cualquier otro tipo de pregunta
        else:
            obj.save()
          

class PreguntaEnLinea(admin.TabularInline):
    model = models.Pregunta
    extra = 1

class SeccionEnLinea(admin.TabularInline):
    model = models.Seccion
    extra = 1

class SeccionAdmin(admin.ModelAdmin):
    inlines = [PreguntaEnLinea]
    fields = ('titulo','descripcion','orden','cuestionario')
    

class CuestionarioAdmin(admin.ModelAdmin):
    inlines = [SeccionEnLinea]
    save_as = True

    class Media:
        js = ['js/tiny_mce/tiny_mce.js', 'js/tmce_config.js',]
    
class OfertaAcademicaSGAEnLinea(admin.TabularInline):
    model = models.OfertaAcademicaSGA
    extra = 1

class PeriodoEvaluacionAdmin(admin.ModelAdmin):
    filter_horizontal = ('areasSGA',)
    ###model = models.PeriodoEvaluacion
    ###extra = 1
    

class PeriodoAcademicoAdmin(admin.ModelAdmin):
    ###inlines = (PeriodoEvaluacionEnLinea,)
    filter_horizontal = ('ofertasAcademicasSGA',)


class EstudianteAsignaturaDocenteEnLinea(admin.TabularInline):
    model = models.EstudianteAsignaturaDocente
    extra = 1
    verbose_name = 'Asignaturas de Estudiante'
    raw_id_fields = ('asignaturaDocente',)

class EstudiantePeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('cedula', '__unicode__')
    list_per_page = 20
    search_fields = ('usuario__username','usuario__cedula','usuario__last_name','usuario__first_name')
    inlines = (EstudianteAsignaturaDocenteEnLinea,)
    raw_id_fields = ('usuario',)

    change_form_template = 'admin/app/estudianteperiodoacademico/change_form.html'
    
    # Para disponer de información extra en el template
    ### En desarrollo
    def change_view(self, request, object_id, extra_context={}):
        estudiante = models.EstudiantePeriodoAcademico.objects.get(id=object_id)
        extra_context['paralelos'] = estudiante.paralelos()
        logg.info(extra_context['paralelos'])
        extra_context['prueba'] = 'pruebaaaa'
        return super(EstudiantePeriodoAcademicoAdmin, self).change_view(request, object_id, extra_context)

    
class AsignaturaDocenteAdmin(admin.ModelAdmin):
    raw_id_fields = ('asignatura','docente',)

class AsignaturaDocenteEnLinea(admin.TabularInline):
    model = models.AsignaturaDocente
    extra = 1
    verbose_name = 'Asignaturas de Docente'
    raw_id_fields = ('asignatura',)

    
class DocentePeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('cedula', '__unicode__')
    list_per_page = 20
    search_fields = ('usuario__cedula','usuario__last_name','usuario__first_name') 
    inlines = (AsignaturaDocenteEnLinea,)
    raw_id_fields = ('usuario',)

    
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('carrera','semestre','paralelo', '__unicode__')
    list_display_links = ('__unicode__',)
    search_fields = ('area','carrera','semestre','paralelo','nombre',)
    list_filter = ('area','carrera','semestre','paralelo','tipo',)
    list_per_page = 20
    # TODO: combobox
    #readonly_fields = ('area','carrera','semestre','paralelo','tipo',)
    fieldsets = (
        ('Datos Académicos', {
            'fields': ('area', 'carrera', 'semestre', 'paralelo')
            }),
        ('Asignatura', {
            'fields': ('nombre', 'tipo', 'creditos')
            }),
        ('Duracion', {
            'fields': ('duracion', 'inicio', 'fin')
            }),        
        
        )
    

class UsuarioAdmin(admin.ModelAdmin):
    search_fields = ('username','cedula')
    list_display = ('username','cedula','get_full_name',)
    list_display_links = ('cedula','get_full_name',)
    list_per_page = 20

class ConfiguracionAdmin(admin.ModelAdmin):
    actions = None
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class ContestacionEnLinea(admin.TabularInline):
    model = models.Contestacion
    extra = 15
    verbose_name = 'Respuesta'
    
class EvaluacionAdmin(admin.ModelAdmin):
    search_fields = ('estudianteAsignaturaDocente__estudiante__usuario__cedula',
                     'estudianteAsignaturaDocente__asignaturaDocente__docente__usuario__cedula')
    inlines = (ContestacionEnLinea,)
    list_per_page = 30
    list_filter = ('fechaFin',)
    date_hierarchy = 'fechaFin'

    def has_add_permission(self, request):
        return False
    
admin.site.register(models.Cuestionario,CuestionarioAdmin)
admin.site.register(models.Seccion,SeccionAdmin)
admin.site.register(models.Pregunta,PreguntaAdmin)
admin.site.register(models.PeriodoAcademico,PeriodoAcademicoAdmin)
admin.site.register(models.PeriodoEvaluacion,PeriodoEvaluacionAdmin)
admin.site.register(models.EstudiantePeriodoAcademico, EstudiantePeriodoAcademicoAdmin)
admin.site.register(models.DocentePeriodoAcademico, DocentePeriodoAcademicoAdmin)
admin.site.register(models.AsignaturaDocente, AsignaturaDocenteAdmin)
admin.site.register(models.Asignatura, AsignaturaAdmin)
admin.site.register(models.Usuario, UsuarioAdmin)
admin.site.register(models.Configuracion, ConfiguracionAdmin)
admin.site.register(models.Evaluacion, EvaluacionAdmin)
