import sys
import os

# '/' al inicio causa inexactitud
dirbase = os.path.abspath(os.path.dirname(__file__) + '/../../')
sys.path.append(dirbase)

os.environ['DJANGO_SETTINGS_MODULE'] = 'proyecto.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
