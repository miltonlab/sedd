# -*- coding: utf-8 -*-

from django import forms
from proyecto.app.models import EstudianteAsignaturaDocente
from proyecto.app.models import AsignaturaDocente

# Para los resultados de la Encuesta de Satisfacción Estudiantil 2012
class ResultadosESE2012Form(forms.Form):
    #opciones = forms.ChoiceField(widget=forms.RadioSelect(),
    #choices=(('uno','uno'),('dos','dos'),('tres','tres')))
    def __init__(self, tabulacion):
        forms.Form.__init__(self)
        choices = [(o[0], o[1]) for o in tabulacion.calculos]
        self.fields['opciones'] = forms.ChoiceField(widget=forms.RadioSelect(), choices=choices)

    class Media:
        js = ('jquery-1.6.2.min.js', 'satisfaccion2012.js',)

class EstudianteAsignaturaDocenteAdminForm(forms.ModelForm):
    carrera = forms.CharField(widget=forms.TextInput(attrs={'size':'80', 'readonly':'readonly'}))
    semestre = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    paralelo = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))

    class Meta:
        model = EstudianteAsignaturaDocente
        
    def __init__(self, *args, **kwargs):
        super(EstudianteAsignaturaDocenteAdminForm, self).__init__(*args, **kwargs)
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['carrera'] = instance.carrera
            self.initial['semestre'] = instance.semestre
            self.initial['paralelo'] = instance.paralelo

class AsignaturaDocenteAdminForm(forms.ModelForm):
    carrera = forms.CharField(widget=forms.TextInput(attrs={'size':'80', 'readonly':'readonly'}))
    semestre = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    paralelo = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))

    class Meta:
        model = AsignaturaDocente
        
    def __init__(self, *args, **kwargs):
        super(AsignaturaDocenteAdminForm, self).__init__(*args, **kwargs)
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['carrera'] = instance.carrera
            self.initial['semestre'] = instance.semestre
            self.initial['paralelo'] = instance.paralelo
