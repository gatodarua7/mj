# Generated by Django 3.1.5 on 2021-04-08 17:14

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cadastros', '0001_initial'),
        ('prisional', '0001_initial'),
        ('localizacao', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AutorizadorInclusao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=250, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='FaltaDisciplinar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=250)),
                ('tempo_reabilitacao', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('tipo', models.CharField(choices=[('LEV', 'Leve'), ('LEM', 'Leve/Média'), ('MED', 'Média'), ('MEG', 'Média/Grave'), ('GRA', 'Grave')], max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='ProcedimentoDisciplinar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=80)),
                ('situacao', models.CharField(choices=[('AND', 'Em andamento'), ('CON', 'Concluído'), ('ARQ', 'Arquivado'), ('REC', 'Recurso')], max_length=3)),
                ('data_fato', models.DateField()),
                ('data_portaria', models.DateField(blank=True, null=True)),
                ('data_decisao', models.DateField(blank=True, null=True)),
                ('data_inicio_isolamento_preventivo', models.DateField(blank=True, null=True)),
                ('qtd_dias_isolamento_preventivo', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('homologado', models.BooleanField(default=False)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('data_cadastro', models.DateTimeField(auto_now=True)),
                ('unidade_cadastradora', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='prisional.unidade')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProcedimentoInternoFalta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('situacao', models.CharField(choices=[('ARQ', 'Arquivado'), ('ABS', 'Absolvido'), ('CON', 'Condenado'), ('AND', 'Em Andamento'), ('EXT', 'Extinto')], max_length=3)),
                ('tipo_sancao', models.CharField(choices=[('ADV', 'Advertência Verbal'), ('ISO', 'Isolamento Celular'), ('REP', 'Repreensão'), ('SUS', 'Suspensão ou Restrição de Direitos')], max_length=3)),
                ('data_inicio_isolamento', models.DateField(blank=True, null=True)),
                ('qtd_dias_isolamento', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('classificacao_conduta', models.CharField(choices=[('OTI', 'Ótima'), ('BOA', 'Boa'), ('REG', 'Regular'), ('MAA', 'Má')], max_length=3)),
                ('data_reabilitacao', models.DateField(blank=True, null=True)),
                ('recurso', models.CharField(choices=[('AGU', 'Aguardando Decisão'), ('IMP', 'Improcedente'), ('PAR', 'Parcialmente Procedente'), ('PRO', 'Procedente')], max_length=3)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('falta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juridico.faltadisciplinar')),
                ('interno', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cadastros.pessoa')),
                ('procedimento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juridico.procedimentodisciplinar')),
            ],
        ),
        migrations.CreateModel(
            name='PedidoInclusao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_solicitacao', models.DateField(blank=True)),
                ('motivo_solicitacao', models.TextField(blank=True, null=True)),
                ('emergencial', models.BooleanField(default=False)),
                ('data_inicial', models.DateField(blank='True', null=True)),
                ('n_autos', models.CharField(blank=True, max_length=120, null=True)),
                ('n_sei', models.CharField(blank=True, max_length=80, null=True)),
                ('n_oficio_renovacao', models.CharField(blank=True, max_length=120, null=True)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('ANAL', 'Em análise'), ('DEF', 'Deferido'), ('IND', 'Indeferido'), ('INC', 'Incluído'), ('CONA', 'Conflito de Competência - Em andamento'), ('CONF', 'Conflito de Competência - Finalizado')], max_length=4)),
                ('motivo_indeferimento', models.TextField(blank=True, null=True)),
                ('prazo', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(365)])),
                ('data_cadastro', models.DateTimeField(auto_now=True)),
                ('autorizador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='juridico.autorizadorinclusao')),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cadastros.pessoa')),
                ('solicitante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='localizacao.estado')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
