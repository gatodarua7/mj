from cadastros.models import OrgaoExpedidor
from rest_framework.decorators import action
from comum.models import Telefone
import datetime
from localizacao.models import Cidade, Estado, Pais
from util.busca import check_duplicidade, formata_data, trata_campo, trata_campo_ativo, trata_telefone, get_ids, has_key
from pessoas.advogado.models import Advogado, EmailAdvogado, OAB, RgAdvogado
from django.db.models import Q
from pessoas.advogado.serializers import AdvogadoSerializer, EmailSerializer, OABSerializer, RgAdvogadoSerializer
from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status, viewsets
from util.paginacao import Paginacao
from util import mensagens, validador, user
from datetime import datetime
from uuid import UUID
import ast
from core.views import Base


class AdvogadoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = AdvogadoSerializer
    pagination_class = Paginacao
    queryset = Advogado.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "cpf", "data_nascimento",
                     "situacao","ativo")
    filter_fields = ("nome","cpf", "data_nascimento","oabs", "situacao","ativo")
    ordering_fields = ("nome", "cpf", "data_nascimento","oabs", "situacao","ativo")
    ordering = ("nome","cpf", "data_nascimento","situacao","ativo")

    def create(self, request, *args, **kwargs):
        requisicao = request.data
        try:
            if not requisicao.get("nacionalidade"):
                return Response(
                    {"nacionalidade": mensagens.MSG2.format(u"nacionalidade")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if self.check_advogado_exists(requisicao):
                return Response(
                    {"cpf": mensagens.MSG4},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if (
                requisicao.get("naturalidade") and requisicao.get("estado")
            ) and not self.check_cidade(requisicao):
                return Response(
                    {"naturalidade": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(AdvogadoViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_advogado_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4},
                    status=status.HTTP_409_CONFLICT,
                )
            if (
                requisicao.get("naturalidade") and requisicao.get("estado")
            ) and not self.check_cidade(requisicao):
                return Response(
                    {"non_field_errors": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_excluido(Advogado, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Advogado, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(AdvogadoViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            Advogado.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )


    def filter_queryset(self, queryset):
        queryset = super(AdvogadoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        queryset_advogado = Advogado.objects.none()
        for query in Advogado.objects.filter(Q(excluido=False)):
            qs = Advogado.objects.none()
            advogado_list = list()
            advogado_list2 = list()
            advogado_list.append(trata_campo(query.nome))
            advogado_list2.append(trata_campo(query.cpf))
            advogado_list.append(formata_data(trata_campo(query.data_nascimento)))

            advogado_list.append(trata_campo(query.genero.descricao) if query.genero else "")
            advogado_list.append(trata_campo(query.estado.nome) if query.estado else "")
            advogado_list.append(
                trata_campo(query.naturalidade.nome) if query.naturalidade else "")
            advogado_list.extend([
                trata_campo(necessidade.nome)
                for necessidade in query.necessidade_especial.all()
            ])

            advogado_list.extend([
                    trata_campo(pais.nome) for pais in query.nacionalidade.all()
                ])

            for endereco in query.enderecos.all():
                advogado_list.append(trata_campo(endereco.logradouro))
                advogado_list.append(trata_campo(endereco.bairro))
                advogado_list.append(trata_campo(endereco.numero))
                advogado_list.append(trata_campo(endereco.cidade.nome))
                advogado_list.append(trata_campo(endereco.estado.nome))
                advogado_list.append(trata_campo(endereco.estado.sigla))
                advogado_list.append(trata_campo(endereco.observacao))
                advogado_list.append(trata_campo(endereco.complemento))
                advogado_list2.append(trata_campo(endereco.cep.replace("-", "").replace(".", "")))
                advogado_list.append(trata_campo(endereco.andar))
                advogado_list.append(trata_campo(endereco.sala))

            for telefone in query.telefones.all():
                advogado_list.append(trata_campo(telefone.tipo))
                advogado_list2.append(trata_campo(telefone.numero))
                advogado_list.append(trata_campo(telefone.observacao))

            for oab in query.oabs.all():
                advogado_list.append(trata_campo(oab.numero))
                advogado_list.append(trata_campo(oab.estado.nome))
            
            for rg in RgAdvogado.objects.filter(advogado_id=query.id, excluido=False):
                advogado_list.append(trata_campo(rg.numero))
                advogado_list.append(trata_campo(rg.orgao_expedidor.nome))
                advogado_list.append(trata_campo(rg.orgao_expedidor.sigla))
                advogado_list.append(trata_campo(rg.orgao_expedidor.estado))

            for email in EmailAdvogado.objects.filter(advogado_id=query.id, excluido=False):
                advogado_list.append(trata_campo(email.email))

            for item in advogado_list:
                if busca in item:
                    qs = Advogado.objects.filter(pk=query.pk)
                    break

            if not qs:
                for item in advogado_list2:
                    if trata_telefone(busca) in item:
                        qs = Advogado.objects.filter(pk=query.pk)
                        break

            if queryset_advogado:
                queryset_advogado = qs
                queryset = queryset_advogado
            elif qs:
                queryset = queryset | qs

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset
    
    def check_advogado_exists(self, requisicao):
        cpf = check_duplicidade(requisicao.get("cpf"))
        return Advogado.objects.filter(
            Q(cpf__iexact=cpf, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_cidade(self, requisicao):
        return Cidade.objects.filter(
            Q(id=requisicao["naturalidade"], estado_id=requisicao["estado"])
        ).exists()

    def check_cadastro(self, requisicao):
        completo = True
        if completo and requisicao.get("nacionalidade"):
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
                "genero",
                "oabs",
                "nacionalidade",
                "enderecos",
                "telefones"
            ]
            for field in fields:
                if not requisicao.get(field):
                    completo = False
                    break
        return completo

    def perform_create(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["telefones"] = self.get_telefones(requisicao)
        kwargs["enderecos"] = get_ids(requisicao.get("enderecos"))
        if requisicao.get("oabs"):
            kwargs["oabs"] = get_ids(requisicao.get("oabs"))
        kwargs["situacao"] = self.check_cadastro(requisicao)
        kwargs["usuario_cadastro"] = user.get_user(self)
        kwargs.update(self.check_motivo_desligamento(requisicao, create=True))
        obj = serializer.save(**kwargs)

        advogado = Advogado.objects.get(id=obj.id)

        if requisicao.get("emails"):
            for email in requisicao["emails"]:
                EmailAdvogado.objects.create(advogado_id=obj.id, email=email, usuario_cadastro=user.get_user(self))

        if requisicao.get("rg"):
            for rg in requisicao["rg"]:
                orgao_exp = OrgaoExpedidor.objects.get(id=rg.get("orgao_expedidor"))
                rg_obj, created = RgAdvogado.objects.get_or_create(numero=rg.get("numero"), orgao_expedidor_id=orgao_exp.id)
                rg_obj.advogado = advogado
                rg_obj.usuario_cadastro = user.get_user(self)
                rg_obj.save()
        self.create_many_fields(serializer=serializer)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["updated_at"] = datetime.now()
        kwargs["situacao"] = self.check_cadastro(requisicao)
        if has_key("telefones", requisicao):
            kwargs["telefones"] = self.get_telefones(requisicao)
        if has_key("enderecos", requisicao):
            kwargs["enderecos"] = get_ids(requisicao.get("enderecos"))
        if requisicao.get("oabs"):
            kwargs["oabs"] = get_ids(requisicao.get("oabs"))
        kwargs["usuario_edicao"] = user.get_user(self)
        kwargs.update(self.check_motivo_desligamento(requisicao))
        serializer.save(**kwargs)
        pk = serializer.data.get("id")
        self.update_many_fields(pk=pk)

    def check_motivo_desligamento(self, requisicao, create=False):
        retorno = dict()
        if not create:
            servidor = (
                Advogado.objects.filter(pk=requisicao["id"]).values("ativo").first()
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
        return retorno


    def create_many_fields(self, serializer):
        requisicao = self.request.data

        if self.request.data.get("rgs"):
            for rg in self.request.data.get("rgs"):
                RgAdvogado.objects.filter(id=rg.get("id")).update(
                    advogado_id=serializer.data["id"]
                )

        try:
            emails = ast.literal_eval(requisicao.get("emails"))
        except Exception:
            emails = (
                self.request.data.get("emails")
                if self.request.data.get("emails")
                else None
            )

        if emails:
            for email in emails:
                if email.strip():
                    email = email.strip()
                    EmailAdvogado.objects.update_or_create(
                        email=email,
                        usuario_cadastro=user.get_user(self),
                        advogado_id=serializer.data["id"],
                        ativo=True,
                    )

    def update_many_fields(self, pk):
        requisicao = self.request.data

        if self.request.data.get("rgs"):
            for rg in self.request.data.get("rgs"):
                RgAdvogado.objects.filter(id=rg.get("id")).update(
                    advogado_id=pk
                )

        try:
            emails = ast.literal_eval(requisicao.get("emails"))
        except Exception:
            emails = (
                requisicao.get("emails")
                if requisicao.get("emails")
                else None
            )

        if emails:
            for email in EmailAdvogado.objects.filter(~Q(email__in=emails) & Q(advogado_id=pk)):
                EmailAdvogado.objects.filter(Q(pk=email.pk)).delete()
            for email in emails:
                if email.strip():
                    email = email.strip()
                    EmailAdvogado.objects.update_or_create(
                        email=email,
                        usuario_cadastro=user.get_user(self),
                        advogado_id=UUID(pk),
                        ativo=True,
                    )

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
            pessoas = Advogado.objects.filter(
                Q(telefones__numero__icontains=trata_telefone(telefone))
                & Q(excluido=False)
            ).values_list("nome", flat=True)
            nome_pessoas["nome"] = pessoas
            return Response(nome_pessoas, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OABViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = OABSerializer
    pagination_class = Paginacao
    queryset = OAB.objects.filter(excluido=False)
    filter_backends = (SearchFilter,)
    search_fields = ("numero", "estado__nome")
    filter_fields = ("numero", "estado__nome")

    def create(self, request, *args, **kwargs):
        try:
            return super(OABViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super(OABViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            OAB.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer,  **kwargs):
        estado = Estado.objects.get(id=self.request.data.get("estado"))
        kwargs["usuario_cadastro"] = user.get_user(self)
        kwargs["estado"] = estado
        serializer.save(**kwargs)

    def perform_update(self, serializer):
        serializer.save(
            usuario_edicao=user.get_user(self),
        )

class RgAdvogadoViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = RgAdvogadoSerializer
    pagination_class = Paginacao
    queryset = RgAdvogado.objects.filter(excluido=False)
    filter_backends = (SearchFilter,)
    search_fields = "numero"

    def create(self, request, *args, **kwargs):
        try:
            return super(RgAdvogadoViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super(RgAdvogadoViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            RgAdvogado.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save(
            usuario_cadastro=user.get_user(self),
        )

    def perform_update(self, serializer):
        serializer.save(
            usuario_edicao=user.get_user(self),
        )

class EmailViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = EmailSerializer
    pagination_class = Paginacao
    queryset = EmailAdvogado.objects.filter(excluido=False)
    filter_backends = (SearchFilter,)
    search_fields = "email"

    def create(self, request, *args, **kwargs):
        try:
            return super(EmailViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super(EmailViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            EmailAdvogado.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save(
            usuario_cadastro=user.get_user(self),
        )

    def perform_update(self, serializer):
        serializer.save(
            usuario_edicao=user.get_user(self),
        )
