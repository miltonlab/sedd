import sys
import os
import site

# If use virtualenvs
# Add the site-packages of the virtualenv to work with
site.addsitedir('/home/evaluacion/venvs/sedd/local/lib/python2.7/site-packages')

# '/' al inicio causa inexactitud
dirbase = os.path.abspath(os.path.dirname(__file__) + '/../../')
sys.path.append(dirbase)

os.environ['DJANGO_SETTINGS_MODULE'] = 'proyecto.settings'

# If use virtualenvs
# Activate your virtual env
activate_env=os.path.expanduser("/home/evaluacion/venvs/sedd/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
