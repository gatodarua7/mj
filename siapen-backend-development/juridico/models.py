from django.db import models
from core.models import BaseModel
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Normas(models.TextChoices):
    EMENDA_CONSTITUICAO = "EMENDA_CONSTITUICAO", _("Emenda à Constituição")
    LEI_COMPLEMENTAR = "LEI_COMPLEMENTAR", _("Lei Complementar")
    LEI_ORDINARIA = "LEI_ORDINARIA", _("Lei Ordinária")
    LEI_DELEGADA = "LEI_DELEGADA", _("Lei Delegada")
    MEDIDA_PROVISORIA = "MEDIDA_PROVISORIA", _("Medida Provisória")
    DECRETO_LEGISLATIVO = "DECRETO_LEGISLATIVO", _("Decreto Legislativo")
    RESOLUCAO = "RESOLUCAO", _("Resolução")


class TituloLei(BaseModel):
    nome = models.CharField(max_length=255)
    norma_juridica = models.CharField(max_length=50, choices=Normas.choices)
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
        related_name="Ativacao_titulo_lei_related",
        default=None,
        blank=True,
        null=True,
    )
    usuario_inativacao = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="Inativação_titulo_lei_related",
        default=None,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = u"Título da Lei"
        verbose_name_plural = u"Títulos da Lei"


class NormasJuridicas(BaseModel):
    descricao = models.TextField()
    titulo = models.ForeignKey(TituloLei, on_delete=models.PROTECT)
    norma_juridica = models.CharField(max_length=100, choices=Normas.choices)
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
        related_name="Ativacao_normas_juridicas_related",
        default=None,
        blank=True,
        null=True,
    )
    usuario_inativacao = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="Inativação_normas_juridicas_related",
        default=None,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.norma_juridica

    class Meta:
        verbose_name = u"Norma Jurídica"
        verbose_name_plural = u"Normas Jurídicas"
