# -*- coding: utf-8 -*-

from django import forms

# Para los resultados de la Encuesta de Satisfacción Estudiantil 2012
class ResultadosESEForm(forms.Form):
    opciones = forms.ChoiceField(widget=forms.RadioSelect(),choices=(('uno','uno'),('dos','dos'),('tres','tres')))
