
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
    fields = ('titulo','descripcion','orden','cuestionario','seccionPadre')

class CuestionarioAdmin(admin.ModelAdmin):
    inlines = [SeccionEnLinea]
    save_as = True

class OfertaAcademicaSGAEnLinea(admin.TabularInline):
    model = models.OfertaAcademicaSGA
    extra = 1

class PeriodoAcademicoAdmin(admin.ModelAdmin):
    inlines = [OfertaAcademicaSGAEnLinea]

class PeriodoEvaluacionAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Cuestionario,CuestionarioAdmin)
admin.site.register(models.Seccion,SeccionAdmin)
admin.site.register(models.Pregunta,PreguntaAdmin)
admin.site.register(models.PeriodoAcademico,PeriodoAcademicoAdmin)
admin.site.register(models.PeriodoEvaluacion,PeriodoEvaluacionAdmin)
