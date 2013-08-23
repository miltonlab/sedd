# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Configuracion'
        db.create_table(u'app_configuracion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('periodoAcademicoActual', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.PeriodoAcademico'], unique=True, null=True, blank=True)),
            ('periodoEvaluacionActual', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.PeriodoEvaluacion'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['Configuracion'])

        # Adding model 'OfertaAcademicaSGA'
        db.create_table(u'app_ofertaacademicasga', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idSGA', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, db_column='id_sga', blank=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='100')),
        ))
        db.send_create_signal(u'app', ['OfertaAcademicaSGA'])

        # Adding model 'PeriodoAcademico'
        db.create_table(u'app_periodoacademico', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length='50')),
            ('inicio', self.gf('django.db.models.fields.DateField')()),
            ('fin', self.gf('django.db.models.fields.DateField')()),
            ('periodoLectivo', self.gf('django.db.models.fields.CharField')(max_length=100, db_column='periodo_lectivo')),
        ))
        db.send_create_signal(u'app', ['PeriodoAcademico'])

        # Adding M2M table for field ofertasAcademicasSGA on 'PeriodoAcademico'
        db.create_table(u'app_periodoacademico_ofertasAcademicasSGA', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('periodoacademico', models.ForeignKey(orm[u'app.periodoacademico'], null=False)),
            ('ofertaacademicasga', models.ForeignKey(orm[u'app.ofertaacademicasga'], null=False))
        ))
        db.create_unique(u'app_periodoacademico_ofertasAcademicasSGA', ['periodoacademico_id', 'ofertaacademicasga_id'])

        # Adding model 'Asignatura'
        db.create_table(u'app_asignatura', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('area', self.gf('django.db.models.fields.CharField')(max_length='20')),
            ('carrera', self.gf('django.db.models.fields.CharField')(max_length='100')),
            ('semestre', self.gf('django.db.models.fields.CharField')(max_length='10')),
            ('paralelo', self.gf('django.db.models.fields.CharField')(max_length='50')),
            ('seccion', self.gf('django.db.models.fields.CharField')(max_length='10')),
            ('modalidad', self.gf('django.db.models.fields.CharField')(max_length='20')),
            ('nombre', self.gf('django.db.models.fields.TextField')()),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length='15')),
            ('creditos', self.gf('django.db.models.fields.IntegerField')()),
            ('duracion', self.gf('django.db.models.fields.FloatField')()),
            ('inicio', self.gf('django.db.models.fields.DateField')(null=True)),
            ('fin', self.gf('django.db.models.fields.DateField')(null=True)),
            ('idSGA', self.gf('django.db.models.fields.CharField')(max_length='15', db_column='id_sga')),
            ('periodoAcademico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='asignaturas', db_column='periodo_academico_id', to=orm['app.PeriodoAcademico'])),
        ))
        db.send_create_signal(u'app', ['Asignatura'])

        # Adding model 'EstudiantePeriodoAcademico'
        db.create_table(u'app_estudianteperiodoacademico', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usuario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='estudiantePeriodosAcademicos', to=orm['app.Usuario'])),
            ('periodoAcademico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='estudiantes', db_column='periodo_academico_id', to=orm['app.PeriodoAcademico'])),
        ))
        db.send_create_signal(u'app', ['EstudiantePeriodoAcademico'])

        # Adding unique constraint on 'EstudiantePeriodoAcademico', fields ['usuario', 'periodoAcademico']
        db.create_unique(u'app_estudianteperiodoacademico', ['usuario_id', 'periodo_academico_id'])

        # Adding model 'EstudianteAsignaturaDocente'
        db.create_table(u'app_estudianteasignaturadocente', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('estudiante', self.gf('django.db.models.fields.related.ForeignKey')(related_name='asignaturasDocentesEstudiante', to=orm['app.EstudiantePeriodoAcademico'])),
            ('asignaturaDocente', self.gf('django.db.models.fields.related.ForeignKey')(related_name='estudiantesAsignaturaDocente', to=orm['app.AsignaturaDocente'])),
            ('matricula', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('estado', self.gf('django.db.models.fields.CharField')(max_length='60', null=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['EstudianteAsignaturaDocente'])

        # Adding unique constraint on 'EstudianteAsignaturaDocente', fields ['estudiante', 'asignaturaDocente']
        db.create_unique(u'app_estudianteasignaturadocente', ['estudiante_id', 'asignaturaDocente_id'])

        # Adding model 'AsignaturaDocente'
        db.create_table(u'app_asignaturadocente', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asignatura', self.gf('django.db.models.fields.related.ForeignKey')(related_name='docentesAsignatura', to=orm['app.Asignatura'])),
            ('docente', self.gf('django.db.models.fields.related.ForeignKey')(related_name='asignaturasDocente', to=orm['app.DocentePeriodoAcademico'])),
        ))
        db.send_create_signal(u'app', ['AsignaturaDocente'])

        # Adding unique constraint on 'AsignaturaDocente', fields ['docente', 'asignatura']
        db.create_unique(u'app_asignaturadocente', ['docente_id', 'asignatura_id'])

        # Adding model 'DocentePeriodoAcademico'
        db.create_table(u'app_docenteperiodoacademico', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usuario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='docentePeriodosAcademicos', to=orm['app.Usuario'])),
            ('periodoAcademico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='docentes', db_column='periodo_academico_id', to=orm['app.PeriodoAcademico'])),
            ('carrera', self.gf('django.db.models.fields.CharField')(max_length='500', null=True, blank=True)),
            ('parAcademico', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'app', ['DocentePeriodoAcademico'])

        # Adding unique constraint on 'DocentePeriodoAcademico', fields ['usuario', 'periodoAcademico']
        db.create_unique(u'app_docenteperiodoacademico', ['usuario_id', 'periodo_academico_id'])

        # Adding model 'DireccionCarrera'
        db.create_table(u'app_direccioncarrera', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carrera', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('director', self.gf('django.db.models.fields.related.ForeignKey')(related_name='direcciones', to=orm['app.DocentePeriodoAcademico'])),
        ))
        db.send_create_signal(u'app', ['DireccionCarrera'])

        # Adding model 'TipoInformante'
        db.create_table(u'app_tipoinformante', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(unique=True, max_length='50')),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='200')),
        ))
        db.send_create_signal(u'app', ['TipoInformante'])

        # Adding model 'Cuestionario'
        db.create_table(u'app_cuestionario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(default='Cuestionario Sin Nombre', max_length='150')),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length='255')),
            ('encabezado', self.gf('django.db.models.fields.TextField')()),
            ('inicio', self.gf('django.db.models.fields.DateTimeField')()),
            ('fin', self.gf('django.db.models.fields.DateTimeField')()),
            ('preguntas_obligatorias', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('informante', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.TipoInformante'])),
            ('peso', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('periodoEvaluacion', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='cuestionarios', null=True, to=orm['app.PeriodoEvaluacion'])),
        ))
        db.send_create_signal(u'app', ['Cuestionario'])

        # Adding model 'Contestacion'
        db.create_table(u'app_contestacion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pregunta', self.gf('django.db.models.fields.IntegerField')()),
            ('respuesta', self.gf('django.db.models.fields.TextField')()),
            ('observaciones', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('evaluacion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contestaciones', to=orm['app.Evaluacion'])),
        ))
        db.send_create_signal(u'app', ['Contestacion'])

        # Adding model 'Evaluacion'
        db.create_table(u'app_evaluacion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fechaInicio', self.gf('django.db.models.fields.DateField')()),
            ('fechaFin', self.gf('django.db.models.fields.DateField')()),
            ('horaInicio', self.gf('django.db.models.fields.TimeField')()),
            ('horaFin', self.gf('django.db.models.fields.TimeField')()),
            ('cuestionario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evaluaciones', to=orm['app.Cuestionario'])),
            ('estudianteAsignaturaDocente', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='evaluaciones', null=True, to=orm['app.EstudianteAsignaturaDocente'])),
            ('docentePeriodoAcademico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evaluaciones', null=True, to=orm['app.DocentePeriodoAcademico'])),
            ('parAcademico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evaluaciones_par_academico', null=True, to=orm['app.DocentePeriodoAcademico'])),
            ('directorCarrera', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evaluaciones_director', null=True, to=orm['app.DocentePeriodoAcademico'])),
            ('carreraDirector', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['Evaluacion'])

        # Adding model 'Resultados'
        db.create_table(u'app_resultados', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'app', ['Resultados'])

        # Adding model 'TipoPregunta'
        db.create_table(u'app_tipopregunta', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(unique=True, max_length='20')),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='100')),
        ))
        db.send_create_signal(u'app', ['TipoPregunta'])

        # Adding model 'SeleccionUnica'
        db.create_table(u'app_seleccionunica', (
            (u'tipopregunta_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoPregunta'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'app', ['SeleccionUnica'])

        # Adding model 'Ensayo'
        db.create_table(u'app_ensayo', (
            (u'tipopregunta_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['app.TipoPregunta'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'app', ['Ensayo'])

        # Adding model 'Seccion'
        db.create_table(u'app_seccion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(default=u'Secci\xf3n de Cuestionario Sin Nombre', max_length='150')),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length='200')),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('orden', self.gf('django.db.models.fields.IntegerField')()),
            ('codigo', self.gf('django.db.models.fields.CharField')(max_length='20', null=True, blank=True)),
            ('ponderacion', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('superseccion', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subsecciones', null=True, db_column='superseccion_id', to=orm['app.Seccion'])),
            ('cuestionario', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='secciones', null=True, to=orm['app.Cuestionario'])),
        ))
        db.send_create_signal(u'app', ['Seccion'])

        # Adding model 'Pregunta'
        db.create_table(u'app_pregunta', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('codigo', self.gf('django.db.models.fields.CharField')(max_length='20', null=True, blank=True)),
            ('texto', self.gf('django.db.models.fields.TextField')()),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('observaciones', self.gf('django.db.models.fields.CharField')(max_length='70', null=True, blank=True)),
            ('orden', self.gf('django.db.models.fields.IntegerField')()),
            ('tipo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.TipoPregunta'])),
            ('seccion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='preguntas', to=orm['app.Seccion'])),
        ))
        db.send_create_signal(u'app', ['Pregunta'])

        # Adding model 'ItemPregunta'
        db.create_table(u'app_itempregunta', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('texto', self.gf('django.db.models.fields.CharField')(max_length='50')),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='70', null=True, blank=True)),
            ('pregunta', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['app.Pregunta'])),
            ('orden', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'app', ['ItemPregunta'])

        # Adding model 'AreaSGA'
        db.create_table(u'app_areasga', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('siglas', self.gf('django.db.models.fields.CharField')(max_length='10')),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length='256')),
        ))
        db.send_create_signal(u'app', ['AreaSGA'])

        # Adding model 'PeriodoEvaluacion'
        db.create_table(u'app_periodoevaluacion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length='100')),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length='300')),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True)),
            ('observaciones', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inicio', self.gf('django.db.models.fields.DateTimeField')()),
            ('fin', self.gf('django.db.models.fields.DateTimeField')()),
            ('periodoAcademico', self.gf('django.db.models.fields.related.ForeignKey')(related_name='periodosEvaluacion', to=orm['app.PeriodoAcademico'])),
        ))
        db.send_create_signal(u'app', ['PeriodoEvaluacion'])

        # Adding M2M table for field areasSGA on 'PeriodoEvaluacion'
        db.create_table(u'app_periodoevaluacion_areasSGA', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('periodoevaluacion', models.ForeignKey(orm[u'app.periodoevaluacion'], null=False)),
            ('areasga', models.ForeignKey(orm[u'app.areasga'], null=False))
        ))
        db.create_unique(u'app_periodoevaluacion_areasSGA', ['periodoevaluacion_id', 'areasga_id'])

        # Adding model 'Tabulacion'
        db.create_table(u'app_tabulacion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length='250')),
            ('tipo', self.gf('django.db.models.fields.CharField')(unique=True, max_length='20')),
            ('periodoEvaluacion', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='tabulacion', unique=True, null=True, to=orm['app.PeriodoEvaluacion'])),
        ))
        db.send_create_signal(u'app', ['Tabulacion'])

        # Adding model 'Usuario'
        db.create_table(u'app_usuario', (
            (u'user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('cedula', self.gf('django.db.models.fields.CharField')(unique=True, max_length='15')),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length='100', null=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['Usuario'])


    def backwards(self, orm):
        # Removing unique constraint on 'DocentePeriodoAcademico', fields ['usuario', 'periodoAcademico']
        db.delete_unique(u'app_docenteperiodoacademico', ['usuario_id', 'periodo_academico_id'])

        # Removing unique constraint on 'AsignaturaDocente', fields ['docente', 'asignatura']
        db.delete_unique(u'app_asignaturadocente', ['docente_id', 'asignatura_id'])

        # Removing unique constraint on 'EstudianteAsignaturaDocente', fields ['estudiante', 'asignaturaDocente']
        db.delete_unique(u'app_estudianteasignaturadocente', ['estudiante_id', 'asignaturaDocente_id'])

        # Removing unique constraint on 'EstudiantePeriodoAcademico', fields ['usuario', 'periodoAcademico']
        db.delete_unique(u'app_estudianteperiodoacademico', ['usuario_id', 'periodo_academico_id'])

        # Deleting model 'Configuracion'
        db.delete_table(u'app_configuracion')

        # Deleting model 'OfertaAcademicaSGA'
        db.delete_table(u'app_ofertaacademicasga')

        # Deleting model 'PeriodoAcademico'
        db.delete_table(u'app_periodoacademico')

        # Removing M2M table for field ofertasAcademicasSGA on 'PeriodoAcademico'
        db.delete_table('app_periodoacademico_ofertasAcademicasSGA')

        # Deleting model 'Asignatura'
        db.delete_table(u'app_asignatura')

        # Deleting model 'EstudiantePeriodoAcademico'
        db.delete_table(u'app_estudianteperiodoacademico')

        # Deleting model 'EstudianteAsignaturaDocente'
        db.delete_table(u'app_estudianteasignaturadocente')

        # Deleting model 'AsignaturaDocente'
        db.delete_table(u'app_asignaturadocente')

        # Deleting model 'DocentePeriodoAcademico'
        db.delete_table(u'app_docenteperiodoacademico')

        # Deleting model 'DireccionCarrera'
        db.delete_table(u'app_direccioncarrera')

        # Deleting model 'TipoInformante'
        db.delete_table(u'app_tipoinformante')

        # Deleting model 'Cuestionario'
        db.delete_table(u'app_cuestionario')

        # Deleting model 'Contestacion'
        db.delete_table(u'app_contestacion')

        # Deleting model 'Evaluacion'
        db.delete_table(u'app_evaluacion')

        # Deleting model 'Resultados'
        db.delete_table(u'app_resultados')

        # Deleting model 'TipoPregunta'
        db.delete_table(u'app_tipopregunta')

        # Deleting model 'SeleccionUnica'
        db.delete_table(u'app_seleccionunica')

        # Deleting model 'Ensayo'
        db.delete_table(u'app_ensayo')

        # Deleting model 'Seccion'
        db.delete_table(u'app_seccion')

        # Deleting model 'Pregunta'
        db.delete_table(u'app_pregunta')

        # Deleting model 'ItemPregunta'
        db.delete_table(u'app_itempregunta')

        # Deleting model 'AreaSGA'
        db.delete_table(u'app_areasga')

        # Deleting model 'PeriodoEvaluacion'
        db.delete_table(u'app_periodoevaluacion')

        # Removing M2M table for field areasSGA on 'PeriodoEvaluacion'
        db.delete_table('app_periodoevaluacion_areasSGA')

        # Deleting model 'Tabulacion'
        db.delete_table(u'app_tabulacion')

        # Deleting model 'Usuario'
        db.delete_table(u'app_usuario')


    models = {
        u'app.areasga': {
            'Meta': {'ordering': "['id']", 'object_name': 'AreaSGA'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': "'256'"}),
            'siglas': ('django.db.models.fields.CharField', [], {'max_length': "'10'"})
        },
        u'app.asignatura': {
            'Meta': {'object_name': 'Asignatura'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': "'20'"}),
            'carrera': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'creditos': ('django.db.models.fields.IntegerField', [], {}),
            'duracion': ('django.db.models.fields.FloatField', [], {}),
            'fin': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idSGA': ('django.db.models.fields.CharField', [], {'max_length': "'15'", 'db_column': "'id_sga'"}),
            'inicio': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'modalidad': ('django.db.models.fields.CharField', [], {'max_length': "'20'"}),
            'nombre': ('django.db.models.fields.TextField', [], {}),
            'paralelo': ('django.db.models.fields.CharField', [], {'max_length': "'50'"}),
            'periodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'asignaturas'", 'db_column': "'periodo_academico_id'", 'to': u"orm['app.PeriodoAcademico']"}),
            'seccion': ('django.db.models.fields.CharField', [], {'max_length': "'10'"}),
            'semestre': ('django.db.models.fields.CharField', [], {'max_length': "'10'"}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': "'15'"})
        },
        u'app.asignaturadocente': {
            'Meta': {'unique_together': "(('docente', 'asignatura'),)", 'object_name': 'AsignaturaDocente'},
            'asignatura': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'docentesAsignatura'", 'to': u"orm['app.Asignatura']"}),
            'docente': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'asignaturasDocente'", 'to': u"orm['app.DocentePeriodoAcademico']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app.configuracion': {
            'Meta': {'object_name': 'Configuracion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodoAcademicoActual': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['app.PeriodoAcademico']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'periodoEvaluacionActual': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['app.PeriodoEvaluacion']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'app.contestacion': {
            'Meta': {'ordering': "['pregunta']", 'object_name': 'Contestacion'},
            'evaluacion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contestaciones'", 'to': u"orm['app.Evaluacion']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observaciones': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pregunta': ('django.db.models.fields.IntegerField', [], {}),
            'respuesta': ('django.db.models.fields.TextField', [], {})
        },
        u'app.cuestionario': {
            'Meta': {'object_name': 'Cuestionario'},
            'encabezado': ('django.db.models.fields.TextField', [], {}),
            'fin': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'informante': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.TipoInformante']"}),
            'inicio': ('django.db.models.fields.DateTimeField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'default': "'Cuestionario Sin Nombre'", 'max_length': "'150'"}),
            'periodoEvaluacion': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cuestionarios'", 'null': 'True', 'to': u"orm['app.PeriodoEvaluacion']"}),
            'peso': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'preguntas_obligatorias': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'255'"})
        },
        u'app.direccioncarrera': {
            'Meta': {'ordering': "['carrera']", 'object_name': 'DireccionCarrera'},
            'carrera': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'director': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'direcciones'", 'to': u"orm['app.DocentePeriodoAcademico']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app.docenteperiodoacademico': {
            'Meta': {'unique_together': "(('usuario', 'periodoAcademico'),)", 'object_name': 'DocentePeriodoAcademico'},
            'carrera': ('django.db.models.fields.CharField', [], {'max_length': "'500'", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parAcademico': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'periodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'docentes'", 'db_column': "'periodo_academico_id'", 'to': u"orm['app.PeriodoAcademico']"}),
            'usuario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'docentePeriodosAcademicos'", 'to': u"orm['app.Usuario']"})
        },
        u'app.ensayo': {
            'Meta': {'object_name': 'Ensayo', '_ormbases': [u'app.TipoPregunta']},
            u'tipopregunta_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['app.TipoPregunta']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'app.estudianteasignaturadocente': {
            'Meta': {'unique_together': "(('estudiante', 'asignaturaDocente'),)", 'object_name': 'EstudianteAsignaturaDocente'},
            'asignaturaDocente': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'estudiantesAsignaturaDocente'", 'to': u"orm['app.AsignaturaDocente']"}),
            'estado': ('django.db.models.fields.CharField', [], {'max_length': "'60'", 'null': 'True', 'blank': 'True'}),
            'estudiante': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'asignaturasDocentesEstudiante'", 'to': u"orm['app.EstudiantePeriodoAcademico']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matricula': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'app.estudianteperiodoacademico': {
            'Meta': {'unique_together': "(('usuario', 'periodoAcademico'),)", 'object_name': 'EstudiantePeriodoAcademico'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'estudiantes'", 'db_column': "'periodo_academico_id'", 'to': u"orm['app.PeriodoAcademico']"}),
            'usuario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'estudiantePeriodosAcademicos'", 'to': u"orm['app.Usuario']"})
        },
        u'app.evaluacion': {
            'Meta': {'object_name': 'Evaluacion'},
            'carreraDirector': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'cuestionario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones'", 'to': u"orm['app.Cuestionario']"}),
            'directorCarrera': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones_director'", 'null': 'True', 'to': u"orm['app.DocentePeriodoAcademico']"}),
            'docentePeriodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones'", 'null': 'True', 'to': u"orm['app.DocentePeriodoAcademico']"}),
            'estudianteAsignaturaDocente': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'evaluaciones'", 'null': 'True', 'to': u"orm['app.EstudianteAsignaturaDocente']"}),
            'fechaFin': ('django.db.models.fields.DateField', [], {}),
            'fechaInicio': ('django.db.models.fields.DateField', [], {}),
            'horaFin': ('django.db.models.fields.TimeField', [], {}),
            'horaInicio': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones_par_academico'", 'null': 'True', 'to': u"orm['app.DocentePeriodoAcademico']"})
        },
        u'app.itempregunta': {
            'Meta': {'ordering': "['-orden']", 'object_name': 'ItemPregunta'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'70'", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orden': ('django.db.models.fields.IntegerField', [], {}),
            'pregunta': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['app.Pregunta']"}),
            'texto': ('django.db.models.fields.CharField', [], {'max_length': "'50'"})
        },
        u'app.ofertaacademicasga': {
            'Meta': {'object_name': 'OfertaAcademicaSGA'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idSGA': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'db_column': "'id_sga'", 'blank': 'True'})
        },
        u'app.periodoacademico': {
            'Meta': {'ordering': "['inicio']", 'object_name': 'PeriodoAcademico'},
            'fin': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': "'50'"}),
            'ofertasAcademicasSGA': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'peridosAcademicos'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['app.OfertaAcademicaSGA']"}),
            'periodoLectivo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'periodo_lectivo'"})
        },
        u'app.periodoevaluacion': {
            'Meta': {'ordering': "['inicio', 'fin']", 'object_name': 'PeriodoEvaluacion'},
            'areasSGA': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'periodosEvaluacion'", 'symmetrical': 'False', 'to': u"orm['app.AreaSGA']"}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'fin': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateTimeField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'observaciones': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'periodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'periodosEvaluacion'", 'to': u"orm['app.PeriodoAcademico']"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'300'"})
        },
        u'app.pregunta': {
            'Meta': {'ordering': "['seccion__orden', 'orden']", 'object_name': 'Pregunta'},
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': "'20'", 'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observaciones': ('django.db.models.fields.CharField', [], {'max_length': "'70'", 'null': 'True', 'blank': 'True'}),
            'orden': ('django.db.models.fields.IntegerField', [], {}),
            'seccion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'preguntas'", 'to': u"orm['app.Seccion']"}),
            'texto': ('django.db.models.fields.TextField', [], {}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.TipoPregunta']"})
        },
        u'app.resultados': {
            'Meta': {'object_name': 'Resultados'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app.seccion': {
            'Meta': {'ordering': "['orden']", 'object_name': 'Seccion'},
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': "'20'", 'null': 'True', 'blank': 'True'}),
            'cuestionario': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'secciones'", 'null': 'True', 'to': u"orm['app.Cuestionario']"}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'default': "u'Secci\\xf3n de Cuestionario Sin Nombre'", 'max_length': "'150'"}),
            'orden': ('django.db.models.fields.IntegerField', [], {}),
            'ponderacion': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'superseccion': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subsecciones'", 'null': 'True', 'db_column': "'superseccion_id'", 'to': u"orm['app.Seccion']"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'200'"})
        },
        u'app.seleccionunica': {
            'Meta': {'object_name': 'SeleccionUnica', '_ormbases': [u'app.TipoPregunta']},
            u'tipopregunta_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['app.TipoPregunta']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'app.tabulacion': {
            'Meta': {'object_name': 'Tabulacion'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'250'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodoEvaluacion': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'tabulacion'", 'unique': 'True', 'null': 'True', 'to': u"orm['app.PeriodoEvaluacion']"}),
            'tipo': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'20'"})
        },
        u'app.tipoinformante': {
            'Meta': {'ordering': "['descripcion']", 'object_name': 'TipoInformante'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'200'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'50'"})
        },
        u'app.tipopregunta': {
            'Meta': {'object_name': 'TipoPregunta'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'20'"})
        },
        u'app.usuario': {
            'Meta': {'object_name': 'Usuario', '_ormbases': [u'auth.User']},
            'cedula': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'15'"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app']