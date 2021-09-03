from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel

from cadastros.models import Pessoa, Foto
from core.models import BaseModel

from localizacao.models import Estado, Pais, Cidade

from cadastros.models import RegimePrisional, Foto, Genero

from pessoas.interno.models import Vulgo

from social.models import NecessidadeEspecial

from juridico.models import NormasJuridicas, TituloLei, Normas

from prisional.models import Unidade


class TipoEscolta(models.TextChoices):
    INCLUSAO = "INCLUSAO", _("INCLUSÃO")


class GrupoFases(models.TextChoices):
    EMERGENCIAL = "EMERGENCIAL", _("Emergêncial")
    DEFINITIVO = "DEFINITIVO", _("Definitivo")


class Fases(models.TextChoices):
    ULTIMA_FASE = "ULTIMA_FASE", _("Última fase")
    CGIN = "CGIN", _("Análise CGIN")
    ARQUIVAR = "ARQUIVAR", _("Arquivar")
    DESARQUIVAR = "DESARQUIVAR", _("Desarquivar")
    REMETIDO = "REMETIDO", _("Remetido os autos ao Juízo corregedor")
    RECEBIDO = "RECEBIDO", _("Recebido os autos do Juízo corregedor")


class FaseFinal(models.TextChoices):
    DEFERIDO = "DEFERIDO", _("Finalizado pelo Juízo corregedor com parecer favorável para inclusão.")
    INDEFERIDO = "INDEFERIDO", _("Finalizado pelo Juízo corregedor com parecer desfavorável para inclusão.")


class FasesPedido(BaseModel):
    nome = models.CharField(max_length=150)
    cor = models.CharField(max_length=10)
    ordem = models.IntegerField()
    grupo = models.CharField(max_length=20, choices=GrupoFases.choices)
    descricao = models.TextField()
    fase_inicial = models.BooleanField(default=False)
    fase = models.CharField(max_length=20, choices=Fases.choices, default=None, null=True, blank=True)
    ultima_fase = models.CharField(max_length=20, choices=FaseFinal.choices, default=None, null=True, blank=True)
    motivo_ativacao = models.TextField(max_length=200, default=None, null=True, blank=True)
    motivo_inativacao = models.TextField(max_length=200, default=None, null=True, blank=True)
    data_ativacao = models.DateTimeField(default=None, blank=True, null=True)
    data_inativacao = models.DateTimeField(default=None, blank=True, null=True)
    usuario_ativacao = models.ForeignKey(User, on_delete=models.PROTECT,
                                        related_name="Ativacao_fases_related",
                                        default=None, blank=True, null=True)
    usuario_inativacao = models.ForeignKey(User, on_delete=models.PROTECT,
                                        related_name="Inativação_fases_related",
                                        default=None, blank=True, null=True)


class PedidoInclusao(BaseModel):
    """Model para armazenar informações do pedido de inclusão"""
    class Interesse(models.TextChoices):
        PRESO = "PRESO", _("Preso")
        SEGURANCA_PUBLICA = "SEGURANCA_PUBLICA", _("SEGURANÇA PÚBLICA")

    nome = models.CharField(max_length=150)
    nome_social = models.CharField(max_length=150, null=True, blank=True)
    genero = models.ForeignKey(Genero, on_delete=models.PROTECT, null=True, blank=True,
        related_name="genero_%(app_label)s_%(class)s_related")
    nacionalidade = models.ManyToManyField(Pais, blank=True, default=None,
        related_name="nacionalidade_%(app_label)s_%(class)s_related")
    estado = models.ForeignKey(Estado, blank=True, null=True, on_delete=models.PROTECT,
        related_name="estado_%(app_label)s_%(class)s_related")
    naturalidade = models.ForeignKey(
        Cidade, on_delete=models.PROTECT, null=True, blank=True,
        related_name="naturalidade_%(app_label)s_%(class)s_related",
    )
    cpf = models.CharField(
        max_length=14,
        validators=[
            RegexValidator(
                regex=r"[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}\-?[0-9]{2}",
                message="CPF inválido",
            ),
        ], null=True, blank=True
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
    necessidade_especial = models.ManyToManyField(NecessidadeEspecial, blank=True,
        related_name="necessidades_%(app_label)s_%(class)s_related")
    data_nascimento = models.DateField()
    vulgo = models.ManyToManyField(Vulgo, through='VulgosThroughModel')
    preso_extraditando = models.BooleanField(default=False)
    aguardando_escolta = models.BooleanField(default=False)
    regime_prisional = models.ForeignKey(RegimePrisional, on_delete=models.PROTECT, null=True, blank=True)
    interesse = models.CharField(max_length=20, choices=Interesse.choices)
    tipo_inclusao = models.CharField(max_length=20, choices=GrupoFases.choices)
    tipo_escolta = models.CharField(max_length=20, choices=TipoEscolta.choices, default=None, null=True, blank=True)
    numero_sei = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"\d{5}\.\d{6}\/\d{4}\-\d{2}",
                message="Nº SEI inválido",
            ),
        ],
    )
    data_pedido_sei = models.DateField()
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    fase_pedido = models.ForeignKey(FasesPedido, on_delete=models.PROTECT, null=True, blank=True)
    motivo_exclusao = models.TextField(max_length=200, default=None, null=True, blank=True)
    estado_solicitante = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name="estado_solicitante_%(app_label)s_%(class)s_related")
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.nome


