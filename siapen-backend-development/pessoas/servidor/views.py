from itertools import permutations
from django.db.models import Q
from django.forms.models import model_to_dict
from rest_framework import status
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from pessoas.servidor.serializers import ServidorSerializer
from pessoas.servidor.models import Servidor
from itertools import chain
from comum.models import Endereco, Telefone
from localizacao.models import Estado, Cidade, Pais
from rest_framework import status, viewsets
from util.paginacao import Paginacao
from util.busca import (
    trata_campo,
    trata_campo_ativo,
    trata_telefone,
    check_duplicidade,
    formata_data,
    formata_data_hora,
    get_ids,
    has_key,
)
from util import mensagens, validador, user
from datetime import datetime
from core.views import Base


class ServidorViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = ServidorSerializer
    pagination_class = Paginacao
    queryset = Servidor.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "cpf", "matricula", "cargos__cargo", "situacao", "ativo")
    filter_fields = ("nome", "cpf", "matricula", "cargos__cargo", "situacao", "ativo")
    ordering_fields = ("nome", "cpf", "matricula", "cargos__cargo", "situacao", "ativo")
    ordering = ("nome", "cpf", "matricula", "cargos__cargo", "situacao", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_servidor_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if (
                requisicao.get("naturalidade") and requisicao.get("estado")
            ) and not self.check_cidade(requisicao):
                return Response(
                    {"non_field_errors": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(ServidorViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_servidor_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if (
                requisicao.get("naturalidade") and requisicao.get("estado")
            ) and not self.check_cidade(requisicao):
                return Response(
                    {"non_field_errors": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_excluido(Servidor, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Servidor, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super(ServidorViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Servidor, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Servidor, pk):
                return Response(
                    {"detail": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Servidor.objects.filter(id=pk).update(excluido=True)
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def filter_queryset(self, queryset):
        queryset = super(ServidorViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        exclude_id = (
            parametros_busca.get("exclude_ids").split(",")
            if parametros_busca.get("exclude_ids")
            else None
        )
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        queryset_servidor = Servidor.objects.none()
        for query in Servidor.objects.filter(Q(excluido=False)):
            qs = Servidor.objects.none()
            servidor_list = list()
            servidor_list2 = list()
            servidor_list.append(trata_campo(query.nome))
            servidor_list.append(trata_campo(query.nome_social))
            servidor_list2.append(trata_campo(query.cpf))
            servidor_list.append(trata_campo(query.matricula))
            servidor_list.append(trata_campo(query.rg))
            servidor_list.append(formata_data(trata_campo(query.data_nascimento)))
            servidor_list.append(trata_campo(query.nome_pai))
            servidor_list.append(trata_campo(query.nome_mae))
            servidor_list.append(trata_campo(query.motivo_desligamento))
            servidor_list.append(formata_data(trata_campo(query.data_admissao)))
            servidor_list.append(
                trata_campo(query.email_pessoal) if query.email_pessoal else ""
            )

            servidor_list.append(
                trata_campo(query.orgao_expedidor.nome) if query.orgao_expedidor else ""
            )
            servidor_list.append(
                trata_campo(query.orgao_expedidor.estado.nome)
                if query.orgao_expedidor
                else ""
            )
            servidor_list.append(
                trata_campo(query.genero.descricao) if query.genero else ""
            )
            servidor_list.append(trata_campo(query.raca.nome) if query.raca else "")
            servidor_list.append(
                trata_campo(query.estado_civil.nome) if query.estado_civil else ""
            )
            servidor_list.append(trata_campo(query.estado.nome) if query.estado else "")
            servidor_list.append(
                trata_campo(query.naturalidade.nome) if query.naturalidade else ""
            )
            servidor_list.append(
                trata_campo(query.grau_instrucao.nome) if query.grau_instrucao else ""
            )
            servidor_list.append(
                trata_campo(query.orientacao_sexual.nome)
                if query.orientacao_sexual
                else ""
            )
            servidor_list.append(
                trata_campo(query.religiao.nome) if query.religiao else ""
            )
            servidor_list.extend(
                [
                    trata_campo(necessidade.nome)
                    for necessidade in query.necessidade_especial.all()
                ]
            )

            servidor_list.append(
                trata_campo(query.email_profissional)
                if query.email_profissional
                else ""
            )
            servidor_list.append(
                formata_data(trata_campo(query.data_desligamento))
                if query.data_desligamento
                else ""
            )
            servidor_list.append(trata_campo(query.lotacao.nome))
            servidor_list.append(
                trata_campo(query.lotacao_temporaria.nome)
                if query.lotacao_temporaria
                else ""
            )
            servidor_list.append(trata_campo(query.cargos.cargo))
            servidor_list.extend(
                [trata_campo(funcao.descricao) for funcao in query.funcao.all()]
            )

            servidor_list.extend(
                [trata_campo(pais.nome) for pais in query.nacionalidade.all()]
            )

            for endereco in query.enderecos.all():
                servidor_list.append(trata_campo(endereco.logradouro))
                servidor_list.append(trata_campo(endereco.bairro))
                servidor_list.append(trata_campo(endereco.numero))
                servidor_list.append(trata_campo(endereco.cidade.nome))
                servidor_list.append(trata_campo(endereco.estado.nome))
                servidor_list.append(trata_campo(endereco.estado.sigla))
                servidor_list.append(trata_campo(endereco.observacao))
                servidor_list.append(trata_campo(endereco.complemento))
                servidor_list2.append(
                    trata_campo(endereco.cep.replace("-", "").replace(".", ""))
                )
                servidor_list.append(trata_campo(endereco.andar))
                servidor_list.append(trata_campo(endereco.sala))

            for telefone in query.telefones.all():
                servidor_list.append(trata_campo(telefone.tipo))
                servidor_list2.append(trata_campo(telefone.numero))
                servidor_list.append(trata_campo(telefone.observacao))

            for telefone in query.telefones_funcionais.all():
                servidor_list.append(trata_campo(telefone.tipo))
                servidor_list2.append(trata_campo(telefone.numero))
                servidor_list.append(trata_campo(telefone.observacao))
                servidor_list.append(trata_campo(telefone.andar))
                servidor_list.append(trata_campo(telefone.sala))

            for documento in query.documentos.all():
                servidor_list.append(trata_campo(documento.num_cod))
                servidor_list.append(trata_campo(documento.observacao))
                servidor_list.append(trata_campo(documento.tipo.nome))
                servidor_list.append(formata_data_hora(documento.created_at))
                if documento.updated_at:
                    servidor_list.append(formata_data_hora(documento.updated_at))
                servidor_list.append(formata_data(trata_campo(documento.data_validade)))

            for item in servidor_list:
                if busca in item:
                    qs = Servidor.objects.filter(pk=query.pk)
                    break

            if not qs:
                for item in servidor_list2:
                    if trata_telefone(busca) in item:
                        qs = Servidor.objects.filter(pk=query.pk)
                        break

            if queryset_servidor:
                queryset_servidor = qs
                queryset = queryset_servidor
            elif qs:
                queryset = queryset | qs

        if exclude_id:
            queryset = queryset.filter(~Q(pk__in=exclude_id))

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_servidor_exists(self, requisicao):
        cpf = check_duplicidade(requisicao.get("cpf"))
        return Servidor.objects.filter(
            Q(cpf__iexact=cpf, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_cidade(self, requisicao):
        return Cidade.objects.filter(
            Q(id=requisicao["naturalidade"], estado_id=requisicao["estado"])
        ).exists()

    def perform_create(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["telefones"] = self.get_telefones(requisicao)
        kwargs["enderecos"] = get_ids(requisicao.get("enderecos"))
        kwargs["documentos"] = get_ids(requisicao.get("documentos"))
        kwargs["telefones_funcionais"] = get_ids(requisicao.get("telefones_funcionais"))
        kwargs["situacao"] = self.check_cadastro(requisicao)
        kwargs["usuario_cadastro"] = user.get_user(self)
        kwargs.update(self.check_motivo_desligamento(requisicao, create=True))
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["updated_at"] = datetime.now()
        if has_key("telefones", requisicao):
            kwargs["telefones"] = self.get_telefones(requisicao)
        if has_key("enderecos", requisicao):
            kwargs["enderecos"] = get_ids(requisicao.get("enderecos"))
        if has_key("documentos", requisicao):
            kwargs["documentos"] = get_ids(requisicao.get("documentos"))
        if has_key("telefones_funcionais", requisicao):
            kwargs["telefones_funcionais"] = get_ids(
                requisicao.get("telefones_funcionais")
            )
        kwargs["situacao"] = self.check_cadastro(self.update_dict(requisicao))
        kwargs["usuario_edicao"] = user.get_user(self)
        kwargs.update(self.check_motivo_desligamento(requisicao))
        serializer.save(**kwargs)

    def check_motivo_desligamento(self, requisicao, create=False):
        retorno = dict()
        if not create:
            servidor = (
                Servidor.objects.filter(pk=requisicao["id"]).values("ativo").first()
            )
            if servidor["ativo"] != requisicao.get("ativo"):
                if requisicao.get("ativo") is False:
                    retorno = {
                        "ativo": requisicao.get("ativo"),
                        "motivo_inativacao": requisicao.get("motivo_inativacao"),
                        "usuario_inativacao": user.get_user(self),
                        "data_inativacao": datetime.now(),
                    }
                    return retorno
                elif requisicao.get("ativo") is True:
                    retorno = {
                        "ativo": requisicao.get("ativo"),
                        "motivo_ativacao": requisicao.get("motivo_ativacao"),
                        "usuario_ativacao": user.get_user(self),
                        "data_ativacao": datetime.now(),
                    }
                    return retorno
        if requisicao.get("data_desligamento"):
            retorno = {
                "ativo": False,
                "motivo_inativacao": requisicao.get("motivo_desligamento"),
                "usuario_inativacao": user.get_user(self),
                "data_inativacao": datetime.now(),
            }
        return retorno

    def update_dict(self, requisicao):
        dict_saida = model_to_dict(Servidor.objects.get(pk=requisicao["id"]))
        for key, v in requisicao.items():
            dict_saida[key] = v
        return dict_saida

    def check_cadastro(self, requisicao):
        completo = True
        if not requisicao.get("nome_pai") and not requisicao.get("pai_nao_declarado"):
            completo = False
        elif completo and (
            not requisicao.get("nome_mae") and not requisicao.get("mae_nao_declarado")
        ):
            completo = False
        elif completo and requisicao.get("nacionalidade"):
            for nacionalidade in requisicao.get("nacionalidade"):
                pais = Pais.objects.filter(id=nacionalidade).values().first()
                if pais["nome"] == "Brasil" and (
                    not requisicao.get("estado") or not requisicao.get("naturalidade")
                ):
                    completo = False
                    break
        if completo:
            fields = [
                "nome",
                "data_nascimento",
                "cpf",
                "rg",
                "orgao_expedidor",
                "genero",
                "raca",
                "estado_civil",
                "nacionalidade",
                "grau_instrucao",
                "necessidade_especial",
                "orientacao_sexual",
                "religiao",
                "enderecos",
                "telefones",
                "foto",
                "email_pessoal",
                "email_profissional",
                "matricula",
                "data_admissao",
                "lotacao",
                "cargos",
                "funcao",
                "documentos",
                "telefones_funcionais",
            ]
            for field in fields:
                if not requisicao.get(field):
                    completo = False
                    break
        return completo

    def get_telefones(self, request):
        list_telefones = list()
        for telefone in request.get("telefones"):
            privado = True
            Telefone.objects.filter(
                Q(id=telefone["id"]) & (Q(tipo="CELULAR") | Q(tipo="RESIDENCIAL"))
            ).update(privado=privado)
            list_telefones.append(telefone["id"])
        return list_telefones

    @action(
        detail=False,
        methods=["get"],
        url_path=r"usuarios_telefone/(?P<telefone>\d+)",
        url_name="usuarios_telefone",
    )
    def get_usuarios_telefone(self, request, telefone):
        try:
            nome_pessoas = dict()
            pessoas = Servidor.objects.filter(
                Q(telefones__numero__icontains=trata_telefone(telefone))
                & Q(excluido=False)
            ).values_list("nome", flat=True)
            nome_pessoas["nome"] = pessoas
            return Response(nome_pessoas, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
