from django.contrib.auth.models import User
from social.models import NecessidadeEspecial
from localizacao.models import Cidade, Estado, Pais
from comum.models import Endereco, Telefone
from django.db import models
from django.core.validators import RegexValidator
from cadastros.models import Foto, Genero, OrgaoExpedidor
from core.models import BaseModel


class OAB(BaseModel):
    numero = models.CharField(max_length=15)
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        related_name="estado_oab_%(app_label)s_%(class)s_related",
    )

    class Meta:
        verbose_name = u"OAB"
        verbose_name_plural = u"OAB"

    def __str__(self):
        return self.numero


class Advogado(BaseModel):
    class Situacao(models.TextChoices):
        PENDENTE = "PENDENTE", ("Pendente")
        COMPLETO = "COMPLETO", ("Completo")

    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField()
    genero = models.ForeignKey(
        Genero,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="genero_%(app_label)s_%(class)s_related",
    )
    nacionalidade = models.ManyToManyField(
        Pais,
        default=None,
        related_name="nacionalidade_advogado_%(app_label)s_%(class)s_related",
    )
    naturalidade = models.ForeignKey(
        Cidade,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="naturalidade_advogado_%(app_label)s_%(class)s_related",
    )
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="estado_advogado_%(app_label)s_%(class)s_related",
    )
    enderecos = models.ManyToManyField(
        Endereco, blank=True, related_name="endereco_related"
    )
    telefones = models.ManyToManyField(
        Telefone, blank=True, related_name="telefone_related"
    )
    situacao = models.BooleanField(default=False)
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
    necessidade_especial = models.ManyToManyField(
        NecessidadeEspecial,
        blank=True,
        related_name="necessidades_advogado%(app_label)s_%(class)s_related",
    )
    motivo_ativacao = models.TextField(
        max_length=200, default=None, null=True, blank=True
    )
    motivo_inativacao = models.TextField(
        max_length=200, default=None, null=True, blank=True
    )
    data_ativacao = models.DateTimeField(default=None, blank=True, null=True)
    data_inativacao = models.DateTimeField(default=None, blank=True, null=True)
    usuario_ativacao = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="ativacao_advogado_related",
        default=None,
        blank=True,
        null=True,
    )
    usuario_inativacao = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="inativacao_advogado_related",
        default=None,
        blank=True,
        null=True,
    )

    oabs = models.ManyToManyField(
        OAB, default=None, related_name="oab_advogado_%(app_label)s_%(class)s_related"
    )


class EmailAdvogado(BaseModel):
    email = models.EmailField(max_length=150, null=True, blank=True)
    advogado = models.ForeignKey(
        Advogado,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="email_advogado",
    )

    class Meta:
        verbose_name = u"Email"
        verbose_name_plural = u"Emails"

    def __str__(self):
        return self.email


class RgAdvogado(BaseModel):
    numero = models.CharField(max_length=15)
    orgao_expedidor = models.ForeignKey(
        OrgaoExpedidor,
        on_delete=models.PROTECT,
        related_name="orgao_expedidor_advogado",
    )
    advogado = models.ForeignKey(
        Advogado,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="rg_advogado",
    )

    class Meta:
        verbose_name = u"RG Advogado"
        verbose_name_plural = u"RG Advogado"

    def __str__(self):
        return self.numero
