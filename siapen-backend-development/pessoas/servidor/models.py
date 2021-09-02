from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from cadastros.models import (
    Cargos,
    Setor,
    Documentos,
    Funcao,
    OrgaoExpedidor,
)
from core.models import BaseModel
from pessoas.models import DadosPessoais
from comum.models import Endereco, Telefone
from localizacao.models import Pais, Estado, Cidade


class Servidor(BaseModel, DadosPessoais):
    data_nascimento = models.DateField(default=None, blank=True, null=True)
    rg = models.CharField(max_length=15, blank=True, null=True)
    orgao_expedidor = models.ForeignKey(
        OrgaoExpedidor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orgao_expedidor_servidor",
    )
    enderecos = models.ManyToManyField(Endereco, blank=True)
    telefones = models.ManyToManyField(
        Telefone, blank=True, related_name="telefones_pessoais"
    )
    telefones_funcionais = models.ManyToManyField(
        Telefone, blank=True, related_name="telefones_funcionais"
    )
    email_pessoal = models.EmailField(max_length=150, null=True, blank=True)
    email_profissional = models.EmailField(max_length=150)
    matricula = models.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r"^[-+]?[0-9]+$",
                message="Apenas números são aceitos.",
            ),
        ],
    )
    data_admissao = models.DateField()
    data_desligamento = models.DateField(default=None, blank=True, null=True)
    lotacao = models.ForeignKey(
        Setor, on_delete=models.PROTECT, related_name="lotacao_servidor"
    )
    lotacao_temporaria = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
        related_name="lotacao_temporaria_servidor",
    )
    cargos = models.ForeignKey(Cargos, on_delete=models.PROTECT)
    funcao = models.ManyToManyField(Funcao, blank=True)
    motivo_desligamento = models.TextField(max_length=200, null=True, blank=True)
    motivo_ativacao = models.TextField(max_length=200, default=None, null=True, blank=True)
    motivo_inativacao = models.TextField(max_length=200, default=None, null=True, blank=True)
    data_ativacao = models.DateTimeField(default=None, blank=True, null=True)
    data_inativacao = models.DateTimeField(default=None, blank=True, null=True)
    usuario_ativacao = models.ForeignKey(User, on_delete=models.PROTECT, 
                                        related_name="Ativacao_servidor_related", 
                                        default=None, blank=True, null=True)
    usuario_inativacao = models.ForeignKey(User, on_delete=models.PROTECT, 
                                        related_name="Inativação_servidor_related", 
                                        default=None, blank=True, null=True)
    documentos = models.ManyToManyField(Documentos, blank=True)
    situacao = models.BooleanField(default=False)


    def __str__(self):
        return self.nome
