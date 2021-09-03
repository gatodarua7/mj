from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from orcrim.serializers import (
    FaccaoCargoSerializer,
    FaccaoPessoaSerializer,
    FaccaoSerializer,
    FaccaoGrupoSerializer,
)
from util.paginacao import Paginacao
from util.busca import trata_campo, trata_campo_ativo, check_duplicidade
from rest_framework import viewsets, status
from orcrim.models import FaccaoPessoa, Faccao, FaccaoGrupo, FaccaoCargo
from util import mensagens, user
from datetime import datetime
from core.views import Base


class FaccaoPessoaViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = FaccaoPessoaSerializer
    pagination_class = Paginacao
    queryset = FaccaoPessoa.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("faccao__nome", "pessoa__nome")
    filter_fields = (
        "faccao__nome",
        "pessoa__nome",
        "data_filiacao_faccao",
        "data_desfiliacao_faccao",
    )
    ordering_fields = (
        "faccao__nome",
        "pessoa__nome",
        "data_filiacao_faccao",
        "data_desfiliacao_faccao",
        "ativo",
    )
    ordering = ["faccao__nome", "ativo"]

    def perform_create(self, serializer):
        user = None

        if self.request and hasattr(self.request, "user"):
            user = self.request.user
        serializer.save(usuario_cadastro=user)


class FaccaoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = FaccaoSerializer
    pagination_class = Paginacao
    queryset = Faccao.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "sigla", "ativo")
    filter_fields = ("nome", "sigla", "ativo")
    ordering_fields = ["nome", "sigla", "ativo"]

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_faccao(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(FaccaoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base().check_registro_exists(Faccao, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if self.check_faccao(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_inativo(Faccao, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if requisicao.get("ativo") is False and not self.inativa_filhos(
                requisicao.get("id")
            ):
                return Response(
                    {"non_field_errors": "Falha ao inativar registros."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(FaccaoViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Faccao, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Faccao, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_faccao_grupo(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_faccao_cargos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Faccao.objects.filter(id=pk).update(
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
        queryset = super(FaccaoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in Faccao.objects.filter(Q(excluido=False)):
            facao_list = list()
            facao_list.append(trata_campo(query.nome))
            facao_list.append(trata_campo(query.sigla))
            facao_list.append(trata_campo(query.observacao))
            facao_list.extend([trata_campo(pais.nome) for pais in query.pais.all()])
            facao_list.extend(
                [trata_campo(estado.nome) for estado in query.estado.all()]
            )

            for faccao in facao_list:
                if busca in faccao:
                    queryset |= Faccao.objects.filter(pk=query.pk)

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def inativa_filhos(self, id):
        try:
            FaccaoGrupo.objects.filter(faccao_id=id, excluido=False, ativo=True).update(
                ativo=False
            )
            FaccaoCargo.objects.filter(faccao_id=id, excluido=False, ativo=True).update(
                ativo=False
            )
            return True
        except Exception:
            return False

    def check_faccao(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        sigla = check_duplicidade(requisicao.get("sigla"))
        faccao_id = requisicao.get("id") if requisicao.get("id") else None
        return Faccao.objects.filter(
            Q(nome__iexact=nome, sigla__iexact=sigla, excluido=False) & ~Q(id=faccao_id)
        ).exists()

    def check_faccao_grupo(self, id):
        return FaccaoGrupo.objects.filter(Q(faccao_id=id, excluido=False)).exists()

    def check_faccao_cargos(self, id):
        return FaccaoCargo.objects.filter(Q(faccao_id=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class FaccaoGrupoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = FaccaoGrupoSerializer
    pagination_class = Paginacao
    queryset = FaccaoGrupo.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("faccao__nome", "nome", "observacao", "ativo")
    filter_fields = ("faccao__nome", "nome", "observacao", "ativo")
    ordering_fields = ("faccao__nome", "nome", "observacao", "ativo")
    ordering = ("faccao__nome", "nome", "observacao", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_faccao_grupo(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(FaccaoGrupoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base().check_registro_exists(FaccaoGrupo, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(FaccaoGrupo, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_faccao_grupo(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if requisicao.get("ativo") and not self.check_faccao(requisicao):
                return Response(
                    {
                        "detail": "Não é possível realizar esta operação. A Facção está inativa."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(FaccaoGrupo, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(FaccaoGrupoViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(FaccaoGrupoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in FaccaoGrupo.objects.filter(Q(excluido=False)):
            facao_grupo = list()
            facao_grupo.append(trata_campo(query.nome))
            facao_grupo.append(trata_campo(query.faccao.nome))
            facao_grupo.append(trata_campo(query.faccao.sigla))
            facao_grupo.append(trata_campo(query.observacao))

            for faccao in facao_grupo:
                if busca in faccao:
                    queryset |= FaccaoGrupo.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(FaccaoGrupo, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(FaccaoGrupo, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            FaccaoGrupo.objects.filter(id=pk).update(
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

    def check_faccao_grupo(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return FaccaoGrupo.objects.filter(
            Q(nome__iexact=nome, faccao_id=requisicao.get("faccao"), excluido=False)
            & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_faccao(self, requisicao):
        faccao = FaccaoGrupo.objects.filter(Q(id=requisicao.get("id"))).first()
        return Faccao.objects.filter(
            Q(id=faccao.faccao_id, ativo=True, excluido=False)
        ).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class FaccaoCargoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = FaccaoCargoSerializer
    pagination_class = Paginacao
    queryset = FaccaoCargo.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("faccao__nome", "nome", "observacao", "ativo")
    filter_fields = ("faccao__nome", "nome", "observacao", "ativo")
    ordering_fields = ("faccao__nome", "nome", "observacao", "ativo")
    ordering = ("faccao__nome", "nome", "observacao", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_faccao_cargo(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(FaccaoCargoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base().check_registro_exists(FaccaoCargo, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(FaccaoCargo, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_faccao_cargo(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if requisicao.get("ativo") and not self.check_faccao(requisicao):
                return Response(
                    {
                        "detail": "Não é possível realizar esta operação. A Facção está inativa."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(FaccaoCargo, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(FaccaoCargoViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(FaccaoCargoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in FaccaoCargo.objects.filter(Q(excluido=False)):
            facao_cargo = list()
            facao_cargo.append(trata_campo(query.nome))
            facao_cargo.append(trata_campo(query.faccao.nome))
            facao_cargo.append(trata_campo(query.faccao.sigla))
            facao_cargo.append(trata_campo(query.observacao))

            for faccao in facao_cargo:
                if busca in faccao:
                    queryset |= FaccaoCargo.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(FaccaoCargo, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(FaccaoCargo, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            FaccaoCargo.objects.filter(id=pk).update(
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

    def check_faccao_cargo(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return FaccaoCargo.objects.filter(
            Q(nome__iexact=nome, faccao_id=requisicao.get("faccao"), excluido=False)
            & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_faccao(self, requisicao):
        faccao = FaccaoCargo.objects.filter(Q(id=requisicao.get("id"))).first()
        return Faccao.objects.filter(
            Q(id=faccao.faccao_id, ativo=True, excluido=False)
        ).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())
