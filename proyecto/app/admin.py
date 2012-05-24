#-*- encoding: utf-8 -*-

from django.contrib import admin
from proyecto.app import models

class ItemPreguntaEnLinea(admin.StackedInline):
    model = models.ItemPregunta
    extra = 1

class PreguntaAdmin(admin.ModelAdmin):
    inlines = [ItemPreguntaEnLinea]
    fields = ('texto','orden','tipo','seccion')

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

class OfertaAcademicaSGAEnLinea(admin.TabularInline):
    model = models.OfertaAcademicaSGA
    extra = 1

class PeriodoEvaluacionEnLinea(admin.StackedInline):
    model = models.PeriodoEvaluacion
    extra = 1

class PeriodoAcademicoAdmin(admin.ModelAdmin):
    inlines = (PeriodoEvaluacionEnLinea,)
    filter_horizontal = ('ofertasAcademicasSGA',)


class EstudianteAsignaturaDocenteEnLinea(admin.TabularInline):
    model = models.EstudianteAsignaturaDocente
    extra = 1
    verbose_name = 'Asignaturas de Estudiante'
    raw_id_fields = ('asignaturaDocente',)
    exclude = ('preguntas',)


class EstudiantePeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('cedula', '__unicode__')
    list_per_page = 20
    search_fields = ('usuario__cedula','usuario__last_name','usuario__first_name')
    inlines = (EstudianteAsignaturaDocenteEnLinea,)
    raw_id_fields = ('usuario',)
    
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
    #TODO: combobox
    #readonly_fields = ('area','carrera','semestre','paralelo','tipo',)
    fieldsets = (
        ('Datos Académicos', {
            'fields': ('area', 'carrera', 'semestre', 'paralelo')
            }),
        ('Asignatura', {
            'fields': ('nombre', 'tipo', 'creditos', 'duracion')
            }),        
        )
    

class UsuarioAdmin(admin.ModelAdmin):
    search_fields = ('username','cedula')
    list_display = ('cedula','get_full_name',)
    list_display_links = ('cedula','get_full_name',)
    list_per_page = 20

class ConfiguracionAdmin(admin.ModelAdmin):
    actions = None
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(models.Cuestionario,CuestionarioAdmin)
admin.site.register(models.Seccion,SeccionAdmin)
admin.site.register(models.Pregunta,PreguntaAdmin)
admin.site.register(models.PeriodoAcademico,PeriodoAcademicoAdmin)
admin.site.register(models.EstudiantePeriodoAcademico, EstudiantePeriodoAcademicoAdmin)
admin.site.register(models.DocentePeriodoAcademico, DocentePeriodoAcademicoAdmin)
admin.site.register(models.AsignaturaDocente, AsignaturaDocenteAdmin)
admin.site.register(models.Asignatura, AsignaturaAdmin)
admin.site.register(models.Usuario, UsuarioAdmin)
admin.site.register(models.Configuracion, ConfiguracionAdmin)
