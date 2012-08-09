# -*- coding: utf-8 -*-

from django_extensions.management.jobs import BaseJob
import datetime

class Job(BaseJob):
    """
    Se puede usar para verificar el resultado y
    la frecuencia de ejecución  de un Job
    """
    help = "Un simple ejemplo que escribe a un archivo."

    def execute(self):
        f = open("/tmp/job.txt",'a')
        f.write('Ejecutando tarea ' + str(datetime.datetime.now()) + '\n')
        f.close()
