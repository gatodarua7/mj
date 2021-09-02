# Generated by Django 3.1.5 on 2021-07-28 12:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0020_auto_20210727_1405'),
        ('vinculos', '0002_remove_vinculo_vinculo'),
        ('cadastros', '0003_auto_20210428_1656'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('visitante', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoAnuencia',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('arquivo_temp', models.FileField(upload_to='documentos_anuencia')),
                ('arquivo', models.BinaryField(blank=True, default=None, null=True)),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tipo_documentos_anuencia', to='cadastros.tipodocumento')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedvisitante_documentoanuencia_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletevisitante_documentoanuencia_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'DocumentoAnuencia',
                'verbose_name_plural': 'DocumentosAnuencia',
            },
        ),
        migrations.CreateModel(
            name='Anuencia',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('data_declaracao', models.DateField()),
                ('observacao', models.CharField(blank=True, max_length=500, null=True)),
                ('declaracao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='documento_anuencia_related', to='visitante.documentoanuencia')),
                ('grau_parentesco', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tipo_vinculo_anuencia_related', to='vinculos.tipovinculo')),
                ('interno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='interno_visitante_related', to='pessoas.interno')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedvisitante_anuencia_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletevisitante_anuencia_related', to=settings.AUTH_USER_MODEL)),
                ('visitante', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='visitante_related', to='visitante.visitante')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]