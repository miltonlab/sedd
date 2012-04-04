#-*- encoding=utf8 -*-
# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
import django #para login de django, evitar colision de nombres
from django.core.context_processors import csrf

def index(request):
    return HttpResponse('Hola mundo django')


def login_test(request):
    #return HttpResponse('Loginnnnnn..........')    
    c = {}
    return render_to_response('login_test.html',c)


def login(request):
    state = "Please log in below..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                django.contrib.auth.login(request, user)
                state = "Ud se ha autentificado!"
            else:
                state = "Su cuenta no está activa, por favor cotacte con el admin."
        else:
            state = "Su usuario y/o contraseña son incorrectos."
    c = {'state':state, 'username': username}
    c.update(csrf(request))
    return render_to_response('login.html',c)
            
