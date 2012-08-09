

Instalación:
==================================================================
 - Renombrar settings.cfg a settings.py y configurar cuentas
 - Modificar y copiar proyecto/apache/sedd.cfg a /etc/apache2/sites-enabled 
 - Aumentar el tamaño de first_name y last_name en el modelo auth.User 
 - Reiniciar apache (por cada cambio)


Requerimientos: 
===================================================================
 * Sistema Operativo: Debian squeeze backports
 * python-django 1.3
 * ptyhon-django-extensions 0.4.2
 * python-soappy 0.12.0
 * python-psycopg2 2.4.2


Opcionales 
-------------------------------------------------------------------

 * django-chronograph 0.3.1 (Admin de Tareas)
 * python-dateutil 1.4.1    (Admin de Tareas)
 * graphviz 2.26   	    (Generación de graficos del modelo)
 * python-pygraphviz 1.0    (Generación de graficos del modelo)
 * libapache2-mod-wsgi 3.3  (modulo para desplegar en apache)
