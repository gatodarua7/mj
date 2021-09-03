from django.db.models import Q
from rest_framework.settings import import_from_string
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from prisional.serializers import (
    BlocoSerializer,
    CelaSerializer,
    DefeitoCelaSerializer,
    DefeitoSerializer,
    DesignacaoFuncaoServidorSerializer,
    ReparoCelaSerializer,
    SistemaPenalSerializer,
    UnidadeSerializer,
    UsuarioSistemaSerializer,
)
from prisional.models import (
    Bloco,
    Cela,
    DefeitoCela,
    Defeito,
    DesignacaoFuncaoServidor,
    ReparoCela,
    SistemaPenal,
    Unidade,
    UsuarioSistema,
)
from localizacao.models import Cidade
from comum.models import Endereco, Telefone
from util.paginacao import Paginacao
from util.busca import trata_campo, trata_campo_ativo, trata_telefone, check_duplicidade
from util import mensagens, user
from rest_framework import viewsets, status
from itertools import chain
from datetime import datetime
import uuid
from core.views import Base


class BlocoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = BlocoSerializer
    pagination_class = Paginacao
    queryset = Bloco.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = (
        "unidade__nome",
        "nome",
        "sistema__nome",
        "bloco_pai__nome",
        "ativo",
    )
    filter_fields = (
        "unidade__nome",
        "nome",
        "sistema__nome",
        "unidade",
        "bloco_pai__nome",
        "ativo",
    )
    ordering_fields = [
        "nome",
        "unidade__nome",
        "bloco_pai__nome",
        "sistema__nome",
        "ativo",
    ]
    ordering = ["nome", "ativo"]

    def create(self, request, *args, **kwargs):
        requisicao = request.data

        if self.check_nome_bloco(requisicao):
            return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)
        if self.check_registro_pai_excluido(requisicao):
            return Response(
                {
                    "non_field_errors": "Não é possível criar um bloco relacionado ao item selecionado."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(BlocoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, pk, *args, **kwargs):
        requisicao = request.data
        try:
            if (
                requisicao.get("bloco_pai") or requisicao.get("unidade")
            ) and self.check_registro_pai(requisicao):
                return Response(
                    {"non_field_errors": "Edição do registro pai não é permitida."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if Base().check_registro_excluido(Bloco, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Bloco, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not requisicao.get("ativo") and self.check_bloco_pai_exists(pk):
                return Response(
                    {
                        "non_field_errors": "Não foi possível inativar bloco. Há bloco(s) filho ativo relacionado."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not requisicao.get("ativo") and self.check_cela_vinculada_update(pk):
                return Response(
                    {
                        "non_field_errors": "Não foi possível inativar bloco. Há cela(s) ativa relacionada."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if self.check_nome_bloco(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

            return super(BlocoViewSet, self).update(request, *args, **kwargs)

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if Base().check_registro_excluido(Bloco, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_bloco_pai_exists(pk):
                return Response(
                    {
                        "non_field_errors": "Não foi possível excluir bloco. Há bloco(s) filho ativo relacionado."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_cela_vinculada_destroy(pk):
                return Response(
                    {
                        "non_field_errors": "Não foi possível excluir bloco. Há cela(s) filha(a) relacionada."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_bloco_filho(pk):
                return Response(
                    {
                        "non_field_errors": "Não foi possível excluir bloco. Há bloco(s) filho(a) relacionado."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Bloco.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(BlocoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in Bloco.objects.filter(Q(excluido=False)):
            bloco_list = list()
            bloco_list.append(trata_campo(query.nome))
            bloco_list.append(trata_campo(query.sistema.nome))
            bloco_list.append(trata_campo(query.unidade.nome))
            bloco_list.append(
                trata_campo(query.bloco_pai.nome) if query.bloco_pai else ""
            )

            for item in bloco_list:
                if busca in item:
                    queryset |= Bloco.objects.filter(pk=query.pk)
                    break

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_registro_pai(self, requisicao):
        diff = False
        bloco_dict = (
            Bloco.objects.filter(Q(id=requisicao["id"]))
            .values("bloco_pai_id", "unidade_id")
            .first()
        )
        if requisicao.get("bloco_pai"):
            diff = bloco_dict["bloco_pai_id"] != uuid.UUID(requisicao["bloco_pai"])
        if diff:
            return diff
        return bloco_dict["unidade_id"] != uuid.UUID(requisicao["unidade"])

    def check_bloco_inativo(self, requisicao):
        return Bloco.objects.filter(
            Q(id=requisicao["bloco"]) & Q(ativo=False) & Q(excluido=False)
        )

    def check_bloco(self, requisicao):
        return Bloco.objects.filter(
            Q(id=requisicao["id"]) & Q(ativo=False) & Q(excluido=False)
        )

    def check_registro_pai_excluido(self, requisicao):
        pai_excluido = Unidade.objects.filter(
            Q(id=requisicao["unidade"], excluido=True)
        ).exists()
        if not pai_excluido and requisicao.get("bloco_pai"):
            pai_excluido = Bloco.objects.filter(
                Q(id=requisicao["bloco_pai"], excluido=True)
            ).exists()
        return pai_excluido

    def check_bloco_exists(self, requisicao):
        bloco = check_duplicidade(requisicao.get("nome"))
        return Bloco.objects.filter(
            Q(bloco_id=requisicao.get("id"), nome__unaccent__iexact=bloco)
            & (~Q(id=requisicao.get("id")) & Q(excluido=False))
        )

    def check_bloco_pai_exists(self, pk):
        return Bloco.objects.filter(
            bloco_pai_id=pk, ativo=True, excluido=False
        ).exists()

    def check_cela_vinculada_destroy(self, pk):
        return Cela.objects.filter(bloco_id=pk, excluido=False).exists()

    def check_cela_vinculada_update(self, pk):
        return Cela.objects.filter(bloco_id=pk, ativo=True, excluido=False).exists()

    def check_nome_bloco(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return Bloco.objects.filter(
            Q(
                bloco_pai_id=requisicao.get("bloco_pai"),
                unidade_id=requisicao.get("unidade"),
                nome__iexact=nome,
            )
            & ~Q(id=requisicao.get("id"))
            & Q(excluido=False)
        )

    def check_bloco_filho(self, pk):
        return Bloco.objects.filter(bloco_pai=pk, excluido=False).exists()

    def perform_create(self, serializer):
        unidade_id = self.request.data["unidade"]
        sistema = Unidade.objects.filter(id=unidade_id).values("sistema_id").first()
        serializer.save(
            usuario_cadastro=user.get_user(self), sistema_id=sistema["sistema_id"]
        )

    def perform_update(self, serializer):
        unidade_id = self.request.data["unidade"]
        sistema = Unidade.objects.filter(id=unidade_id).values("sistema_id").first()
        serializer.save(
            usuario_edicao=user.get_user(self),
            sistema_id=sistema["sistema_id"],
            updated_at=datetime.now(),
        )


class CelaViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = CelaSerializer
    pagination_class = Paginacao
    queryset = Cela.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = (
        "unidade__nome",
        "sistema__nome",
        "bloco__nome",
        "nome",
        "capacidade",
        "ativo",
    )
    filter_fields = (
        "unidade__nome",
        "sistema__nome",
        "bloco__nome",
        "nome",
        "capacidade",
        "ativo",
    )
    ordering_fields = (
        "nome",
        "capacidade",
        "ativo",
        "bloco__nome",
        "unidade__nome",
        "sistema__nome",
    )
    ordering = ("nome", "bloco__nome", "unidade__nome", "sistema__nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_bloco_excluido(requisicao):
                return Response(
                    {
                        "non_field_errors": "Não é permitido realizar associação a este bloco"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_bloco_inativo(requisicao):
                return Response(
                    {"non_field_errors": "Bloco informado está inativo"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_cela_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(CelaViewSet, self).create(request, *args, **kwargs)

    def update(self, request, pk, *args, **kwargs):
        try:
            requisicao = request.data
            if requisicao.get("bloco") and self.check_bloco(requisicao):
                return Response(
                    {"non_field_errors": "Edição de Bloco não é permitido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_excluido(Cela, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Cela, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_cela_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(CelaViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if Base().check_registro_excluido(Cela, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Cela.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(CelaViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in Cela.objects.filter(Q(excluido=False)):
            cela_list = list()
            cela_list.append(trata_campo(query.nome))
            cela_list.append(trata_campo(query.sistema.nome))
            cela_list.append(trata_campo(query.unidade.nome))
            cela_list.append(trata_campo(query.bloco.nome))
            cela_list.append(trata_campo(query.capacidade))
            cela_list.append(trata_campo(query.observacao))

            for item in cela_list:
                if busca in item:
                    queryset |= Cela.objects.filter(pk=query.pk)
                    break

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_bloco_inativo(self, requisicao):
        return Bloco.objects.filter(Q(id=requisicao["bloco"], ativo=False))

    def check_bloco(self, requisicao):
        cela = Cela.objects.filter(Q(id=requisicao["id"])).values("bloco_id").first()
        return cela["bloco_id"] != uuid.UUID(requisicao["bloco"])

    def check_bloco_excluido(self, requisicao):
        return Bloco.objects.filter(Q(id=requisicao["bloco"], excluido=True))

    def check_cela_exists(self, requisicao):
        cela = check_duplicidade(requisicao.get("nome"))
        return Cela.objects.filter(
            Q(bloco_id=requisicao.get("bloco"), nome__iexact=cela)
            & (~Q(id=requisicao.get("id")) & ~Q(excluido=True))
        )

    def perform_create(self, serializer):
        bloco_id = self.request.data["bloco"]
        unidade = Bloco.objects.filter(id=bloco_id).values("unidade_id").first()
        sistema = (
            Unidade.objects.filter(id=unidade["unidade_id"])
            .values("sistema_id")
            .first()
        )
        serializer.save(
            usuario_cadastro=user.get_user(self),
            unidade_id=unidade["unidade_id"],
            sistema_id=sistema["sistema_id"],
        )

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        if requisicao.get("bloco"):
            unidade = Bloco.objects.filter(id=requisicao.get("bloco")).values("unidade_id").first()
            sistema = (
                Unidade.objects.filter(id=unidade["unidade_id"])
                .values("sistema_id")
                .first()
            )
            kwargs["unidade_id"] = unidade["unidade_id"]
            kwargs["sistema_id"] = unidade["sistema_id"]
        kwargs["updated_id"] = datetime.now()
        kwargs["usuario_edicao"] = user.get_user(self)
        serializer.save(**kwargs)


class DefeitoCelaViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = DefeitoCelaSerializer
    pagination_class = Paginacao
    queryset = DefeitoCela.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("defeito__descricao", "cela__nome", "data_criacao", "observacao")
    filter_fields = ("defeito__descricao", "cela__nome", "data_criacao", "observacao")
    ordering_fields = ("data_criacao", "ativo")
    ordering = ("data_criacao", "ativo")

    def create(self, request, *args, **kwargs):
        requisicao = request.data
        if self.check_cela(requisicao["cela"]):
            return Response(
                {"non_field_errors": "Esta cela não pode ser associada ao Defeito."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if self.check_defeito_cela(requisicao):
            return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)

        return super(DefeitoCelaViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        requisicao = request.data
        if Base().check_registro_excluido(DefeitoCela, requisicao["id"]):
            return Response(
                {"non_field_errors": mensagens.NAO_PERMITIDO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Base().check_registro_inativo(DefeitoCela, requisicao):
            return Response(
                {"non_field_errors": mensagens.INATIVO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if self.check_defeito_cela(requisicao):
            return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)
        return super(DefeitoCelaViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(DefeitoCelaViewSet).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))

        for query in DefeitoCela.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            defeito = trata_campo(query.defeito.descricao)

            if busca in nome or busca in defeito:
                queryset |= Cela.objects.filter(pk=query.pk)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if Base().check_registro_excluido(DefeitoCela, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            DefeitoCela.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def check_defeito_cela(self, requisicao):
        defeito = check_duplicidade(requisicao.get("descricao"))
        return DefeitoCela.objects.filter(
            Q(descricao__unaccent__iexact=defeito)
            & ~Q(id=requisicao.get("id"))
            & Q(excluido=False)
        )

    def check_cela(self, id):
        return Cela.objects.filter(Q(id=id) & (Q(excluido=True) | Q(ativo=False)))

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class DefeitoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = DefeitoSerializer
    pagination_class = Paginacao
    queryset = Defeito.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("descricao", "ativo")
    filter_fields = ("descricao", "ativo")
    ordering_fields = ("descricao", "ativo")
    ordering = ("descricao", "ativo")

    def create(self, request, *args, **kwargs):
        requisicao = request.data
        try:
            if self.check_defeito(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(DefeitoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        requisicao = request.data
        try:
            if Base().check_registro_excluido(Defeito, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Defeito, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_defeito(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            return super(DefeitoViewSet, self).update(request, *args, **kwargs)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):

        try:
            if Base().check_registro_excluido(Defeito, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_registro_filho(pk):
                return Response(
                    {
                        "non_field_errors": "Operação não permitida, existes Cela associadas a este Defeito."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Defeito.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(DefeitoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in Defeito.objects.filter(Q(excluido=False)):
            descricao = trata_campo(query.descricao)

            if busca in descricao:
                queryset |= Defeito.objects.filter(pk=query.pk)
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_defeito(self, requisicao):
        defeito = check_duplicidade(requisicao.get("descricao"))
        return Defeito.objects.filter(
            Q(descricao__iexact=defeito)
            & ~Q(id=requisicao.get("id"))
            & Q(excluido=False)
        ).exists()

    def check_registro_filho(self, id):
        return DefeitoCela.objects.filter(Q(defeito_id=id)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class DesignacaoFuncaoServidorViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = DesignacaoFuncaoServidorSerializer
    pagination_class = Paginacao
    queryset = DesignacaoFuncaoServidor.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("descricao", "data_cadastro")
    filter_fields = ("descricao", "data_cadastro")
    ordering_fields = ("descricao",)
    ordering = ("descricao",)


class ReparoCelaViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = ReparoCelaSerializer
    pagination_class = Paginacao
    queryset = ReparoCela.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("defeito_cela__defeito", "data_reparo")
    filter_fields = ("defeito_cela__defeito", "data_reparo")
    ordering_fields = ("data_reparo",)
    ordering = ("data_reparo",)


class SistemaPenalViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = SistemaPenalSerializer
    pagination_class = Paginacao
    queryset = SistemaPenal.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "sigla", "ativo", "pais__nome", "estado__nome")
    filter_fields = ("nome", "sigla", "ativo")
    ordering_fields = ("nome", "sigla", "ativo", "pais__nome", "estado__nome", "ativo")
    ordering = ("nome", "sigla", "ativo", "pais__nome", "estado__nome", "ativo")

    def create(self, request, *args, **kwargs):
        requisicao = request.data
        try:
            if self.check_sistema_penal(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            return super(SistemaPenalViewSet, self).create(request, *args, **kwargs)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        requisicao = request.data
        if Base().check_registro_excluido(SistemaPenal, requisicao["id"]):
            return Response(
                {"non_field_errors": mensagens.NAO_PERMITIDO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Base().check_registro_inativo(SistemaPenal, requisicao):
            return Response(
                {"non_field_errors": mensagens.INATIVO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if self.check_sistema_penal(requisicao):
            return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)
        if not requisicao.get("ativo") and self.check_registros_filhos(
            requisicao["id"]
        ):
            return Response(
                {
                    "non_field_errors": "Operação não permitida, existes Unidades associadas a este Sistema Penal."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super(SistemaPenalViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if Base().check_registro_excluido(SistemaPenal, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_registros_filhos_destroy(pk):
                return Response(
                    {
                        "non_field_errors": "Operação não permitida, existes Unidades associadas a este Sistema Penal."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            SistemaPenal.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(SistemaPenalViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in SistemaPenal.objects.filter(Q(excluido=False)):
            sistema_list = list()
            sistema_list.append(trata_campo(query.nome))
            sistema_list.append(trata_campo(query.sigla))
            sistema_list.append(trata_campo(query.pais.nome) if query.pais else "")
            sistema_list.append(trata_campo(query.estado.nome) if query.estado else "")

            for item in sistema_list:
                if busca in item:
                    queryset |= SistemaPenal.objects.filter(pk=query.pk)
                    break

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = queryset.distinct()

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_sistema_penal(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        sistema_id = requisicao.get("id") if requisicao.get("id") else None
        return SistemaPenal.objects.filter(
            Q(nome__iexact=nome) & (~Q(id=sistema_id) & ~Q(excluido=True))
        ).exists()

    def check_registros_filhos(self, id):
        return Unidade.objects.filter(
            Q(sistema_id=id) & Q(ativo=True) & Q(excluido=False)
        ).exists()

    def check_registros_filhos_destroy(self, id):
        return Unidade.objects.filter(Q(sistema_id=id) & Q(excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class UnidadeViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = UnidadeSerializer
    pagination_class = Paginacao
    queryset = Unidade.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = (
        "id",
        "nome",
        "sigla",
        "ativo",
        "estado__nome",
        "sistema__nome",
        "cidade__nome",
        "sistema__id",
    )
    filter_fields = (
        "id",
        "nome",
        "sigla",
        "ativo",
        "estado__nome",
        "sistema__nome",
        "cidade__nome",
        "sistema__id",
    )
    ordering_fields = (
        "nome",
        "sigla",
        "ativo",
        "estado__nome",
        "sistema__nome",
        "cidade__nome",
    )
    ordering = ("nome", "sigla", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_unidade(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if not self.check_cidade(requisicao):
                return Response(
                    {"non_field_errors": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(UnidadeViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(Unidade, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Unidade, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_unidade(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if not self.check_cidade(requisicao):
                return Response(
                    {"non_field_errors": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not requisicao.get("ativo") and self.check_registros_filhos(
                requisicao["id"]
            ):
                return Response(
                    {
                        "non_field_errors": "Operação não permitida, existes registo(s) filho(s) associado a esta Unidade."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(UnidadeViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if Base().check_registro_excluido(Unidade, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_registros_filhos_destroy(pk):
                return Response(
                    {
                        "non_field_errors": "Operação não permitida, existes registo(s) filho(s) associado a esta Unidade."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Unidade.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(UnidadeViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in Unidade.objects.filter(Q(excluido=False)):
            unidade_list = list()
            unidade_list.append(trata_campo(query.nome))
            unidade_list.append(trata_campo(query.sigla))
            unidade_list.append(trata_campo(query.sistema.nome))
            unidade_list.append(trata_campo(query.estado.nome) if query.estado else "")

            for item in unidade_list:
                if busca in item:
                    queryset |= Unidade.objects.filter(pk=query.pk)
                    break

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_unidade(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        unidade_id = requisicao.get("id") if requisicao.get("id") else None
        return Unidade.objects.filter(
            Q(
                sistema_id=requisicao.get("sistema"),
                cidade_id=requisicao.get("cidade"),
                estado_id=requisicao.get("estado"),
                nome__iexact=nome,
            )
            & ~Q(id=unidade_id)
            & ~Q(excluido=True)
        ).exists()

    def check_cidade(self, requisicao):
        return Cidade.objects.filter(
            Q(id=requisicao["cidade"], estado_id=requisicao["estado"])
        ).exists()

    def check_registros_filhos(self, id):
        children = None
        children = Bloco.objects.filter(
            Q(unidade_id=id) & (Q(ativo=True) & Q(excluido=False))
        ).exists()
        return children

    def check_registros_filhos_destroy(self, id):
        children = None
        children = Bloco.objects.filter(Q(unidade_id=id) & Q(excluido=False)).exists()
        return children

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class PrisionalViewSet(GenericViewSet):
    queryset = SistemaPenal.objects.all()
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = SistemaPenalSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)

    def __init__(self, *args, **kwargs):
        super(PrisionalViewSet, self).__init__(*args, **kwargs)

    def get_cela(self, cela_id):

        cela = (
            Cela.objects.filter(id=cela_id, excluido=False)
            .values("id", "bloco_id", "nome")
            .first()
        )
        cela_dict = {
            "id": cela["id"],
            "name": cela["nome"],
            "type": "Cela",
            "key": rf"CE{cela['id']}",
        }
        bloco_id = cela["bloco_id"]

        return cela_dict, bloco_id

    def get_bloco(self, children=None, bloco_id=None):

        bloco = (
            Bloco.objects.filter(id=bloco_id, excluido=False)
            .values("id", "nome", "bloco_pai_id", "unidade_id")
            .first()
        )
        bloco_dict = {
            "id": bloco["id"],
            "name": bloco["nome"],
            "type": "Bloco",
            "key": rf"BO{bloco['id']}",
        }
        if children:
            bloco_dict["children"] = [children]
        if bloco.get("bloco_pai_id"):
            bloco_dict, unidade = self.get_bloco(bloco_dict, bloco.get("bloco_pai_id"))

        return bloco_dict, bloco.get("unidade_id")

    def get_unidade(self, children, unidade_id):

        unidade = (
            Unidade.objects.filter(id=unidade_id, excluido=False)
            .values("id", "nome", "sistema_id")
            .first()
        )
        unidade_dict = {
            "id": unidade["id"],
            "name": unidade["nome"],
            "type": "Unidade",
            "key": rf"UN{unidade['id']}",
            "children": [children],
        }

        return unidade_dict, unidade.get("sistema_id")

    def get_sistema(self, children, sistema_id):

        sistema = (
            SistemaPenal.objects.filter(id=sistema_id, excluido=False)
            .values("id", "nome")
            .first()
        )
        sistema_dict = {
            "id": sistema["id"],
            "name": sistema["nome"],
            "type": "Sistema Penal",
            "key": rf"SP{sistema['id']}",
            "children": [children],
        }

        return sistema_dict

    @action(
        detail=False,
        methods=["get"],
        url_path=r"treeview-cela/(?P<cela_id>[^/.]+)",
        url_name="treeview-cela",
    )
    def get_arvore_celas(self, request, cela_id):
        try:
            tree = list()
            cela_dict, bloco_id = self.get_cela(cela_id)
            bloco_treeview, unidade_id = self.get_bloco(cela_dict, bloco_id)
            unidade_treeview, sistema_id = self.get_unidade(bloco_treeview, unidade_id)
            tree.append(self.get_sistema(unidade_treeview, sistema_id))

            return Response(tree, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG3}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=False,
        methods=["get"],
        url_path=r"treeview-bloco/(?P<bloco_id>[^/.]+)",
        url_name="treeview-bloco",
    )
    def get_arvore_blocos(self, request, bloco_id):
        try:
            tree = list()
            bloco_treeview, unidade_id = self.get_bloco(bloco_id=bloco_id)
            unidade_treeview, sistema_id = self.get_unidade(bloco_treeview, unidade_id)
            tree.append(self.get_sistema(unidade_treeview, sistema_id))

            return Response(tree, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG3}, status=status.HTTP_404_NOT_FOUND
            )

    def sistema_penal(self, filter_celas=False):
        sistemas_penais = SistemaPenal.objects.filter(
            Q(ativo=True) & Q(excluido=False)
        ).values()
        items = list()
        for penal in sistemas_penais:
            penal_dict = {
                "id": penal["id"],
                "name": penal["nome"],
                "type": "Sistema Penal",
                "key": "SP{}".format(penal["id"]),
                "children": self.unidades_custodia(penal, filter_celas=filter_celas),
            }
            items.append(penal_dict)
        return items

    def unidades_custodia(self, penal, filter_celas):

        unidades_custodia = list()
        unidades = Unidade.objects.filter(
            Q(sistema=penal["id"]) & Q(ativo=True) & Q(excluido=False)
        ).values()
        for unidade in unidades:
            unidade = {
                "id": unidade["id"],
                "name": unidade["nome"],
                "sistema": penal["id"],
                "sistema_nome": penal["nome"],
                "type": "Unidade",
                "key": "UN{}".format(unidade["id"]),
            }
            unidade["children"] = self.get_bloco_unidade(
                unidade_dict=unidade, filter_celas=filter_celas
            )
            unidades_custodia.append(unidade)
        return unidades_custodia

    def get_celas_bloco(self, bloco, unidade_dict):
        celas = list()
        cela_list = Cela.objects.filter(
            bloco=bloco["id"], ativo=True, excluido=False
        ).values()
        for cela in cela_list:
            cela_id = cela["id"]
            cela_json = {
                "id": cela["id"],
                "name": cela["nome"],
                "type": "Cela",
                "sistema": unidade_dict["sistema"],
                "sistema_nome": unidade_dict["sistema_nome"],
                "unidade": unidade_dict["id"],
                "unidade_nome": unidade_dict["name"],
                "bloco": bloco["id"],
                "bloco_nome": bloco["nome"],
                "key": rf"CE{cela_id}",
            }
            celas.append(cela_json)
        return celas

    def get_bloco_unidade(self, unidade_dict, comeco=None, filter_celas=False):
        lista = []

        blocos = Bloco.objects.filter(
            Q(unidade=unidade_dict["id"]) & Q(ativo=True) & Q(excluido=False)
        ).values()
        for bloco in blocos:
            if bloco["bloco_pai_id"] == comeco:
                bloco_json = {
                    "id": bloco["id"],
                    "name": bloco["nome"],
                    "type": "Bloco",
                    "key": "BO{}".format(bloco["id"]),
                    "sistema": unidade_dict["sistema"],
                    "sistema_nome": unidade_dict["sistema_nome"],
                    "unidade": unidade_dict["id"],
                    "unidade_nome": unidade_dict["name"],
                    "children": self.get_bloco_unidade(
                        unidade_dict, bloco["id"], filter_celas=filter_celas
                    ),
                }

                if filter_celas:
                    celas_list = self.get_celas_bloco(bloco, unidade_dict)
                    if celas_list:
                        bloco_json["children"].extend(celas_list)

                lista.append(bloco_json)

        return lista

    @action(
        detail=False,
        methods=["get"],
        url_path="bloco-alocacao",
        url_name="bloco-alocacao",
    )
    def bloco_alocacao(self, request):
        items = self.sistema_penal()
        return Response(items, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="cela-alocacao",
        url_name="cela-alocacao",
    )
    def cela_alocacao(self, request):
        items = self.sistema_penal(filter_celas=True)
        return Response(items, status=status.HTTP_200_OK)


class UsuarioSistemaViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = UsuarioSistemaSerializer
    pagination_class = Paginacao
    queryset = UsuarioSistema.objects.all()
    search_fields = ("setor__nome", "pessoa__nome", "data_cadastro")
    filter_fields = ("setor__nome", "pessoa__nome", "data_cadastro")
    ordering_fields = ("pessoa__nome",)
    ordering = ("pessoa__nome",)
