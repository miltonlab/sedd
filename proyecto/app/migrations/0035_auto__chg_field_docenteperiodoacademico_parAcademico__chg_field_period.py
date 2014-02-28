# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'DocentePeriodoAcademico.parAcademico'
        db.alter_column('app_docenteperiodoacademico', 'parAcademico', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'PeriodoEvaluacion.contabilizar_extras'
        db.alter_column('app_periodoevaluacion', 'contabilizar_extras', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Removing unique constraint on 'ExtensionPeriodoEvaluacion', fields ['secuencia']
        db.delete_unique('app_extensionperiodoevaluacion', ['secuencia'])

        # Changing field 'Cuestionario.preguntas_obligatorias'
        db.alter_column('app_cuestionario', 'preguntas_obligatorias', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Cuestionario.fuente_verificacion'
        db.alter_column('app_cuestionario', 'fuente_verificacion', self.gf('django.db.models.fields.BooleanField')(blank=True))
    
    
    def backwards(self, orm):
        
        # Changing field 'DocentePeriodoAcademico.parAcademico'
        db.alter_column('app_docenteperiodoacademico', 'parAcademico', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'PeriodoEvaluacion.contabilizar_extras'
        db.alter_column('app_periodoevaluacion', 'contabilizar_extras', self.gf('django.db.models.fields.BooleanField')())

        # Adding unique constraint on 'ExtensionPeriodoEvaluacion', fields ['secuencia']
        db.create_unique('app_extensionperiodoevaluacion', ['secuencia'])

        # Changing field 'Cuestionario.preguntas_obligatorias'
        db.alter_column('app_cuestionario', 'preguntas_obligatorias', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Cuestionario.fuente_verificacion'
        db.alter_column('app_cuestionario', 'fuente_verificacion', self.gf('django.db.models.fields.BooleanField')())
    
    
    models = {
        'app.areasga': {
            'Meta': {'object_name': 'AreaSGA'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': "'256'"}),
            'siglas': ('django.db.models.fields.CharField', [], {'max_length': "'10'"})
        },
        'app.asignatura': {
            'Meta': {'object_name': 'Asignatura'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': "'20'"}),
            'carrera': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'carrera_senescyt': ('django.db.models.fields.CharField', [], {'default': "'0000'", 'max_length': "'10'"}),
            'creditos': ('django.db.models.fields.IntegerField', [], {}),
            'duracion': ('django.db.models.fields.FloatField', [], {}),
            'fin': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idSGA': ('django.db.models.fields.CharField', [], {'max_length': "'15'", 'db_column': "'id_sga'"}),
            'inicio': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'modalidad': ('django.db.models.fields.CharField', [], {'max_length': "'20'"}),
            'nombre': ('django.db.models.fields.TextField', [], {}),
            'paralelo': ('django.db.models.fields.CharField', [], {'max_length': "'50'"}),
            'periodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'asignaturas'", 'db_column': "'periodo_academico_id'", 'to': "orm['app.PeriodoAcademico']"}),
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
            'observaciones': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pregunta': ('django.db.models.fields.IntegerField', [], {}),
            'respuesta': ('django.db.models.fields.TextField', [], {})
        },
        'app.cuestionario': {
            'Meta': {'object_name': 'Cuestionario'},
            'encabezado': ('django.db.models.fields.TextField', [], {}),
            'fin': ('django.db.models.fields.DateTimeField', [], {}),
            'fuente_verificacion': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'informante': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.TipoInformante']", 'null': 'True'}),
            'inicio': ('django.db.models.fields.DateTimeField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'default': "'Cuestionario Sin Nombre'", 'max_length': "'150'"}),
            'periodoEvaluacion': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cuestionarios'", 'null': 'True', 'to': "orm['app.PeriodoEvaluacion']"}),
            'peso': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'preguntas_obligatorias': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'255'"})
        },
        'app.direccioncarrera': {
            'Meta': {'object_name': 'DireccionCarrera'},
            'carrera': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'director': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'direcciones'", 'null': 'True', 'to': "orm['app.DocentePeriodoAcademico']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'app.docenteperiodoacademico': {
            'Meta': {'unique_together': "(('usuario', 'periodoAcademico'),)", 'object_name': 'DocentePeriodoAcademico'},
            'carrera': ('django.db.models.fields.CharField', [], {'max_length': "'500'", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parAcademico': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
            'carreraDirector': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'cuestionario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones'", 'to': "orm['app.Cuestionario']"}),
            'directorCarrera': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones_director'", 'null': 'True', 'to': "orm['app.DocentePeriodoAcademico']"}),
            'docentePeriodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones'", 'null': 'True', 'to': "orm['app.DocentePeriodoAcademico']"}),
            'estudianteAsignaturaDocente': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'evaluaciones'", 'null': 'True', 'to': "orm['app.EstudianteAsignaturaDocente']"}),
            'fechaFin': ('django.db.models.fields.DateField', [], {}),
            'fechaInicio': ('django.db.models.fields.DateField', [], {}),
            'horaFin': ('django.db.models.fields.TimeField', [], {}),
            'horaInicio': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluaciones_par_academico'", 'null': 'True', 'to': "orm['app.DocentePeriodoAcademico']"})
        },
        'app.extensionperiodoevaluacion': {
            'Meta': {'object_name': 'ExtensionPeriodoEvaluacion'},
            'fin': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateTimeField', [], {}),
            'observaciones': ('django.db.models.fields.TextField', [], {}),
            'periodoEvaluacion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'extensiones'", 'to': "orm['app.PeriodoEvaluacion']"}),
            'secuencia': ('django.db.models.fields.IntegerField', [], {})
        },
        'app.itempregunta': {
            'Meta': {'object_name': 'ItemPregunta'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'70'", 'null': 'True', 'blank': 'True'}),
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
            'Meta': {'object_name': 'PeriodoAcademico'},
            'fin': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': "'50'"}),
            'ofertasAcademicasSGA': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'peridosAcademicos'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['app.OfertaAcademicaSGA']"}),
            'periodoLectivo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'periodo_lectivo'"})
        },
        'app.periodoevaluacion': {
            'Meta': {'object_name': 'PeriodoEvaluacion'},
            'areasSGA': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'periodosEvaluacion'", 'symmetrical': 'False', 'to': "orm['app.AreaSGA']"}),
            'contabilizar_extras': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'fin': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateTimeField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'observaciones': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'periodoAcademico': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'periodosEvaluacion'", 'to': "orm['app.PeriodoAcademico']"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'300'"})
        },
        'app.pregunta': {
            'Meta': {'object_name': 'Pregunta'},
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': "'20'", 'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observaciones': ('django.db.models.fields.CharField', [], {'max_length': "'70'", 'null': 'True', 'blank': 'True'}),
            'orden': ('django.db.models.fields.IntegerField', [], {}),
            'seccion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'preguntas'", 'to': "orm['app.Seccion']"}),
            'texto': ('django.db.models.fields.TextField', [], {}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.TipoPregunta']"})
        },
        'app.resultados': {
            'Meta': {'object_name': 'Resultados'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'app.seccion': {
            'Meta': {'object_name': 'Seccion'},
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': "'20'", 'null': 'True', 'blank': 'True'}),
            'cuestionario': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'secciones'", 'null': 'True', 'to': "orm['app.Cuestionario']"}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'default': "u'Secci\\xf3n de Cuestionario Sin Nombre'", 'max_length': "'150'"}),
            'orden': ('django.db.models.fields.IntegerField', [], {}),
            'ponderacion': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'superseccion': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subsecciones'", 'null': 'True', 'db_column': "'superseccion_id'", 'to': "orm['app.Seccion']"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': "'200'"})
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
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': "'20'"})
        },
        'app.tipoinformante': {
            'Meta': {'object_name': 'TipoInformante'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': "'200'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'50'"})
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
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['app']
