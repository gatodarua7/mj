from configuracao.settings import MEDIA_ROOT
from django.contrib.auth.models import User
from util.upload import diretorio_upload
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from social.models import Profissao
from cadastros.models import Foto, OrgaoExpedidor, TipoDocumento, Documentos
from comum.models import Endereco, Telefone
from pessoas.models import DadosPessoais
from pessoas.interno.models import Interno
from vinculos.models import TipoVinculo
from core.models import BaseModel
from django.db import models
import datetime
import os
from datetime import date
from mj_crypt.mj_crypt import AESCipher
from imagehelpers.image import (
    resize_contain,
    get_format_file,
    get_mimetype,
    thumbnail,
    image_to_bytes,
    image_to_b64,
)


PLAIN_FASES = {
    "ANALISE_DIRETORIA": [
        "ASSISTENCIA_SOCIAL",
        "ANALISE_INTELIGENCIA",
        "DEFERIDO",
        "INDEFERIDO",
    ],
    "ANALISE_INTELIGENCIA": ["ANALISE_DIRETORIA", "ASSISTENCIA_SOCIAL"],
    "ASSISTENCIA_SOCIAL": ["ANALISE_DIRETORIA", "ANALISE_INTELIGENCIA"],
    "DEFERIDO": [],
    "INDEFERIDO": ["RECURSO"],
    "INICIADO": ["ANALISE_DIRETORIA", "ANALISE_INTELIGENCIA"],
    "RECURSO": ["RECURSO_EM_ANALISE"],
    "RECURSO_EM_ANALISE": ["RECURSO_DEFERIDO", "RECURSO_INDEFERIDO"],
    "RECURSO_DEFERIDO": [],
    "RECURSO_INDEFERIDO": [],
}

FASES_INFOR_SOLICITANTE = [
    "RECURSO_DEFERIDO",
    "RECURSO_INDEFERIDO",
    "DEFERIDO",
    "INDEFERIDO",
]


class Situacao(models.TextChoices):
    ANALISE_DIRETORIA = "ANALISE_DIRETORIA", _("Análise da Diretoria")
    ANALISE_INTELIGENCIA = "ANALISE_INTELIGENCIA", _("Análise da Inteligência")
    ASSISTENCIA_SOCIAL = "ASSISTENCIA_SOCIAL", _("Assistência Social")
    DEFERIDO = "DEFERIDO", _("Deferido")
    INDEFERIDO = "INDEFERIDO", _("Indeferido")
    INICIADO = "INICIADO", _("Iniciado")
    RECURSO = "RECURSO", _("Recurso")
    RECURSO_EM_ANALISE = "RECURSO_EM_ANALISE", _("Recurso - Análise da Diretoria")
    RECURSO_DEFERIDO = "RECURSO_DEFERIDO", _("Recurso Deferido")
    RECURSO_INDEFERIDO = "RECURSO_INDEFERIDO", _("Recurso Indeferido")
    SOLICITANTE_INFORMADO = "SOLICITANTE_INFORMADO", _("Solicitante Informado")


class DocumentosVisitante(BaseModel):
    crypt = AESCipher()
    arquivo_temp = models.FileField(upload_to="documentos_visitante")
    arquivo = models.BinaryField(default=None, blank=True, null=True)
    filename = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name = u"Documento"
        verbose_name_plural = u"Documentos"

    def save(self, *args, **kwargs):
        super(DocumentosVisitante, self).save(*args, **kwargs)
        temp = str(self.arquivo_temp)
        DOCUMENTO = os.path.join(MEDIA_ROOT, temp)
        name = temp.replace("documentos/", "").replace("documentos_visitante/", "")

        if os.path.isfile(DOCUMENTO):
            if DOCUMENTO.split(".")[-1].lower() != "pdf":
                self.resize_image(DOCUMENTO)
            else:
                self.encode_pdf(DOCUMENTO)
            os.remove(DOCUMENTO)

        DocumentosVisitante.objects.filter(id=self.id).update(
            arquivo=self.arquivo, filename=name
        )

    def encode_pdf(self, documento_local):
        import base64

        mime = get_mimetype(documento_local)
        with open(documento_local, "rb") as pdf_file:
            encoded_string = pdf_file.read()
        arquivo = image_to_b64(encoded_string, mime)
        self.arquivo = self.crypt.encrypt(arquivo)

    def resize_image(self, foto_local):
        mime = get_mimetype(foto_local)
        format_file = get_format_file(foto_local)
        arquivo = resize_contain(foto_local)
        barquivo = image_to_bytes(arquivo, format_file)
        arquivo = image_to_b64(barquivo, mime)
        self.arquivo = self.crypt.encrypt(arquivo)


