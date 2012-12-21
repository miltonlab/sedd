# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TipoInformante'
        db.create_table('app_tipoinformante', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(unique=True, max_length='20')),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='100')),
        ))
        db.send_create_signal('app', ['TipoInformante'])

        # Adding model 'InformanteDocente'
        db.create_table('app_informantedocente', (
            ('tipoinformante_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoInformante'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('app', ['InformanteDocente'])

        # Adding model 'InformanteEstudiante'
        db.create_table('app_informanteestudiante', (
            ('tipoinformante_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoInformante'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('app', ['InformanteEstudiante'])

        # Adding model 'InformanteEstudianteNovel'
        db.create_table('app_informanteestudiantenovel', (
            ('tipoinformante_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoInformante'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('app', ['InformanteEstudianteNovel'])

        # Adding model 'InformanteDirectivos'
        db.create_table('app_informantedirectivos', (
            ('tipoinformante_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoInformante'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('app', ['InformanteDirectivos'])

        # Adding model 'InformanteInstitutoIdiomas'
        db.create_table('app_informanteinstitutoidiomas', (
            ('tipoinformante_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoInformante'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('app', ['InformanteInstitutoIdiomas'])

        # Adding model 'InformanteEstudianteMED'
        db.create_table('app_informanteestudiantemed', (
            ('tipoinformante_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoInformante'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('app', ['InformanteEstudianteMED'])

        # Adding model 'InformanteIdiomasMED'
        db.create_table('app_informanteidiomasmed', (
            ('tipoinformante_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoInformante'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('app', ['InformanteIdiomasMED'])

        # Adding model 'Cuestionario'
        db.create_table('app_cuestionario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length='100')),
            ('encabezado', self.gf('django.db.models.fields.TextField')()),
            ('inicio', self.gf('django.db.models.fields.DateTimeField')()),
            ('fin', self.gf('django.db.models.fields.DateTimeField')()),
            ('informante', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.TipoInformante'], null=True, blank=True)),
            ('periodoEvaluacion', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='cuestionarios', null=True, to=orm['app.PeriodoEvaluacion'])),
        ))
        db.send_create_signal('app', ['Cuestionario'])

        # Adding model 'Contestacion'
        db.create_table('app_contestacion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pregunta', self.gf('django.db.models.fields.IntegerField')()),
            ('respuesta', self.gf('django.db.models.fields.TextField')()),
            ('evaluacion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contestaciones', to=orm['app.Evaluacion'])),
        ))
        db.send_create_signal('app', ['Contestacion'])

        # Adding model 'Evaluacion'
        db.create_table('app_evaluacion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fechaInicio', self.gf('django.db.models.fields.DateField')()),
            ('fechaFin', self.gf('django.db.models.fields.DateField')()),
            ('horaInicio', self.gf('django.db.models.fields.TimeField')()),
            ('horaFin', self.gf('django.db.models.fields.TimeField')()),
            ('cuestionario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evaluaciones', to=orm['app.Cuestionario'])),
            ('estudianteAsignaturaDocente', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evaluaciones', to=orm['app.EstudianteAsignaturaDocente'])),
        ))
        db.send_create_signal('app', ['Evaluacion'])

        # Adding model 'Resultados'
        db.create_table('app_resultados', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('app', ['Resultados'])

        # Adding model 'TipoPregunta'
        db.create_table('app_tipopregunta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(unique=True, max_length='20')),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='100')),
        ))
        db.send_create_signal('app', ['TipoPregunta'])

        # Adding model 'SeleccionUnica'
        db.create_table('app_seleccionunica', (
            ('tipopregunta_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoPregunta'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('app', ['SeleccionUnica'])

        # Adding model 'Ensayo'
        db.create_table('app_ensayo', (
            ('tipopregunta_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoPregunta'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('app', ['Ensayo'])

        # Adding model 'Seccion'
        db.create_table('app_seccion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length='50')),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='100')),
            ('orden', self.gf('django.db.models.fields.IntegerField')()),
            ('seccionPadre', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subsecciones', null=True, db_column='seccion_padre_id', to=orm['app.Seccion'])),
            ('cuestionario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='secciones', to=orm['app.Cuestionario'])),
        ))
        db.send_create_signal('app', ['Seccion'])

        # Adding model 'Pregunta'
        db.create_table('app_pregunta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('texto', self.gf('django.db.models.fields.TextField')(max_length='100')),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True)),
            ('orden', self.gf('django.db.models.fields.IntegerField')()),
            ('tipo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.TipoPregunta'])),
            ('seccion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='preguntas', to=orm['app.Seccion'])),
        ))
        db.send_create_signal('app', ['Pregunta'])

        # Adding model 'ItemPregunta'
        db.create_table('app_itempregunta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('texto', self.gf('django.db.models.fields.CharField')(max_length='50')),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='80', null=True)),
            ('pregunta', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['app.Pregunta'])),
            ('orden', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('app', ['ItemPregunta'])

        # Adding model 'AreaSGA'
        db.create_table('app_areasga', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('siglas', self.gf('django.db.models.fields.CharField')(max_length='10')),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length='256')),
        ))
        db.send_create_signal('app', ['AreaSGA'])

        # Adding model 'PeriodoEvaluacion'
        db.create_table('app_periodoevaluacion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length='300')),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True)),
            ('observaciones', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inicio', self.gf('django.db.models.fields.DateTimeField')()),
            ('fin', self.gf('django.db.models.fields.DateTimeField')()),
            ('periodoAcademico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='periodosEvaluacion', to=orm['app.PeriodoAcademico'])),
        ))
        db.send_create_signal('app', ['PeriodoEvaluacion'])

        # Adding M2M table for field areasSGA on 'PeriodoEvaluacion'
        db.create_table('app_periodoevaluacion_areasSGA', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('periodoevaluacion', models.ForeignKey(orm['app.periodoevaluacion'], null=False)),
            ('areasga', models.ForeignKey(orm['app.areasga'], null=False))
        ))
        db.create_unique('app_periodoevaluacion_areasSGA', ['periodoevaluacion_id', 'areasga_id'])

        # Adding model 'Tabulacion'
        db.create_table('app_tabulacion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='250')),
            ('tipo', self.gf('django.db.models.fields.CharField')(unique=True, max_length='20')),
            ('periodoEvaluacion', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='tabulacion', unique=True, null=True, to=orm['app.PeriodoEvaluacion'])),
        ))
        db.send_create_signal('app', ['Tabulacion'])

        # Adding model 'OfertaAcademicaSGA'
        db.create_table('app_ofertaacademicasga', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idSGA', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, db_column='id_sga', blank=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='100')),
        ))
        db.send_create_signal('app', ['OfertaAcademicaSGA'])

        # Adding model 'PeriodoAcademico'
        db.create_table('app_periodoacademico', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length='50')),
            ('inicio', self.gf('django.db.models.fields.DateField')()),
            ('fin', self.gf('django.db.models.fields.DateField')()),
            ('periodoLectivo', self.gf('django.db.models.fields.CharField')(max_length=100, db_column='periodo_lectivo')),
        ))
        db.send_create_signal('app', ['PeriodoAcademico'])

        # Adding M2M table for field ofertasAcademicasSGA on 'PeriodoAcademico'
        db.create_table('app_periodoacademico_ofertasAcademicasSGA', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('periodoacademico', models.ForeignKey(orm['app.periodoacademico'], null=False)),
            ('ofertaacademicasga', models.ForeignKey(orm['app.ofertaacademicasga'], null=False))
        ))
        db.create_unique('app_periodoacademico_ofertasAcademicasSGA', ['periodoacademico_id', 'ofertaacademicasga_id'])

        # Adding model 'Configuracion'
        db.create_table('app_configuracion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('periodoAcademicoActual', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.PeriodoAcademico'], unique=True, null=True, blank=True)),
            ('periodoEvaluacionActual', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.PeriodoEvaluacion'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('app', ['Configuracion'])

        # Adding model 'Asignatura'
        db.create_table('app_asignatura', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('area', self.gf('django.db.models.fields.CharField')(max_length='20')),
            ('carrera', self.gf('django.db.models.fields.CharField')(max_length='100')),
            ('semestre', self.gf('django.db.models.fields.CharField')(max_length='10')),
            ('paralelo', self.gf('django.db.models.fields.CharField')(max_length='50')),
            ('seccion', self.gf('django.db.models.fields.CharField')(max_length='10')),
            ('nombre', self.gf('django.db.models.fields.TextField')()),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length='15')),
            ('creditos', self.gf('django.db.models.fields.IntegerField')()),
            ('duracion', self.gf('django.db.models.fields.FloatField')()),
            ('inicio', self.gf('django.db.models.fields.DateField')(null=True)),
            ('fin', self.gf('django.db.models.fields.DateField')(null=True)),
            ('idSGA', self.gf('django.db.models.fields.CharField')(max_length='15', db_column='id_sga')),
        ))
        db.send_create_signal('app', ['Asignatura'])

        # Adding model 'EstudiantePeriodoAcademico'
        db.create_table('app_estudianteperiodoacademico', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usuario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='estudiantePeriodosAcademicos', to=orm['app.Usuario'])),
            ('periodoAcademico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='estudiantes', db_column='periodo_academico_id', to=orm['app.PeriodoAcademico'])),
        ))
        db.send_create_signal('app', ['EstudiantePeriodoAcademico'])

        # Adding unique constraint on 'EstudiantePeriodoAcademico', fields ['usuario', 'periodoAcademico']
        db.create_unique('app_estudianteperiodoacademico', ['usuario_id', 'periodo_academico_id'])

        # Adding model 'EstudianteAsignaturaDocente'
        db.create_table('app_estudianteasignaturadocente', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('estudiante', self.gf('django.db.models.fields.related.ForeignKey')(related_name='asignaturasDocentesEstudiante', to=orm['app.EstudiantePeriodoAcademico'])),
            ('asignaturaDocente', self.gf('django.db.models.fields.related.ForeignKey')(related_name='estudiantesAsignaturaDocente', to=orm['app.AsignaturaDocente'])),
            ('matricula', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('estado', self.gf('django.db.models.fields.CharField')(max_length='60', null=True, blank=True)),
        ))
        db.send_create_signal('app', ['EstudianteAsignaturaDocente'])

        # Adding unique constraint on 'EstudianteAsignaturaDocente', fields ['estudiante', 'asignaturaDocente']
        db.create_unique('app_estudianteasignaturadocente', ['estudiante_id', 'asignaturaDocente_id'])

        # Adding model 'AsignaturaDocente'
        db.create_table('app_asignaturadocente', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asignatura', self.gf('django.db.models.fields.related.ForeignKey')(related_name='docentesAsignatura', to=orm['app.Asignatura'])),
            ('docente', self.gf('django.db.models.fields.related.ForeignKey')(related_name='asignaturasDocente', to=orm['app.DocentePeriodoAcademico'])),
        ))
        db.send_create_signal('app', ['AsignaturaDocente'])

        # Adding unique constraint on 'AsignaturaDocente', fields ['docente', 'asignatura']
        db.create_unique('app_asignaturadocente', ['docente_id', 'asignatura_id'])

        # Adding model 'DocentePeriodoAcademico'
        db.create_table('app_docenteperiodoacademico', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usuario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='docentePeriodosAcademicos', to=orm['app.Usuario'])),
            ('periodoAcademico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='docentes', db_column='periodo_academico_id', to=orm['app.PeriodoAcademico'])),
            ('esCoordinador', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('app', ['DocentePeriodoAcademico'])

        # Adding unique constraint on 'DocentePeriodoAcademico', fields ['usuario', 'periodoAcademico']
        db.create_unique('app_docenteperiodoacademico', ['usuario_id', 'periodo_academico_id'])

        # Adding model 'DireccionCarrera'
        db.create_table('app_direccioncarrera', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carrera', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('director', self.gf('django.db.models.fields.related.ForeignKey')(related_name='direcciones', to=orm['app.DocentePeriodoAcademico'])),
        ))
        db.send_create_signal('app', ['DireccionCarrera'])

        # Adding model 'Usuario'
        db.create_table('app_usuario', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('cedula', self.gf('django.db.models.fields.CharField')(unique=True, max_length='15')),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length='100', null=True, blank=True)),
        ))
        db.send_create_signal('app', ['Usuario'])


    def backwards(self, orm):
        # Removing unique constraint on 'DocentePeriodoAcademico', fields ['usuario', 'periodoAcademico']
        db.delete_unique('app_docenteperiodoacademico', ['usuario_id', 'periodo_academico_id'])

        # Removing unique constraint on 'AsignaturaDocente', fields ['docente', 'asignatura']
        db.delete_unique('app_asignaturadocente', ['docente_id', 'asignatura_id'])

        # Removing unique constraint on 'EstudianteAsignaturaDocente', fields ['estudiante', 'asignaturaDocente']
        db.delete_unique('app_estudianteasignaturadocente', ['estudiante_id', 'asignaturaDocente_id'])

        # Removing unique constraint on 'EstudiantePeriodoAcademico', fields ['usuario', 'periodoAcademico']
        db.delete_unique('app_estudianteperiodoacademico', ['usuario_id', 'periodo_academico_id'])

        # Deleting model 'TipoInformante'
        db.delete_table('app_tipoinformante')

        # Deleting model 'InformanteDocente'
        db.delete_table('app_informantedocente')

        # Deleting model 'InformanteEstudiante'
        db.delete_table('app_informanteestudiante')

        # Deleting model 'InformanteEstudianteNovel'
        db.delete_table('app_informanteestudiantenovel')

        # Deleting model 'InformanteDirectivos'
        db.delete_table('app_informantedirectivos')

        # Deleting model 'InformanteInstitutoIdiomas'
        db.delete_table('app_informanteinstitutoidiomas')

        # Deleting model 'InformanteEstudianteMED'
        db.delete_table('app_informanteestudiantemed')

        # Deleting model 'InformanteIdiomasMED'
        db.delete_table('app_informanteidiomasmed')

        # Deleting model 'Cuestionario'
        db.delete_table('app_cuestionario')

        # Deleting model 'Contestacion'
        db.delete_table('app_contestacion')

        # Deleting model 'Evaluacion'
        db.delete_table('app_evaluacion')

        # Deleting model 'Resultados'
        db.delete_table('app_resultados')

        # Deleting model 'TipoPregunta'
        db.delete_table('app_tipopregunta')

        # Deleting model 'SeleccionUnica'
        db.delete_table('app_seleccionunica')

        # Deleting model 'Ensayo'
        db.delete_table('app_ensayo')

        # Deleting model 'Seccion'
        db.delete_table('app_seccion')

        # Deleting model 'Pregunta'
        db.delete_table('app_pregunta')

        # Deleting model 'ItemPregunta'
        db.delete_table('app_itempregunta')

        # Deleting model 'AreaSGA'
        db.delete_table('app_areasga')

        # Deleting model 'PeriodoEvaluacion'
        db.delete_table('app_periodoevaluacion')

        # Removing M2M table for field areasSGA on 'PeriodoEvaluacion'
        db.delete_table('app_periodoevaluacion_areasSGA')

        # Deleting model 'Tabulacion'
        db.delete_table('app_tabulacion')

        # Deleting model 'OfertaAcademicaSGA'
        db.delete_table('app_ofertaacademicasga')

        # Deleting model 'PeriodoAcademico'
        db.delete_table('app_periodoacademico')

        # Removing M2M table for field ofertasAcademicasSGA on 'PeriodoAcademico'
        db.delete_table('app_periodoacademico_ofertasAcademicasSGA')

        # Deleting model 'Configuracion'
        db.delete_table('app_configuracion')

        # Deleting model 'Asignatura'
        db.delete_table('app_asignatura')

        # Deleting model 'EstudiantePeriodoAcademico'
        db.delete_table('app_estudianteperiodoacademico')

        # Deleting model 'EstudianteAsignaturaDocente'
        db.delete_table('app_estudianteasignaturadocente')

        # Deleting model 'AsignaturaDocente'
        db.delete_table('app_asignaturadocente')

        # Deleting model 'DocentePeriodoAcademico'
        db.delete_table('app_docenteperiodoacademico')

        # Deleting model 'DireccionCarrera'
        db.delete_table('app_direccioncarrera')

        # Deleting model 'Usuario'
        db.delete_table('app_usuario')


    models = {
        'app.areasga': {
            'Meta': {'ordering': "['id']", 'object_name': 'AreaSGA'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': "'256'"}),
            'siglas': ('django.db.models.fields.CharField', [], {'max_length': "'10'"})
        },
        'app.asignatura': {
            'Meta': {'object_name': 'Asignatura'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': "'20'"}),
            'carrera': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'creditos': ('django.db.models.fields.IntegerField', [], {}),
            'duracion': ('django.db.models.fields.FloatField', [], {}),
            'fin': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idSGA': ('django.db.models.fields.CharField', [], {'max_length': "'15'", 'db_column': "'id_sga'"}),
            'inicio': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'nombre': ('django.db.models.fields.TextField', [], {}),
            'paralelo': ('django.db.models.fields.CharField', [], {'max_length': "'50'"}),
            'seccion': ('django.db.models.fields.CharField', [], {'max_length': "'10'"}),
            'semestre': ('django.db.models.fields.CharField', [], {'max_length': "'10'"}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': "'15'"})
        },
        'app.asignaturadocente': {
            'Meta': {'unique_together': "(('docente', 'asignatura'),)", 'object_name': 'AsignaturaDocente'},
            'asignatura': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'docentesAsignatura'", 'to': "orm['app.Asignatura']"}),
            'docente': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'asignaturasDocente'", 'to': "orm['app.DocentePeriodoAcademico']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'app.configuracion': {
            'Meta': {'object_name': 'Configuracion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodoAcademicoActual': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.PeriodoAcademico']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'periodoEvaluacionActual': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.PeriodoEvaluacion']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'app.contestacion': {
            'Meta': {'object_name': 'Contestacion'},
            'evaluacion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contestaciones'", 'to': "orm['app.Evaluacion']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pregunta': ('django.db.models.fields.IntegerField', [], {}),
            'respuesta': ('django.db.models.fields.TextField', [], {})
        },
        'app.cuestionario': {
            'Meta': {'object_name': 'Cuestionario'},
            'encabezado': ('django.db.models.fields.TextField', [], {}),
            'fin': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'informante': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.TipoInformante']", 'null': 'True', 'blank': 'True'}),
            'inicio': ('django.db.models.fields.DateTimeField', [], {}),
            'periodoEvaluacion': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cuestionarios'", 'null': 'True', 'to': "orm['app.PeriodoEvaluacion']"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'100'"})
        },
        'app.direccioncarrera': {
            'Meta': {'object_name': 'DireccionCarrera'},
            'carrera': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'director': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'direcciones'", 'to': "orm['app.DocentePeriodoAcademico']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'app.docenteperiodoacademico': {
            'Meta': {'unique_together': "(('usuario', 'periodoAcademico'),)", 'object_name': 'DocentePeriodoAcademico'},
            'esCoordinador': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'docentes'", 'db_column': "'periodo_academico_id'", 'to': "orm['app.PeriodoAcademico']"}),
            'usuario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'docentePeriodosAcademicos'", 'to': "orm['app.Usuario']"})
        },
        'app.ensayo': {
            'Meta': {'object_name': 'Ensayo', '_ormbases': ['app.TipoPregunta']},
            'tipopregunta_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.TipoPregunta']", 'unique': 'True', 'primary_key': 'True'})
        },
        'app.estudianteasignaturadocente': {
            'Meta': {'unique_together': "(('estudiante', 'asignaturaDocente'),)", 'object_name': 'EstudianteAsignaturaDocente'},
            'asignaturaDocente': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'estudiantesAsignaturaDocente'", 'to': "orm['app.AsignaturaDocente']"}),
            'estado': ('django.db.models.fields.CharField', [], {'max_length': "'60'", 'null': 'True', 'blank': 'True'}),
            'estudiante': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'asignaturasDocentesEstudiante'", 'to': "orm['app.EstudiantePeriodoAcademico']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matricula': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'app.estudianteperiodoacademico': {
            'Meta': {'unique_together': "(('usuario', 'periodoAcademico'),)", 'object_name': 'EstudiantePeriodoAcademico'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'estudiantes'", 'db_column': "'periodo_academico_id'", 'to': "orm['app.PeriodoAcademico']"}),
            'usuario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'estudiantePeriodosAcademicos'", 'to': "orm['app.Usuario']"})
        },
        'app.evaluacion': {
            'Meta': {'object_name': 'Evaluacion'},
            'cuestionario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones'", 'to': "orm['app.Cuestionario']"}),
            'estudianteAsignaturaDocente': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones'", 'to': "orm['app.EstudianteAsignaturaDocente']"}),
            'fechaFin': ('django.db.models.fields.DateField', [], {}),
            'fechaInicio': ('django.db.models.fields.DateField', [], {}),
            'horaFin': ('django.db.models.fields.TimeField', [], {}),
            'horaInicio': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'app.informantedirectivos': {
            'Meta': {'object_name': 'InformanteDirectivos', '_ormbases': ['app.TipoInformante']},
            'tipoinformante_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.TipoInformante']", 'unique': 'True', 'primary_key': 'True'})
        },
        'app.informantedocente': {
            'Meta': {'object_name': 'InformanteDocente', '_ormbases': ['app.TipoInformante']},
            'tipoinformante_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.TipoInformante']", 'unique': 'True', 'primary_key': 'True'})
        },
        'app.informanteestudiante': {
            'Meta': {'object_name': 'InformanteEstudiante', '_ormbases': ['app.TipoInformante']},
            'tipoinformante_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.TipoInformante']", 'unique': 'True', 'primary_key': 'True'})
        },
        'app.informanteestudiantemed': {
            'Meta': {'object_name': 'InformanteEstudianteMED', '_ormbases': ['app.TipoInformante']},
            'tipoinformante_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.TipoInformante']", 'unique': 'True', 'primary_key': 'True'})
        },
        'app.informanteestudiantenovel': {
            'Meta': {'object_name': 'InformanteEstudianteNovel', '_ormbases': ['app.TipoInformante']},
            'tipoinformante_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.TipoInformante']", 'unique': 'True', 'primary_key': 'True'})
        },
        'app.informanteidiomasmed': {
            'Meta': {'object_name': 'InformanteIdiomasMED', '_ormbases': ['app.TipoInformante']},
            'tipoinformante_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.TipoInformante']", 'unique': 'True', 'primary_key': 'True'})
        },
        'app.informanteinstitutoidiomas': {
            'Meta': {'object_name': 'InformanteInstitutoIdiomas', '_ormbases': ['app.TipoInformante']},
            'tipoinformante_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.TipoInformante']", 'unique': 'True', 'primary_key': 'True'})
        },
        'app.itempregunta': {
            'Meta': {'ordering': "['orden']", 'object_name': 'ItemPregunta'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'80'", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orden': ('django.db.models.fields.IntegerField', [], {}),
            'pregunta': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['app.Pregunta']"}),
            'texto': ('django.db.models.fields.CharField', [], {'max_length': "'50'"})
        },
        'app.ofertaacademicasga': {
            'Meta': {'object_name': 'OfertaAcademicaSGA'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idSGA': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'db_column': "'id_sga'", 'blank': 'True'})
        },
        'app.periodoacademico': {
            'Meta': {'ordering': "['inicio']", 'object_name': 'PeriodoAcademico'},
            'fin': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': "'50'"}),
            'ofertasAcademicasSGA': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'peridosAcademicos'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['app.OfertaAcademicaSGA']"}),
            'periodoLectivo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'periodo_lectivo'"})
        },
        'app.periodoevaluacion': {
            'Meta': {'ordering': "['inicio']", 'object_name': 'PeriodoEvaluacion'},
            'areasSGA': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'periodosEvaluacion'", 'symmetrical': 'False', 'to': "orm['app.AreaSGA']"}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'fin': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateTimeField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': "'300'"}),
            'observaciones': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'periodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'periodosEvaluacion'", 'to': "orm['app.PeriodoAcademico']"})
        },
        'app.pregunta': {
            'Meta': {'ordering': "['seccion__orden', 'orden']", 'object_name': 'Pregunta'},
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orden': ('django.db.models.fields.IntegerField', [], {}),
            'seccion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'preguntas'", 'to': "orm['app.Seccion']"}),
            'texto': ('django.db.models.fields.TextField', [], {'max_length': "'100'"}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.TipoPregunta']"})
        },
        'app.resultados': {
            'Meta': {'object_name': 'Resultados'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'app.seccion': {
            'Meta': {'ordering': "['orden']", 'object_name': 'Seccion'},
            'cuestionario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'secciones'", 'to': "orm['app.Cuestionario']"}),
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orden': ('django.db.models.fields.IntegerField', [], {}),
            'seccionPadre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subsecciones'", 'null': 'True', 'db_column': "'seccion_padre_id'", 'to': "orm['app.Seccion']"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'50'"})
        },
        'app.seleccionunica': {
            'Meta': {'object_name': 'SeleccionUnica', '_ormbases': ['app.TipoPregunta']},
            'tipopregunta_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['app.TipoPregunta']", 'unique': 'True', 'primary_key': 'True'})
        },
        'app.tabulacion': {
            'Meta': {'object_name': 'Tabulacion'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'250'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodoEvaluacion': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'tabulacion'", 'unique': 'True', 'null': 'True', 'to': "orm['app.PeriodoEvaluacion']"}),
            'tipo': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'20'"})
        },
        'app.tipoinformante': {
            'Meta': {'object_name': 'TipoInformante'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'20'"})
        },
        'app.tipopregunta': {
            'Meta': {'object_name': 'TipoPregunta'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'20'"})
        },
        'app.usuario': {
            'Meta': {'object_name': 'Usuario', '_ormbases': ['auth.User']},
            'cedula': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'15'"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app']