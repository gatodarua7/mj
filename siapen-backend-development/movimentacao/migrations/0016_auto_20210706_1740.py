# Generated by Django 3.1.5 on 2021-07-06 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movimentacao', '0015_merge_20210706_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedidoinclusao',
            name='aguardando_escolta',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='pedidoinclusao',
            name='tipo_escolta',
            field=models.CharField(blank=True, choices=[('INCLUSAO', 'INCLUSÃO')], default=None, max_length=20, null=True),
        ),
    ]
