#-*- encoding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.core.context_processors import csrf

from django.contrib import auth

from django.forms.forms import NON_FIELD_ERRORS

def index(request):
    return HttpResponse("<h3>Bienvenido al Sistema de Evaluacion de la UNL</h3>")

def login(request):
    from django import forms
    form = forms.Form()
    form.fields['username'] = forms.CharField(label="Username", max_length=30,error_messages={'required':'Ingrese nombre de usuario'})
    form.fields['password'] = forms.CharField(label="Password", widget=forms.PasswordInput,error_messages={'required':'Ingrese el password'})
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
    
    return HttpResponse('Aqui van las carreras')

    
