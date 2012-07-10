
Instalación:
==================================================================
 - Renombrar settings.cfg a settings.py y configurar cuentas
 - Modificar y copiar proyecto/apache/sedd.cfg a /etc/apache2/sites-enabled 
 - Aumentar el tamaño de first_name y last_name en el modelo auth.User 
 - Reiniciar apache (por cada cambio)


Requerimientos: 
===================================================================
 * Sistema Operativo: Debian squeeze backports
 * Django 1.3
 * python-soappy 0.12.0
 * python-psycopg2 2.4.2

Deploying with apache and mod_wsgi

 * libapache2-mod-wsgi 3.3
