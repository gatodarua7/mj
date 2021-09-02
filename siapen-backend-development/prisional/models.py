from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields.array import ArrayField
from django.core.validators import MinValueValidator, RegexValidator
from cadastros.models import Pessoa, Setor
from core.models import BaseModel
from localizacao.models import Cidade, Estado, Pais
from util import mensagens


class CaseInsensitiveFieldMixin:
    LOOKUP_CONVERSIONS = {
        'exact': 'iexact',
        'contains': 'icontains',
        'startswith': 'istartswith',
        'endswith': 'iendswith',
        'regex': 'iregex',
        'unaccent': 'unaccent'
    }

    def get_lookup(self, lookup_name):
        converted = self.LOOKUP_CONVERSIONS.get(lookup_name, lookup_name)
        return super().get_lookup(converted)


class CICharField(CaseInsensitiveFieldMixin, models.CharField):
    pass


class Departamento(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    sigla = models.CharField(max_length=50, default=None)
    pais = models.ForeignKey(
        Pais, on_delete=models.PROTECT, null=True, blank=True)
    estado = models.ForeignKey(
        Estado, on_delete=models.PROTECT, null=True, blank=True)
    ativo = models.BooleanField(default=True,  null=False)

    def __str__(self):
        return self.nome


class SistemaPenal(BaseModel):
    nome = CICharField(max_length=100)
    sigla = models.CharField(max_length=60, default=None)
    pais = models.ForeignKey(
        Pais, on_delete=models.PROTECT, null=True, blank=True)
    estado = models.ForeignKey(
        Estado, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = (u"Sistema Penal")
        verbose_name_plural = (u"Sistemas Penais")


class Unidade(BaseModel):
    nome = models.CharField(max_length=250)
    sigla = models.CharField(max_length=60, default=None)
    sistema = models.ForeignKey(
        SistemaPenal, on_delete=models.PROTECT)
    estado = models.ForeignKey(
        Estado, on_delete=models.PROTECT, null=True, blank=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)

    class Meta:
        verbose_name = (u"Unidade de Custódia")
        verbose_name_plural = (u"Unidades de Custódia")
        unique_together = ['nome', 'cidade', 'sistema']

    def __str__(self):
        return self.nome


class Bloco(BaseModel):
    bloco_pai = models.ForeignKey(
        'self', on_delete=models.PROTECT, null=True, blank=True, related_name="blocopai")
    sistema = models.ForeignKey(SistemaPenal, null=True, default=None, related_name='bloco_sistema', on_delete=models.PROTECT)
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Defeito(BaseModel):
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.descricao


class Cela(BaseModel):
    bloco = models.ForeignKey(Bloco, on_delete=models.PROTECT)
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT,
                                default=None, blank=True, null=True)
    sistema = models.ForeignKey(SistemaPenal, on_delete=models.PROTECT,
                                default=None, blank=True, null=True)
    nome = models.CharField(max_length=30)
    capacidade = models.IntegerField(validators=[MinValueValidator(1)])
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome


class DefeitoCela(BaseModel):
    defeito = models.ForeignKey(Defeito, on_delete=models.PROTECT)
    cela = models.ForeignKey(Cela, on_delete=models.PROTECT)
    data_criacao = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return 'Cela ' + self.cela.nome + ' - ' + self.cela.bloco.nome + ' / ' + self.defeito.descricao


class ReparoCela(models.Model):
    defeito_cela = models.ForeignKey(DefeitoCela, on_delete=models.PROTECT)
    data_reparo = models.DateTimeField(auto_now_add=True)
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT)


class DesignacaoFuncaoServidor(models.Model):
    descricao = models.CharField(max_length=150, unique=True)
    data_cadastro = models.DateTimeField(auto_now=True)


class UsuarioSistema(models.Model):
    login = models.OneToOneField(User, on_delete=models.CASCADE)
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT)
    data_cadastro = models.DateTimeField(auto_now=True)
