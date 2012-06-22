# -*- coding: utf-8 -*-

from django import forms

# Para los resultados de la Encuesta de Satisfacción Estudiantil 2012
class ResultadosESE2012Form(forms.Form):
    #opciones = forms.ChoiceField(widget=forms.RadioSelect(),
    #choices=(('uno','uno'),('dos','dos'),('tres','tres')))
    def __init__(self, tabulacion):
        forms.Form.__init__(self)
        choices = [(o[0], o[1]) for o in tabulacion.calculos]
        self.fields['opciones'] = forms.ChoiceField(widget=forms.RadioSelect(), choices=choices)
