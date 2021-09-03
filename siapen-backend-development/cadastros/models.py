from configuracao.settings import MEDIA_ROOT
from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel
from localizacao.models import Cidade, Estado, Pais
from social.models import (
    Raca,
    GrauDeInstrucao,
    Religiao,
    OrientacaoSexual,
    Profissao,
    EstadoCivil,
    NecessidadeEspecial,
)

from util.upload import diretorio_upload
from django.core.validators import RegexValidator
from comum.models import Endereco, Telefone
import os
from mj_crypt.mj_crypt import AESCipher
from imagehelpers.image import (
    resize_contain,
    get_format_file,
    get_mimetype,
    thumbnail,
    image_to_bytes,
    image_to_b64,
)


class Genero(BaseModel):
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = u"Gênero"
        verbose_name_plural = u"Gêneros"


class Funcao(BaseModel):
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = u"Função"
        verbose_name_plural = u"Funções"


class Foto(BaseModel):
    crypt = AESCipher()

    foto_temp = models.ImageField(upload_to="fotos")
    foto = models.BinaryField(default=None, blank=True, null=True)
    thumbnail = models.BinaryField(default=None, blank=True, null=True)

    class Meta:
        verbose_name = u"Foto"
        verbose_name_plural = u"Fotos"

    def save(self, *args, **kwargs):
        super(Foto, self).save(*args, **kwargs)
        FOTO = os.path.join(MEDIA_ROOT, str(self.foto_temp))
        if os.path.isfile(FOTO):
            self.resize_image(FOTO)

    def resize_image(self, foto_local):
        from imagehelpers.image import thumbnail

        mime = get_mimetype(foto_local)
        format_file = get_format_file(foto_local)
        foto = resize_contain(foto_local)
        bfoto = image_to_bytes(foto, format_file)
        foto = image_to_b64(bfoto, mime)
        thumb = thumbnail(foto_local)
        bthumb = image_to_bytes(thumb, format_file)
        thumbnail = image_to_b64(bthumb, mime)
        self.foto = self.crypt.encrypt(foto)
        self.thumbnail = self.crypt.encrypt(thumbnail)
        Foto.objects.filter(id=self.id).update(thumbnail=self.thumbnail, foto=self.foto)


class OrgaoExpedidor(BaseModel):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=20)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = u"Órgão Expedidor"
        verbose_name_plural = u"Órgãos Expedidores"


class Pessoa(BaseModel):
    nome = models.CharField(max_length=150, null=False, blank=False)
    nome_social = models.CharField(max_length=150, null=True, blank=True)
    foto = models.ForeignKey(
        Foto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="foto_pessoa",
    )
    data_nascimento = models.DateField(default=None, blank=True, null=True)
    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}\-?[0-9]{2}",
                message="CPF inválido",
            )
        ],
    )
    rg = models.CharField(max_length=15, blank=True, null=True)
    orgao_expedidor = models.ForeignKey(
        OrgaoExpedidor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orgao_expedidor_pessoa",
    )
    genero = models.ForeignKey(Genero, on_delete=models.PROTECT, null=True, blank=True)
    raca = models.ForeignKey(Raca, on_delete=models.PROTECT, null=True, blank=True)
    estado_civil = models.ForeignKey(
        EstadoCivil, on_delete=models.PROTECT, null=True, blank=True
    )
    nacionalidade = models.ForeignKey(
        Pais, on_delete=models.PROTECT, null=True, blank=True
    )
    estado = models.ForeignKey(Estado, blank=True, null=True, on_delete=models.PROTECT)
    naturalidade = models.ForeignKey(
        Cidade, on_delete=models.PROTECT, null=True, blank=True
    )
    nome_mae = models.CharField(max_length=150, null=True, blank=True)
    nome_pai = models.CharField(max_length=150, null=True, blank=True)
    grau_instrucao = models.ForeignKey(
        GrauDeInstrucao, on_delete=models.PROTECT, null=True, blank=True
    )
    profissao = models.ForeignKey(
        Profissao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="profissao_%(app_label)s_%(class)s_related",
    )
    necessidade_especial = models.ManyToManyField(NecessidadeEspecial, blank=True)
    orientacao_sexual = models.ForeignKey(
        OrientacaoSexual, on_delete=models.PROTECT, null=True, blank=True
    )
    religiao = models.ForeignKey(
        Religiao, on_delete=models.PROTECT, null=True, blank=True
    )
    enderecos = models.ManyToManyField(Endereco, blank=True)
    telefones = models.ManyToManyField(Telefone, blank=True)
    mae_falecido = models.BooleanField(default=False)
    mae_nao_declarado = models.BooleanField(default=False)
    pai_falecido = models.BooleanField(default=False)
    pai_nao_declarado = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class TipoDocumento(models.Model):
    nome = models.CharField(max_length=150)
    ativo = models.BooleanField(default=True)
    excluido = models.BooleanField(default=False, null=False)

    def __str__(self):
        return self.nome


class Cargos(BaseModel):
    cargo = models.CharField(max_length=150)

    def __str__(self):
        return self.cargo

    class Meta:
        verbose_name = u"Cargos"
        verbose_name_plural = u"Cargos"


class RegimePrisional(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = u"Regime Prisional"
        verbose_name_plural = u"Regimes Prisionais"


class Periculosidade(BaseModel):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=20)
    observacao = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = u"Periculosidade"
        verbose_name_plural = u"Periculosidades"


class Documentos(BaseModel):
    crypt = AESCipher()
    tipo = models.ForeignKey(
        TipoDocumento, on_delete=models.PROTECT, related_name="tipo_documentos"
    )
    num_cod = models.CharField(max_length=30)
    observacao = models.CharField(max_length=100, blank=True, null=True, default="")
    arquivo_temp = models.FileField(upload_to="documentos")
    arquivo = models.BinaryField(default=None, blank=True, null=True)
    data_validade = models.DateField(default=None, blank=True, null=True)

    class Meta:
        verbose_name = u"Documento"
        verbose_name_plural = u"Documentos"

    def save(self, *args, **kwargs):
        super(Documentos, self).save(*args, **kwargs)
        DOCUMENTO = os.path.join(MEDIA_ROOT, str(self.arquivo_temp))
        if os.path.isfile(DOCUMENTO):
            if DOCUMENTO.split(".")[-1].lower() != "pdf":
                self.resize_image(DOCUMENTO)
            else:
                self.encode_pdf(DOCUMENTO)
            os.remove(DOCUMENTO)

        Documentos.objects.filter(id=self.id).update(arquivo=self.arquivo)

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


class Setor(BaseModel):
    setor_pai = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="setorpai"
    )
    enderecos = models.ForeignKey(
        Endereco,
        related_name="setor_endereco",
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
    )
    telefones = models.ManyToManyField(Telefone, blank=True)
    nome = models.CharField(max_length=150)
    sigla = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = u"Setor"
        verbose_name_plural = u"Setores"


class ComportamentoInterno(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = u"Comportamento de Interno"
