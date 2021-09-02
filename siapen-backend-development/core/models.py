from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

import uuid


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=None, blank=True, null=True)
    delete_at = models.DateTimeField(default=None, blank=True, null=True)
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT)
    usuario_edicao = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="updated%(app_label)s_%(class)s_related",
        default=None,
        blank=True,
        null=True,
    )
    usuario_exclusao = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="delete%(app_label)s_%(class)s_related",
        default=None,
        blank=True,
        null=True,
    )
    excluido = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Metodos(models.TextChoices):
    PATCH = "PATCH", _("Atualizar")
    PUT = "PUT", _("Atualizar")
    POST = "POST", _("Cadastrar")
    DELETE = "DELETE", _("Excluir")
    GET = "GET", _("Consultar")


class Log(models.Model):
    STATUS = (
        (100, _("Continuar")),
        (101, _("Mudando Protocolos")),
        (102, _("Processando")),
        (200, _("Ok")),
        (201, _("Criado")),
        (202, _("Aceito")),
        (203, _("Não autorizado")),
        (204, _("Nenhum Conteúdo")),
        (205, _("Resetar Conteúdo")),
        (206, _("Conteúdo Parcial")),
        (300, _("Múltipla Escolha")),
        (301, _("Movido Permanentemente")),
        (302, _("Encontrado")),
        (303, _("Veja outro")),
        (304, _("Não modificado")),
        (305, _("Use Proxy")),
        (306, _("Proxy Trocado")),
        (400, _("Solicitação Inválida")),
        (401, _("Não autorizado")),
        (402, _("Pagamento necessário")),
        (403, _("Proibido")),
        (404, _("Não encontrado")),
        (405, _("Método não permitido")),
        (406, _("Não aceito")),
        (407, _("Autenticação de Proxy Necessária")),
        (408, _("Tempo de solicitação esgotado")),
        (409, _("Conflito")),
        (410, _("Perdido")),
        (411, _("Duração necessária")),
        (412, _("Falha de pré-condição")),
        (413, _("Solicitação da entidade muito extensa")),
        (414, _("Solicitação de URL muito Longa")),
        (415, _("Tipo de mídia não suportado")),
        (416, _("Solicitação de faixa não satisfatória")),
        (417, _("Falha na expectativa")),
        (500, _("Erro do Servidor Interno")),
        (501, _("Não implementado")),
        (502, _("Porta de entrada ruim")),
        (503, _("Serviço Indisponível")),
        (504, _("Tempo limite da Porta de Entrada")),
        (505, _("Versão HTTP não suportada")),
    )

    id = models.IntegerField(primary_key=True)
    requested_at = models.DateTimeField()
    response_ms = models.IntegerField()
    path = models.CharField(max_length=200)
    remote_addr = models.TextField()
    host =  models.CharField(max_length=200)
    method = models.CharField(max_length=10, choices=Metodos.choices)
    query_params = models.TextField()
    data = models.TextField()
    response = models.TextField()
    status_code = models.IntegerField(choices=STATUS, default=1)
    user_id = models.IntegerField()
    view = models.CharField(max_length=200)
    view_method = models.CharField(max_length=200)
    errors = models.TextField()
    username_persistent = models.CharField(max_length=200)
    response_old = models.TextField(null=True, blank=True)

    class Meta:
       managed = False
       db_table = 'rest_framework_tracking_apirequestlog'