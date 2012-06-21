from django.conf.urls.defaults import patterns, include, url


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'proyecto.app.controllers.index'),
    url(r'^login/$', 'proyecto.app.controllers.login'),
    url(r'^logout/$', 'proyecto.app.controllers.logout'),
    url(r'^portada/$', 'proyecto.app.controllers.portada'), 
    # Recibe como parametro el numero de carrera
    url(r'^estudiante/asignaturas/docentes/(\d{1})/$', 
        'proyecto.app.controllers.estudiante_asignaturas_docentes'),
    url(r'^encuestas/(\d{1,5})/(\d{1,5})/$', 'proyecto.app.controllers.encuestas'),
    url(r'^encuesta/responder/(\d{1,5})/$', 'proyecto.app.controllers.encuesta_responder'),
    url(r'^encuesta/grabar/$', 'proyecto.app.controllers.encuesta_grabar'),
    url(r'^resultados/carrera/(\w)/$', 'proyecto.app.controllers.resultados_carrera'),                       
    url(r'^sga/cargar_ofertas_sga/(\d{1,3})/$', 'proyecto.app.controllers.cargar_ofertas_sga'),
    url(r'^sga/cargar_info_sga/(\d{1,3})/$', 'proyecto.app.controllers.cargar_info_sga'),
    # Examples:

    # url(r'^proyecto/', include('proyecto.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    ### url(r'^tinymce/', include('tinymce.urls')), 
                       
)
