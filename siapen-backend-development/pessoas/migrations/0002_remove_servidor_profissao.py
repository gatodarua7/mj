# Generated by Django 3.1.5 on 2021-04-09 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servidor',
            name='profissao',
        ),
    ]
