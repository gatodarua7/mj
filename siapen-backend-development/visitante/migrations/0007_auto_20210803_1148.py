# Generated by Django 3.1.5 on 2021-08-03 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitante', '0006_auto_20210803_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitante',
            name='situacao',
            field=models.CharField(blank=True, choices=[('ANALISE_DIRETORIA', 'ANÁLISE DIRETORIA'), ('ANALISE_INTELIGENCIA', 'ANÁLISE DE INTELIGÊNCIA'), ('ASSISTENCIA_SOCIAL', 'ASSISTÊNCIA SOCIAL'), ('DEFERIDO', 'DEFERIDO'), ('INDEFERIDO', 'INDEFERIDO'), ('INICIADO', 'INICIADO'), ('RECURSO', 'RECURSO'), ('RECURSO_EM_ANALISE', 'RECURSO - ANÁLISE DIRETORIA'), ('RECURSO_DEFERIDO', 'RECURSO DEFERIDO'), ('RECURSO_INDEFERIDO', 'RECURSO INDEFERIDO'), ('SOLICITANTE_INFORMADO', 'Visitante informado')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='visitantemovimentacao',
            name='situacao',
            field=models.CharField(choices=[('ANALISE_DIRETORIA', 'ANÁLISE DIRETORIA'), ('ANALISE_INTELIGENCIA', 'ANÁLISE DE INTELIGÊNCIA'), ('ASSISTENCIA_SOCIAL', 'ASSISTÊNCIA SOCIAL'), ('DEFERIDO', 'DEFERIDO'), ('INDEFERIDO', 'INDEFERIDO'), ('INICIADO', 'INICIADO'), ('RECURSO', 'RECURSO'), ('RECURSO_EM_ANALISE', 'RECURSO - ANÁLISE DIRETORIA'), ('RECURSO_DEFERIDO', 'RECURSO DEFERIDO'), ('RECURSO_INDEFERIDO', 'RECURSO INDEFERIDO'), ('SOLICITANTE_INFORMADO', 'Visitante informado')], max_length=25),
        ),
    ]
