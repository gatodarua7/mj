from django.db import models
from django.core.validators import RegexValidator
from cadastros.models import Foto, Genero
from social.models import (
    Raca,
    GrauDeInstrucao,
    Religiao,
    OrientacaoSexual,
    EstadoCivil,
    NecessidadeEspecial,
    Profissao,
)
from localizacao.models import Pais, Estado, Cidade


class DadosPessoais(models.Model):
    nome = models.CharField(max_length=150)
    nome_social = models.CharField(max_length=150, null=True, blank=True)
    genero = models.ForeignKey(
        Genero,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="genero_%(app_label)s_%(class)s_related",
    )
    nacionalidade = models.ManyToManyField(
        Pais,
        blank=True,
        default=None,
        related_name="nacionalidade_%(app_label)s_%(class)s_related",
    )
    estado = models.ForeignKey(
        Estado,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="estado_%(app_label)s_%(class)s_related",
    )
    naturalidade = models.ForeignKey(
        Cidade,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="naturalidade_%(app_label)s_%(class)s_related",
    )
    cpf = models.CharField(
        max_length=14,
        validators=[
            RegexValidator(
                regex=r"[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}\-?[0-9]{2}",
                message="CPF inválido",
            )
        ],
    )
    foto = models.ForeignKey(
        Foto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="foto%(app_label)s_%(class)s_related",
    )
    nome_mae = models.CharField(max_length=150, null=True, blank=True)
    nome_pai = models.CharField(max_length=150, null=True, blank=True)
    mae_falecido = models.BooleanField(default=False)
    mae_nao_declarado = models.BooleanField(default=False)
    pai_falecido = models.BooleanField(default=False)
    pai_nao_declarado = models.BooleanField(default=False)
    grau_instrucao = models.ForeignKey(
        GrauDeInstrucao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="grau_instrucao_%(app_label)s_%(class)s_related",
    )
    raca = models.ForeignKey(
        Raca,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="raca_%(app_label)s_%(class)s_related",
    )
    orientacao_sexual = models.ForeignKey(
        OrientacaoSexual,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orientacao_sexual_%(app_label)s_%(class)s_related",
    )
    religiao = models.ForeignKey(
        Religiao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="religiao_%(app_label)s_%(class)s_related",
    )
    necessidade_especial = models.ManyToManyField(
        NecessidadeEspecial,
        blank=True,
        related_name="necessidades_%(app_label)s_%(class)s_related",
    )
    estado_civil = models.ForeignKey(
        EstadoCivil,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="estado_civil_%(app_label)s_%(class)s_related",
    )

    class Meta:
        abstract = True
