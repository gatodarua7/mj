from django.db import models
from cadastros.models import OrgaoExpedidor, Documentos
from comum.models import Telefone, Endereco
from core.models import BaseModel
from social.models import Profissao
from pessoas.models import DadosPessoais
from vinculos.models import TipoVinculo
from comum.models import Endereco, Telefone
from cadastros.models import Foto
from ordered_model.models import OrderedModel
from django.utils.translation import gettext_lazy as _
import uuid


class AbaCaracteristicas(models.Model):
    class Cutis(models.TextChoices):
        BRANCA = "BRANCA", _("Branca")
        AMARELA = "AMARELA", _("Amarela")
        PARDA = "PARDA", _("Parda")
        PRETA = "PRETA", _("Preta")

    class CorCabelo(models.TextChoices):
        PRETO = ("PRETO", _("Preto"))
        CASTANHO = ("CASTANHO", _("Castanho"))
        RUIVO = ("RUIVO", _("Ruivo"))
        LOIRO = ("LOIRO", _("Loiro"))
        GRISALHO = ("GRISALHO", _("Grisalho"))
        BRANCO = "BRANCO", _("Branco")

    class TipoCabelo(models.TextChoices):
        LISO = ("LISO", _("Liso"))
        CRESPO = ("CRESPO", _("Crespo"))
        ONDULADO = ("ONDULADO", _("Ondulado"))
        CARAPINHA = "CARAPINHA", _("Carapinha")

    class TipoRosto(models.TextChoices):
        ACHATADO = ("ACHATADO", _("Achatado"))
        COMPRIDO = ("COMPRIDO", _("Comprido"))
        OVALADO = ("OVALADO", _("Ovalado"))
        QUADRADO = ("QUADRADO", _("Quadrado"))
        REDONDO = "REDONDO", _("Redondo")

    class TipoTesta(models.TextChoices):
        ALTA = ("ALTA", _("Alta"))
        COM_ENTRADAS = ("COM_ENTRADAS", _("Com entradas"))
        CURTA = "CURTA", _("Curta")

    class Sobrancelhas(models.TextChoices):
        APARADAS = ("APARADAS", _("Aparadas"))
        FINAS = ("FINAS", _("Finas"))
        GROSSAS = ("GROSSAS", _("Grossas"))
        PINTADAS = ("PINTADAS", _("Pintadas"))
        SEPARADAS = ("SEPARADAS", _("Separadas"))
        UNIDAS = "UNIDAS", _("Unidas")

    class TipoOlhos(models.TextChoices):
        FUNDOS = ("FUNDOS", _("Fundos"))
        GRANDES = ("GRANDES", _("Grandes"))
        ORIENTAIS = ("ORIENTAIS", _("Orientais"))
        PEQUENOS = ("PEQUENOS", _("Pequenos"))
        SALTADOS = "SALTADOS", _("Saltados")

    class CorOlhos(models.TextChoices):
        PRETOS = ("PRETOS", _("Pretos"))
        CASTANHO = ("CASTANHO", _("Castanho"))
        AZUIS = ("AZUIS", _("Azuis"))
        VERDES = ("VERDES", _("Verdes"))
        DUAS_CORES = ("DUAS_CORES", _("Duas cores"))
        INDEFINIDOS_CLAROS = ("INDEFINIDOS_CLAROS", _("Indefinidos claros"))
        INDEFINIDOS_ESCUROS = "INDEFINIDOS_ESCUROS", _("Indefinidos escuros")

    class Nariz(models.TextChoices):
        ACHATADO = ("ACHATADO", _("Achatado"))
        ADUNCO = ("ADUNCO", _("Adunco"))
        AFILADO = ("AFILADO", _("Afilado"))
        ARREBITADO = ("ARREBITADO", _("Arrebitado"))
        GRANDE = ("GRANDE", _("Grande"))
        MEDIO = ("MEDIO", _("Médio"))
        PEQUENO = "PEQUENO", _("Pequeno")

    class Orelhas(models.TextChoices):
        GRANDES = ("GRANDES", _("Grandes"))
        MEDIAS = ("MEDIAS", _("Médias"))
        PEQUENAS = ("PEQUENAS", _("Pequenas"))
        LOBULOS_FECHADOS = ("LOBULOS_FECHADOS", _("Lóbulos fechados"))
        LOBULOS_ABERTOS = "LOBULOS_ABERTOS", _("Lóbulos abertos")

    class Labios(models.TextChoices):
        FINOS = ("FINOS", _("Finos"))
        MEDIOS = ("MEDIOS", _("Médios"))
        GROSSOS = ("GROSSOS", _("Grossos"))
        LEPORINOS = "LEPORINOS", _("Leporinos")

    class Compleicao(models.TextChoices):
        GORDA = ("GORDA", _("Gorda"))
        MEDIA = ("MEDIA", _("Média"))
        MAGRA = ("MAGRA", _("Magra"))
        MUSCULOSA = ("MUSCULOSA", _("Musculosa"))
        RAQUITICA = "RAQUITICA", _("Raquítica")

    caracteristicas_cutis = models.CharField(max_length=20, choices=Cutis.choices)
    caracteristicas_cor_cabelo = models.CharField(
        max_length=20, choices=CorCabelo.choices
    )
    caracteristicas_tipo_cabelo = models.CharField(
        max_length=20, choices=TipoCabelo.choices
    )
    caracteristicas_tipo_rosto = models.CharField(
        max_length=20, choices=TipoRosto.choices
    )
    caracteristicas_tipo_testa = models.CharField(
        max_length=20, choices=TipoTesta.choices
    )
    caracteristicas_tipo_olhos = models.CharField(
        max_length=20, choices=TipoOlhos.choices
    )
    caracteristicas_cor_olhos = models.CharField(
        max_length=20, choices=CorOlhos.choices
    )
    caracteristicas_nariz = models.CharField(max_length=20, choices=Nariz.choices)
    caracteristicas_labios = models.CharField(max_length=20, choices=Labios.choices)
    caracteristicas_compleicao = models.CharField(
        max_length=20, choices=Compleicao.choices
    )
    caracteristicas_sobrancelhas = models.CharField(
        max_length=20, choices=Sobrancelhas.choices
    )
    caracteristicas_orelhas = models.CharField(max_length=20, choices=Orelhas.choices)

    class Meta:
        abstract = True