class VulgosThroughModel(OrderedModel):
    pedido_inclusao = models.ForeignKey(PedidoInclusao, on_delete=models.PROTECT)
    vulgo = models.ForeignKey(Vulgo, on_delete=models.PROTECT)
    order_with_respect_to = 'vulgo'

    def __str__(self):
        return f"{self.pedido_inclusao} - {self.vulgo}"


class PedidoInclusaoOutroNome(BaseModel):
    pedido_inclusao = models.ForeignKey(
        PedidoInclusao,
        on_delete=models.PROTECT,
        related_name="models_outro_nome",
        related_query_name="model_outro_nome",
    )
    nome = models.CharField(max_length=150)

    class Meta:
        verbose_name = u"Outro Nome"
        verbose_name_plural = u"Outros Nomes"

    def __str__(self):
        return self.nome


class PedidoInclusaoMotivos(OrderedModel):
    norma_juridica = models.CharField(max_length=50, choices=Normas.choices)
    titulo = models.ForeignKey(TituloLei, on_delete=models.PROTECT)
    pedido_inclusao = models.ForeignKey(PedidoInclusao, on_delete=models.PROTECT)
    descricao = models.ManyToManyField(NormasJuridicas, through='NormasJuridicasMotivosThroughModel')
    order_with_respect_to = 'titulo'

    def __str__(self):
        return f"{self.pedido_inclusao} - {self.get_norma_juridica_display()}"


class NormasJuridicasMotivosThroughModel(OrderedModel):
    motivo = models.ForeignKey(PedidoInclusaoMotivos, on_delete=models.PROTECT)
    norma = models.ForeignKey(NormasJuridicas, on_delete=models.PROTECT)
    order_with_respect_to = 'motivo'

    def __str__(self):
        return f"{self.motivo} - {self.norma}"


class PedidoInclusaoMovimentacao(models.Model):
    pedido_inclusao = models.ForeignKey(PedidoInclusao, on_delete=models.PROTECT)
    fase_pedido = models.ForeignKey(FasesPedido, on_delete=models.PROTECT)
    motivo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT,
                                         related_name="usuario_movimentacao_related")

    def __str__(self):
        return self.fase_pedido.nome


class AnalisePedido(BaseModel):
    class Posicionamento(models.TextChoices):
        FAVORAVEL = "FAVORAVEL", _("Favorável")
        DESFAVORAVEL = "DESFAVORAVEL", _("Desfavorável")

    pedido_inclusao = models.ForeignKey(PedidoInclusao, on_delete=models.PROTECT)
    penitenciaria = models.ForeignKey(Unidade, on_delete=models.PROTECT)
    posicionamento = models.CharField(max_length=20, choices=Posicionamento.choices)
    parecer = models.TextField()


    def __str__(self):
        return self.parecer
