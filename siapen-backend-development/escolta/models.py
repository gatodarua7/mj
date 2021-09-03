from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from pessoas.servidor.models import Servidor

from movimentacao.models import PedidoInclusao, TipoEscolta


class TipoAeronave(models.TextChoices):
    COMERCIAL = "COMERCIAL", _("Comercial")
    INSTITUCIONAL = "INSTITUCIONAL", _("Institucional")


class Instituicao(models.TextChoices):
    FAB = "FAB", _("Força Aérea Brasileira")
    PF = "PF", _("Polícia Federal")
    PRF = "PRF", _("Polícia Rodoviária Federal")
    PC = "PC", _("Polícia Civil")
    OUTROS = "OUTROS", _("Outros")


class ResponsavelEscolta(models.TextChoices):
    DEPEN = "DEPEN", _("DEPEN")
    ESTADO = "ESTADO", _("ESTADO")


class FasesEscolta(models.TextChoices):
    AGENDADA = "AGENDADA", _("Agendada")
    INICIADA_TERRESTRE = "INICIADA_TERRESTRE", _("Iniciada Escolta Terrestre")
    INICIADA_AEREA = "INICIADA_AEREA", _("Iniciada Escolta Aérea")
    EM_TRANSITO = "EM_TRANSITO", _("Em Trânsito")
    FINALIZADA = "FINALIZADA", _("Finalizada")


class Escoltas(BaseModel):
    nome_missao = models.CharField(max_length=150, default=None, blank=True, null=True)
    numero_sei = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"\d{5}\.\d{6}\/\d{4}\-\d{2}", message="Nº SEI inválido"
            )
        ],
    )
    numero_documento_sei = models.CharField(max_length=10)
    ordem_missao = models.CharField(max_length=50)
    responsavel = models.CharField(max_length=20, choices=ResponsavelEscolta.choices)
    data_inicio_aerea = models.DateField(default=None, null=True, blank=True)
    hora_inicio_aerea = models.TimeField(default=None, null=True, blank=True)
    data_fim_aerea = models.DateField(default=None, null=True, blank=True)
    hora_fim_aerea = models.TimeField(default=None, null=True, blank=True)
    descricao_aerea = models.TextField(
        max_length=500, default=None, null=True, blank=True
    )
    fase_escolta_aerea = models.CharField(
        max_length=20, choices=FasesEscolta.choices, default=None, null=True, blank=True
    )
    servidores_escolta_aerea = models.ManyToManyField(
        Servidor,
        blank=True,
        default=None,
        related_name="servidores_escolta_aerea_related",
    )
    data_inicio_terrestre = models.DateField(default=None, null=True, blank=True)
    hora_inicio_terrestre = models.TimeField(default=None, null=True, blank=True)
    data_fim_terrestre = models.DateField(default=None, null=True, blank=True)
    hora_fim_terrestre = models.TimeField(default=None, null=True, blank=True)
    descricao_terrestre = models.TextField(
        max_length=500, default=None, null=True, blank=True
    )
    servidores_escolta_terrestre = models.ManyToManyField(
        Servidor,
        blank=True,
        default=None,
        related_name="servidores_escolta_terrestre_related",
    )
    fase_escolta_terrestre = models.CharField(
        max_length=20, choices=FasesEscolta.choices, default=None, null=True, blank=True
    )
    pedidos_inclusao = models.ManyToManyField(
        PedidoInclusao, related_name="pedido_inclusao_related"
    )
    tipo_aeronave = models.CharField(
        max_length=20, choices=TipoAeronave.choices, default=None, null=True, blank=True
    )
    instituicao = models.CharField(
        max_length=20, choices=Instituicao.choices, default=None, null=True, blank=True
    )
    numero_escolta = models.CharField(max_length=20)
    tipo_escolta = models.CharField(
        max_length=20, choices=TipoEscolta.choices, default=None, null=True, blank=True
    )


class VoosEscolta(models.Model):
    escolta = models.ForeignKey(Escoltas, on_delete=models.PROTECT)
    voo = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    usuario_cadastro = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="usuario_voo_escolta_related"
    )

    def __str__(self):
        return self.voo