class VisitanteRecurso(BaseModel):
    data_recurso = models.DateField()
    observacao = models.TextField(blank=True, null=True)
    documentos = models.ManyToManyField(DocumentosVisitante, blank=True)


class Visitante(BaseModel, DadosPessoais):
    class Atendimento(models.TextChoices):
        NORMAL = "NORMAL", ("Normal")
        PREFERENCIAL = "PREFERENCIAL", ("Preferencial")

    data_nascimento = models.DateField()
    mae_falecido = models.BooleanField(default=False, null=True, blank=True)
    mae_nao_declarado = models.BooleanField(default=False, null=True, blank=True)
    pai_falecido = models.BooleanField(default=False, null=True, blank=True)
    pai_nao_declarado = models.BooleanField(default=False, null=True, blank=True)
    idade = models.IntegerField(null=True, blank=True)
    profissao = models.ForeignKey(
        Profissao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="profissao_visitante_related",
    )
    numero_sei = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"\d{5}\.\d{6}\/\d{4}\-\d{2}", message="Nº SEI inválido"
            )
        ],
    )
    foto = models.ForeignKey(
        Foto,
        on_delete=models.PROTECT,
        related_name="foto%(app_label)s_%(class)s_related",
    )
    atendimento = models.CharField(
        max_length=20, choices=Atendimento.choices, null=True, blank=True
    )
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    solicitante_informado = models.BooleanField(default=False)
    enderecos = models.ManyToManyField(
        Endereco, blank=True, related_name="endereco_visitante_related"
    )
    telefones = models.ManyToManyField(
        Telefone, blank=True, related_name="telefone_visitante_related"
    )
    cpf = models.CharField(
        max_length=14,
        validators=[
            RegexValidator(
                regex=r"[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}\-?[0-9]{2}",
                message="CPF inválido",
            )
        ],
        null=True,
        blank=True,
    )
    documentos = models.ManyToManyField(Documentos, blank=True)
    fase = models.CharField(
        max_length=25, choices=Situacao.choices, null=True, blank=True
    )
    data_validade = models.DateField(default=None, null=True, blank=True)
    situacao = models.BooleanField(default=False)
    recurso = models.ForeignKey(
        VisitanteRecurso,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="recurso_visitante_related",
    )

    def __str__(self):
        return self.nome


class EmailVisitante(BaseModel):
    email = models.EmailField(max_length=150, null=True, blank=True)
    visitante = models.ForeignKey(
        Visitante,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="email_visitante",
    )

    class Meta:
        verbose_name = u"Email"
        verbose_name_plural = u"Emails"

    def __str__(self):
        return self.email


class RgVisitante(BaseModel):
    numero = models.CharField(max_length=15)
    orgao_expedidor = models.ForeignKey(
        OrgaoExpedidor,
        on_delete=models.PROTECT,
        related_name="orgao_expedidor_visitante",
    )
    visitante = models.ForeignKey(
        Visitante,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="rg_visitante",
    )

    class Meta:
        verbose_name = u"RG Visitante"
        verbose_name_plural = u"RG Visitante"

    def __str__(self):
        return self.numero


class Anuencia(BaseModel):
    visitante = models.ForeignKey(
        Visitante,
        on_delete=models.PROTECT,
        related_name="visitante_related",
        blank=True,
        null=True,
    )
    interno = models.ForeignKey(
        Interno, on_delete=models.PROTECT, related_name="interno_visitante_related"
    )
    data_declaracao = models.DateField()
    observacao = models.CharField(max_length=500, blank=True, null=True)
    tipo_vinculo = models.ForeignKey(
        TipoVinculo,
        on_delete=models.PROTECT,
        related_name="tipo_vinculo_anuencia_related",
    )
    documento = models.ForeignKey(
        DocumentosVisitante,
        on_delete=models.PROTECT,
        related_name="documento_visitante_related",
    )

    class Meta:
        verbose_name = u"Anuencia"
        verbose_name_plural = u"Anuencia"


class Manifestacao(BaseModel):
    visitante = models.ForeignKey(Visitante, on_delete=models.PROTECT)
    parecer = models.TextField()
    documentos = models.ManyToManyField(DocumentosVisitante, blank=True)

    def __str__(self):
        return self.parecer


class VisitanteMovimentacao(models.Model):
    visitante = models.ForeignKey(Visitante, on_delete=models.PROTECT)
    fase = models.CharField(max_length=25, choices=Situacao.choices)
    motivo = models.TextField(null=True, blank=True)
    data_contato = models.DateField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    usuario_cadastro = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="usuario_movimentacao_visitante_related",
    )


class ManifestacaoDiretoria(BaseModel):
    visitante = models.ForeignKey(Visitante, on_delete=models.PROTECT)
    parecer = models.TextField()
    documentos = models.ManyToManyField(DocumentosVisitante, blank=True)

    def __str__(self):
        return self.parecer
