#-*- encoding: utf-8 -*-
from proyecto.app.models import Cuestionario

def index(request):
    lista_encuestas = Cuestionario.objects.all()
    return render_to_response("app/cuestionarios/index.html",dict(lista_encuestas=lista_encuestas))
    #return HttpResponse("testing...")
    
def responder(request, id_cuestionario):
    try:
        c = Cuestionario.objects.get(id=id_cuestionario)
        return render_to_response('app/cuestionarios/responder.html',dict(cuestionario=c))
    except Cuestionario.DoesNotExist:
        return HttpResponse("No exsite esta encuesta")
    
