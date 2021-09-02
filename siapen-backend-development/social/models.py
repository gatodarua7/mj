from django.db import models
from core.models import BaseModel


class Raca(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class GrauDeInstrucao(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Religiao(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class OrientacaoSexual(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Profissao(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class EstadoCivil(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class NecessidadeEspecial(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome