# Generated by Django 3.1.5 on 2021-05-06 15:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("movimentacao", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FasesPedido",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("ativo", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "updated_at",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
                (
                    "delete_at",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
                ("excluido", models.BooleanField(default=False)),
                ("nome", models.CharField(max_length=150)),
                ("cor", models.CharField(max_length=10)),
                ("ordem", models.IntegerField()),
                (
                    "grupo",
                    models.CharField(
                        choices=[
                            ("EMERGENCIAL", "Emergêncial"),
                            ("DEFINITIVO", "Definitivo"),
                        ],
                        max_length=20,
                    ),
                ),
                ("descricao", models.TextField()),
                ("fase_inicial", models.BooleanField(default=False)),
                ("ultima_fase", models.BooleanField(default=False)),
                (
                    "usuario_cadastro",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "usuario_edicao",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="updatedmovimentacao_fasespedido_related",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "usuario_exclusao",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="deletemovimentacao_fasespedido_related",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        )
    ]
