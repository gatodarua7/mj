# Generated by Django 3.1.5 on 2021-05-10 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0007_auto_20210505_0920'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='internovulgosthroughmodel',
            name='ativo',
        ),
        migrations.RemoveField(
            model_name='vulgo',
            name='ativo',
        ),
        migrations.RemoveField(
            model_name='vulgo',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='vulgo',
            name='delete_at',
        ),
        migrations.RemoveField(
            model_name='vulgo',
            name='excluido',
        ),
        migrations.RemoveField(
            model_name='vulgo',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='vulgo',
            name='usuario_cadastro',
        ),
        migrations.RemoveField(
            model_name='vulgo',
            name='usuario_edicao',
        ),
        migrations.RemoveField(
            model_name='vulgo',
            name='usuario_exclusao',
        ),
    ]