class Vulgo(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    nome = models.CharField(max_length=150)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Interno(BaseModel, AbaCaracteristicas, DadosPessoais):
    data_nascimento = models.DateField()
    profissao = models.ForeignKey(
        Profissao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="profissao_interno_related",
    )
    documentos = models.ManyToManyField(Documentos, blank=True)
    vulgo = models.ManyToManyField(Vulgo, through="InternoVulgosThroughModel")

    class Meta:
        order_with_respect_to = "id"

    def __str__(self):
        return self.nome


class InternoVulgosThroughModel(OrderedModel):
    interno = models.ForeignKey(Interno, on_delete=models.PROTECT)
    vulgo = models.ForeignKey(Vulgo, on_delete=models.PROTECT)
    order_with_respect_to = "vulgo"

    def __str__(self):
        return "{0} - {1}".format(self.interno, self.vulgo)


class Rg(BaseModel):
    numero = models.CharField(max_length=15)
    orgao_expedidor = models.ForeignKey(
        OrgaoExpedidor, on_delete=models.PROTECT, related_name="orgao_expedidor_interno"
    )
    interno = models.ForeignKey(
        Interno,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="rg_interno",
    )

    class Meta:
        verbose_name = u"RG"
        verbose_name_plural = u"RG"

    def __str__(self):
        return self.numero


class OutroNome(BaseModel):
    interno = models.ForeignKey(
        Interno,
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


class Contatos(BaseModel):
    interno = models.ForeignKey(
        Interno,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="interno_contato_related",
    )
    nome = models.CharField(max_length=100)
    tipo_vinculo = models.ForeignKey(
        TipoVinculo,
        on_delete=models.PROTECT,
        related_name="tipo_vinculo_contato_related",
    )
    enderecos = models.ManyToManyField(
        Endereco, blank=True, related_name="endereco_contato_related"
    )
    telefones = models.ManyToManyField(
        Telefone, blank=True, related_name="telefone_contato_related"
    )

    def __str__(self):
        return self.nome


class SinaisParticulares(BaseModel):
    class TipoSinal(models.TextChoices):
        SINAL = "SINAL", _("Sinal Particular")
        TATUAGEM = "TATUAGEM", _("Tatuagem")

    interno = models.ForeignKey(
        Interno,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="interno_sinais_related",
    )
    foto = models.ForeignKey(
        Foto, on_delete=models.PROTECT, related_name="foto_sinais_related"
    )
    area = models.CharField(max_length=50)
    position_x = models.FloatField()
    position_y = models.FloatField()
    tipo = models.CharField(max_length=20, choices=TipoSinal.choices)
    descricao = models.TextField(max_length=200)
    motivo_ativacao = models.TextField(
        max_length=200, default=None, null=True, blank=True
    )
