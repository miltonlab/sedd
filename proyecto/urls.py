from django.conf.urls.defaults import patterns, include, url
#testing...
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ###url(r'^$', 'proyecto.app.views.index'),
    url(r'^$', 'proyecto.app.controllers.app.login'),
    url(r'^login/$', 'proyecto.app.controllers.app.login'),
    url(r'^carreras/$', 'proyecto.app.controllers.app.carreras'),
    url(r'^carrera/asignaturas/(\d{1})/$', 'proyecto.app.controllers.app.carrera_asignaturas'),
    url(r'^carrera/asignaturas/docentes/(\d{1,5})/$', 'proyecto.app.controllers.app.asignaturas_docentes'),
    url(r'^encuestas/(\d{1,5})/$', 'proyecto.app.controllers.app.encuestas'), 
    url(r'^sga/cargar_ofertas_sga/(\d{1,3})/$', 'proyecto.app.controllers.sga.cargar_ofertas_sga'),
    url(r'^sga/cargar_info_sga/(\d{1,3})/$', 'proyecto.app.controllers.sga.cargar_info_sga'),
                       
    url(r'^cuestionarios/$','proyecto.app.controllers.cuestionario.index'),
    url(r'^cuestionarios/responder/(\d+)/$','proyecto.app.controllers.cuestionario.responder'),
    # Examples:

    # url(r'^proyecto/', include('proyecto.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
