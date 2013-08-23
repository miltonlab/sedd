SEDD [Sistema de Evaluacion de Docentes]
=========================================


Instalación
------------------------------------------------------------------

 - Renombrar settings.cfg a settings.py y configurar cuentas de acceso
 - Sincronizar la BD
 - Aplicar todas las migraciones existentes
 - Cargar los objetos iniciales Configuracion, TipoInformante y TipoPregunta
 - Modificar y copiar proyecto/apache/sedd.cfg a /etc/apache2/sites-enabled 
 - Reiniciar apache

### Cambios en el codigo fuente de Django
 * Cambiar el ancho de #changelist-filter en "...django/contrib/admin/media/css/changelists.css"
 * Aumentar el tamaño de first_name y last_name en el modelo "...django/contrib/auth/models.py"
 * Cambiar el ancho de .dashboard #content "...django/contrib/admin/media/css/base.css"

Requerimientos
-------------------------------------------------------------------
 * Sistema Operativo: Debian squeeze backports
 * python-django 1.3
 * python-psycopg2 2.4.2
 * python-lxml 2.3
 * ordereddict 1.1
 * ptyhon-django-extensions 0.4.2
 * python-soappy 0.12.0
 * django-piston 0.2.3
 * libapache2-mod-wsgi 3.3	(modulo para desplegar en apache)
 * south 0.7.3          	(Migraciones)

#### Opcionales 

 * django-chronograph 0.3.1 (Admin de Tareas)
   - python-dateutil 1.4.1    
 * python-pygraphviz 1.0    (Generación de graficos del modelo)
   - graphviz 2.26   	    
   - libgraphviz-dev
 * ptyhon-mysqldb 1.2.2	    (Importacion desde el anterior Sistema de Evaluacion)
   - libmysqlclient-dev 5.5.27
   

Historial de cambios importantes
-------------------------------------------------------------------

 * Compatibilidad en el uso de la libreria soappy, desde la version 0.12.0 hacia versiones superiores hasta la 0.12.5:
   - Agregado parámetro timeout en "proyecto.app.tools.sgaws.cliente.myHTTPTransport.call"
