# Generated by Django 3.1.5 on 2021-08-02 22:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visitante', '0004_auto_20210730_1955'),
    ]

    operations = [
        migrations.RenameField(
            model_name='anuencia',
            old_name='grau_parentesco',
            new_name='tipo_vinculo',
        ),
    ]
