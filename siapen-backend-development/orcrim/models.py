from django.contrib.auth.models import User
from localizacao.models import Estado, Pais
from cadastros.models import Pessoa
from comum.models import BaseModel
from django.db import models
from util import mensagens


class Faccao(BaseModel):
    nome = models.CharField(max_length=150)
    sigla = models.CharField(max_length=10)
    pais = models.ManyToManyField(Pais, blank=True)
    estado = models.ManyToManyField(Estado, blank=True)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = (u"Facção")
        verbose_name_plural = (u"Facções")

class FaccaoPessoa(BaseModel):
    faccao = models.ForeignKey(Faccao, on_delete=models.PROTECT)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT)
    data_filiacao_faccao = models.DateField(null=True, blank=True)
    data_desfiliacao_faccao = models.DateField(null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.faccao} - {self.pessoa}"


class FaccaoGrupo(BaseModel):
    faccao = models.ForeignKey(Faccao, on_delete=models.PROTECT)
    nome = models.CharField(max_length=150)
    observacao = models.TextField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.nome


class FaccaoCargo(BaseModel):
    faccao = models.ForeignKey(Faccao, on_delete=models.PROTECT)
    nome = models.CharField(max_length=150)
    observacao = models.TextField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.nome
