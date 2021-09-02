# Generated by Django 3.1.5 on 2021-08-18 13:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('visitante', '0018_auto_20210810_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManifestacaoDiretoria',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('parecer', models.TextField()),
                ('documentos', models.ManyToManyField(blank=True, to='visitante.DocumentosVisitante')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedvisitante_manifestacaodiretoria_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletevisitante_manifestacaodiretoria_related', to=settings.AUTH_USER_MODEL)),
                ('visitante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='visitante.visitante')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]