# Generated by Django 3.1.5 on 2021-06-11 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0012_auto_20210609_1815'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oab',
            name='advogado',
        ),
        migrations.AddField(
            model_name='advogado',
            name='oabs',
            field=models.ManyToManyField(blank=True, default=None, related_name='oab_advogado_pessoas_advogado_related', to='pessoas.OAB'),
        ),
    ]
