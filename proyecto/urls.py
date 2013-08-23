#encoding:utf-8
from django.conf.urls.defaults import patterns, include, url


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # django-chronograph: Aplicacion para comandos de administración
    # url(r'^admin/chronograph/job/(?P<pk>\d+)/run/$', 'chronograph.views.job_run', name="admin_chronograph_job_run"),
                      
    url(r'^$', 'proyecto.app.controllers.portada', name='portada'),                        
    url(r'^login/$', 'proyecto.app.controllers.login', name='login'),
    url(r'^index/$', 'proyecto.app.controllers.index', name='index'),                       
    url(r'^logout/$', 'proyecto.app.controllers.logout', name='logout'),
    # Recibe como parametro el numero de carrera
    url(r'^estudiante/asignaturas/docentes/(\d{1})/$', 
        'proyecto.app.controllers.estudiante_asignaturas_docentes', name='estudiante_asignaturas_docentes'),
    # Recibe un número de carrera de la sesion                       
    url(r'^director/docentes/(\d{1})/$', 
        'proyecto.app.controllers.director_docentes',
        name='director_docentes'),
    # Recibe un número de carrera de la sesion                  
    url(r'^pares_academicos/docentes/(\d{1})/$', 'proyecto.app.controllers.pares_academicos_docentes', 
        name='pares_academicos_docentes'),
    url(r'^encuestas/(?P<id_docente>\d{1,5})/(?P<id_asignatura>\d{1,5})/(?P<id_tinformante>\d{1,2})/(?P<id_cuestionario>\d{1,2})/', 
        'proyecto.app.controllers.encuestas', name='encuestas'),
    url(r'^encuesta/responder/(\d{1,5})/$', 'proyecto.app.controllers.encuesta_responder',
        name='encuesta_responder'),
    url(r'^encuesta/grabar/$', 'proyecto.app.controllers.encuesta_grabar',name='encuesta_grabar'),
    # Recibe numero de carrera
    url(r'^resultados/carrera/(\d{1})/$', 'proyecto.app.controllers.resultados_carrera',name='resultados_carrera'),
    url(r'^resultados/periodo/(\d{1,2})/$', 'proyecto.app.controllers.menu_resultados_carrera',name='menu_resultados_carrera'),
    url(r'^resultados/mostrar/$', 'proyecto.app.controllers.mostrar_resultados',name='mostrar_resultados'),                       
    url(r'^sga/cargar_ofertas_sga/(\d{1,3})/$', 'proyecto.app.controllers.cargar_ofertas_sga',name='cargar_ofertas_sga'),
    url(r'^admin/resumen/evaluaciones/$', 'proyecto.app.controllers.resumen_evaluaciones',name='resumen_evaluaciones'),
    url(r'^admin/resumen/calcular/$', 'proyecto.app.controllers.calcular_resumen',name='calcular_resumen'),
    url(r'^admin/app/resultados/$', 'proyecto.app.controllers.resultados',name='resultados'),
    url(r'^admin/', include(admin.site.urls)),
    # API Webservices
    url(r'^api/', include('proyecto.app.api.urls'))
)
