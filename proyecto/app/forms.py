# -*- coding: utf-8 -*-

from django import forms
from django.db.models import Q
from proyecto.app.models import Configuracion
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import PeriodoEvaluacion
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import DireccionCarrera
from proyecto.app.models import AreaSGA
from proyecto.app.models import Asignatura
from proyecto.app.models import EstudianteAsignaturaDocente
from proyecto.app.models import AsignaturaDocente
from proyecto.app.models import Seccion
from proyecto.app.models import Pregunta


class ResultadosEDD2013Form(forms.Form):
    """
    Formulario Unico para los resultados de la Evaluación del 
    Desempenio Docente  2012 - 2013
    """

    def __init__(self, tabulacion, area, carrera):
        forms.Form.__init__(self)
        opciones = [(o[0], o[1]) for o in tabulacion.calculos]
        self.fields['opciones'] = forms.ChoiceField(widget=forms.RadioSelect(), choices=opciones)
        try:
            # Docentes de la carrera que selecciono el coordinador en el periodoAcademico respectivo
            ids_docentes = set([ad.docente.id for ad in AsignaturaDocente.objects.filter(
                        docente__periodoAcademico=tabulacion.periodoEvaluacion.periodoAcademico, 
                        asignatura__carrera=carrera, asignatura__area=area)])
            self.fields['docentes'] = forms.ModelChoiceField(
                queryset=DocentePeriodoAcademico.objects.filter(
                    Q(periodoAcademico=tabulacion.periodoEvaluacion.periodoAcademico) &
                    (Q(id__in=ids_docentes) | Q(carrera=carrera))
                    ).order_by('usuario__last_name', 'usuario__first_name')
                )
        except Exception, ex:
            logg.error("Error en Formulario Resultados EDD2013: {0}".format(ex))


class ResultadosEAAD2012Form(forms.Form):
    """
    Formulario Unico para los resultados de la Evaluación de 
    Actividades Adicionales a la Docencia 2012
    """

    def __init__(self, tabulacion, area, carrera):
        forms.Form.__init__(self)
        opciones = [(o[0], o[1]) for o in tabulacion.calculos]
        self.fields['opciones'] = forms.ChoiceField(widget=forms.RadioSelect(), choices=opciones)
        # Docentes de la carrera que selecciono el coordinador en el periodoAcademico respectivo
        ids_docentes = set([ad.docente.id for ad in AsignaturaDocente.objects.filter(
            docente__periodoAcademico=tabulacion.periodoEvaluacion.periodoAcademico, 
            asignatura__carrera=carrera, asignatura__area=area)])
        self.fields['docentes'] = forms.ModelChoiceField(
            queryset=DocentePeriodoAcademico.objects.filter(
                Q(periodoAcademico=tabulacion.periodoEvaluacion.periodoAcademico) &
                (Q(id__in=ids_docentes) | Q(carrera=carrera))
                ).order_by('usuario__last_name', 'usuario__first_name')
            )


class ResultadosESE2012Form(forms.Form):
    """
    Formulario Único para los resultados de la Encuesta de Satisfacción Estudiantil 2012
    cualquier tipo de Informante
    """

    def __init__(self, tabulacion, area, carrera):
        forms.Form.__init__(self)
        opciones = [(o[0], o[1]) for o in tabulacion.calculos]
        self.fields['opciones'] = forms.ChoiceField(widget=forms.RadioSelect(), choices=opciones)
        # Docentes de la carrera que seleccionó el coordinador
        ids_docentes = set([ad.docente.id for ad in AsignaturaDocente.objects.filter(
            asignatura__carrera=carrera, asignatura__area=area
            )])
        self.fields['docentes'] = forms.ModelChoiceField(queryset=DocentePeriodoAcademico.objects.filter(id__in=ids_docentes))                
        periodoEvaluacion = tabulacion.periodoEvaluacion
        if area == u'ACE':
            cuestionario = periodoEvaluacion.cuestionarios.get(informante__tipo=u'InstitutoIdiomas')
        elif area == u'MED':
            cuestionario = periodoEvaluacion.cuestionarios.get(informante__tipo=u'EstudianteMED')
        else:  # Todas las demás areas
            cuestionario = periodoEvaluacion.cuestionarios.get(informante__tipo=u'Estudiante')
        secciones = Seccion.objects.filter(cuestionario=cuestionario)
        campos = [ (s.id, u'{0}. {1}'.format(s.orden, s.titulo)) for s in secciones ]
        preguntas = []
        for s in secciones:
            preguntas.extend(s.preguntas.all())
        # Por estética en la presentación del SELECT del form de HTML 
        indicadores = [ (p.id, u'{0}.{1}. {2}'.format(p.seccion.orden, p.orden, p.__unicode__()[:150])) for p in preguntas ]
        
        self.fields['campos'] = forms.ChoiceField(choices=campos)
        self.fields['indicadores'] = forms.ChoiceField(choices=indicadores)

        
    class Media:
        ###js = ('/static/js/jquery-1.6.2.min.js', '/static/js/ese2012.js',)
        js = ('js/ese2012.js',)


class ResultadosForm(forms.Form):
    periodo_academico = forms.ModelChoiceField(queryset=PeriodoAcademico.objects.all())
    periodo_academico.label = u'Periodo Académico'
    periodo_evaluacion = forms.ModelChoiceField(PeriodoEvaluacion.objects.none())
    periodo_evaluacion.label = u'Periodo Evaluación'
    area = forms.ModelChoiceField(AreaSGA.objects.none())
    carrera = forms.ModelChoiceField(Asignatura.objects.none())
    # docente = forms.ModelChoiceField(Asignatura.objects.none())
    # semestre = forms.ModelChoiceField(Asignatura.objects.none())
    # paralelo = forms.ModelChoiceField(Asignatura.objects.none())


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
    """ Formulario para AsignaturaDocente en Linea en el objeto DocentePeriodoAcademico """ 
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
