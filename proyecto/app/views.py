# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from app.models import Cuestionario
from django.core.context_processors import csrf

import logging

log = logging.getLogger('logapp')

def index(request):
    return HttpResponse("<h3>Bienvenido al Sistema de Evaluacion de la UNL</h3>")

def login(request):
    from django import forms
    form = forms.Form()
    form.fields['username'] = forms.CharField(label="Username", max_length=30)
    form.fields['password'] = forms.CharField(label="Password", widget=forms.PasswordInput)
    data = dict(form=form)    
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        username = username.upper()
        auxiliar = username

    data.update(csrf(request))
    return render_to_response("app/login.html",data)
    
def cuestionario_index(request):
    lista_encuestas = Cuestionario.objects.all()
    return render_to_response("app/cuestionarios/index.html",dict(lista_encuestas=lista_encuestas))
    #return HttpResponse("testing...")
    
def cuestionario_responder(request, id_cuestionario):
    try:
        c = Cuestionario.objects.get(id=id_cuestionario)
        return render_to_response('app/cuestionarios/responder.html',dict(cuestionario=c))
    except Cuestionario.DoesNotExist:
        return HttpResponse("No exsite esta encuesta")
    
