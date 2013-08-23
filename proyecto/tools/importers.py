from data_importer import BaseImporter

class DocentesImporter(BaseImporter):
        fields = ['cedula','nombres','apellidos','periodoAcademico']
        #requerid_fields = ['periodoAcademico']





# ------------------------------------------------------

from proyecto.app.models import DocentePeriodoAcademico
from proyecto.app.models import Usuario
from proyecto.app.models import PeriodoAcademico

from adaptor.model import CsvModel
from adaptor.model import CsvDbModel
from adaptor.fields import ForeignKey
from adaptor.fields import CharField
from adaptor.fields import BooleanField

class DocentePeriodoAcademicoCsvModel(CsvDbModel):
    
    class Meta:
        delimiter = ';'
        dbModel = DocentePeriodoAcademico
