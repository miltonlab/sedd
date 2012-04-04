from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sedd.views.home', name='home'),
     url(r'^saes/$', 'saes.views.index'),
     url(r'^saes/login_test/$', 'saes.views.login_test'),
     url(r'^saes/login/$', 'saes.views.login'),
                       
    # url(r'^sedd/', include('sedd.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
