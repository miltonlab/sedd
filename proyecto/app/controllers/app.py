#-*- encoding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import auth
from django.forms.forms import NON_FIELD_ERRORS

from proyecto.app.models import DocentePeriodoAcademicoAsignatura
from proyecto.app.models import EstudiantePeriodoAcademicoAsignatura
from proyecto.app.models import EstudiantePeriodoAcademico
from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import PeriodoAcademico
from proyecto.app.models import Configuracion

import logging
logg = logging.getLogger('logapp')

def index(request):
    return HttpResponse("<h3>Bienvenido al Sistema de Evaluacion de la UNL</h3>")

def login(request):
    from django import forms
    form = forms.Form()
    form.fields['username'] = forms.CharField(label="Username", max_length=30,
                                              error_messages={'required':'Ingrese nombre de usuario'})
    form.fields['password'] = forms.CharField(label="Password", widget=forms.PasswordInput,
                                              error_messages={'required':'Ingrese el password'})
    data = dict(form=form)    
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)        
        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('/carreras')
        else:
            form.full_clean()
            form._errors[NON_FIELD_ERRORS] = form.error_class(['Error de usuario o contraseña'])
    data.update(csrf(request))
    return render_to_response("app/login.html",data)
        

def carreras(request):
    pa = Configuracion.getPeriodoAcademicoActual()
    pe = Configuracion.getPeriodoEvaluacionActual()
    usuario = request.user
    try:
        estudiante = EstudiantePeriodoAcademico.objects.get(periodoAcademico=pa, estudiante=usuario)
        carreras = estudiante.asignaturas.values('asignatura__carrera').distinct()
        # Al final un diccionario de carreras
        carreras = [ dict(id_tmp=i, nombre=c['asignatura__carrera']) for i,c in enumerate(carreras) ]
        request.session['estudiante'] = estudiante
        request.session['carreras'] = carreras
        return render_to_response("app/carreras.html", context_instance=RequestContext(request))
    except EstudiantePeriodoAcademico.DoesNotExist:
        try:
            docente = DocentePeriodoAcademico.objects.get(periodoAcademico=pa, docente=usuario)
            return HttpResponse('Ud es docente en el presente periodo')
        except DocentePeriodoAcademico.DoesNotExist:
            return HttpResponse('Fin')

def carrera_unidades(request, id_tmp):
    estudiante = request.session['estudiante']
    carrera = request.session['carreras'][int(id_tmp)]
    asignaturas = EstudiantePeriodoAcademicoAsignatura.objects.filter(estudiante=estudiante, asignatura__carrera=carrera).all()
    logg.info(str(asignaturas))
    return render_to_response("app/carrera_unidades.html",dict(asignaturas=asignaturas, estudiante=estudiante))
    #return HttpResponse('Unidades: '+ str(estudiante) + str(len(asignaturas)))


    
