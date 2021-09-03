from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from social.serializers import (
    EstadoCivilSerializer,
    GrauDeInstrucaoSerializer,
    NecessidadeEspecialSerializer,
    OrientacaoSexualSerializer,
    ProfissaoSerializer,
    RacaSerializer,
    ReligiaoSerializer,
)
from util.paginacao import Paginacao
from util.busca import trata_campo, trata_campo_ativo, check_duplicidade
from rest_framework import viewsets, status
from cadastros.models import Pessoa
from pessoas.servidor.models import Servidor
from social.models import (
    EstadoCivil,
    GrauDeInstrucao,
    NecessidadeEspecial,
    OrientacaoSexual,
    Profissao,
    Raca,
    Religiao,
)
from util import mensagens, user
from core.views import Base
from datetime import datetime


class EstadoCivilViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = EstadoCivilSerializer
    pagination_class = Paginacao
    queryset = EstadoCivil.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("nome",)
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_estado_civil(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(EstadoCivilViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        try:
            requisicao = request.data
            if not Base().check_registro_exists(EstadoCivil, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(EstadoCivil, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_estado_civil(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_inativo(EstadoCivil, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(EstadoCivilViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(EstadoCivilViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in EstadoCivil.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= EstadoCivil.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(EstadoCivil, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(EstadoCivil, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_pessoa_estado_civil(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            EstadoCivil.objects.filter(id=pk).update(
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

    def check_estado_civil(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return EstadoCivil.objects.filter(
            Q(nome__iexact=nome, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_pessoa_estado_civil(self, id):
        pessoa = Pessoa.objects.filter(Q(estado_civil=id, excluido=False)).exists()
        if pessoa:
            return pessoa
        return Servidor.objects.filter(Q(estado_civil=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class GrauDeInstrucaoViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = GrauDeInstrucaoSerializer
    pagination_class = Paginacao
    queryset = GrauDeInstrucao.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("nome",)
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_grau_instrucao(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(GrauDeInstrucaoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base().check_registro_exists(GrauDeInstrucao, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(GrauDeInstrucao, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_grau_instrucao(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_inativo(GrauDeInstrucao, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(GrauDeInstrucaoViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(GrauDeInstrucaoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in GrauDeInstrucao.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= GrauDeInstrucao.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(GrauDeInstrucao, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(GrauDeInstrucao, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_pessoa_grau_instrucao(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            GrauDeInstrucao.objects.filter(id=pk).update(
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

    def check_grau_instrucao(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return GrauDeInstrucao.objects.filter(
            Q(nome__iexact=nome, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_pessoa_grau_instrucao(self, id):
        pessoa = Pessoa.objects.filter(Q(grau_instrucao=id, excluido=False)).exists()
        if pessoa:
            return pessoa
        return Servidor.objects.filter(Q(grau_instrucao=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class NecessidadeEspecialViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = NecessidadeEspecialSerializer
    pagination_class = Paginacao
    queryset = NecessidadeEspecial.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("nome",)
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_necessidade_especial(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(NecessidadeEspecialViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base().check_registro_exists(
                NecessidadeEspecial, requisicao.get("id")
            ):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(
                NecessidadeEspecial, requisicao.get("id")
            ):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_necessidade_especial(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_inativo(NecessidadeEspecial, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(NecessidadeEspecialViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(NecessidadeEspecialViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in NecessidadeEspecial.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= NecessidadeEspecial.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(NecessidadeEspecial, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(NecessidadeEspecial, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_pessoa_necessidade(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            NecessidadeEspecial.objects.filter(id=pk).update(
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

    def check_necessidade_especial(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return NecessidadeEspecial.objects.filter(
            Q(nome__iexact=nome, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_pessoa_necessidade(self, id):
        pessoa = Pessoa.objects.filter(
            Q(necessidade_especial=id, excluido=False)
        ).exists()
        if pessoa:
            return pessoa
        return Servidor.objects.filter(
            Q(necessidade_especial=id, excluido=False)
        ).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class OrientacaoSexualViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = OrientacaoSexualSerializer
    pagination_class = Paginacao
    queryset = OrientacaoSexual.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("nome",)
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_orientacao_sexual(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(OrientacaoSexualViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base().check_registro_exists(OrientacaoSexual, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(OrientacaoSexual, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_orientacao_sexual(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_inativo(OrientacaoSexual, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(OrientacaoSexualViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(OrientacaoSexualViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in OrientacaoSexual.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= OrientacaoSexual.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(OrientacaoSexual, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(OrientacaoSexual, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_pessoa_orientacao_sexual(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            OrientacaoSexual.objects.filter(id=pk).update(
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

    def check_orientacao_sexual(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return OrientacaoSexual.objects.filter(
            Q(nome__iexact=nome, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_pessoa_orientacao_sexual(self, id):
        pessoa = Pessoa.objects.filter(Q(orientacao_sexual=id, excluido=False)).exists()
        if pessoa:
            return pessoa
        return Servidor.objects.filter(Q(orientacao_sexual=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class ProfissaoViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = ProfissaoSerializer
    pagination_class = Paginacao
    queryset = Profissao.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("nome",)
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_profissao(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(ProfissaoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base().check_registro_exists(Profissao, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Profissao, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_profissao(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_inativo(Profissao, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(ProfissaoViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(ProfissaoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in Profissao.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= Profissao.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Profissao, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Profissao, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_pessoa_profissao(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Profissao.objects.filter(id=pk).update(
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

    def check_profissao(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return Profissao.objects.filter(
            Q(nome__iexact=nome, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_pessoa_profissao(self, id):
        return Pessoa.objects.filter(Q(profissao=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class RacaViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = RacaSerializer
    pagination_class = Paginacao
    queryset = Raca.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("nome",)
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_raca(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(RacaViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base.check_registro_exists(Raca, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Raca, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_raca(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_inativo(Raca, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(RacaViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(RacaViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in Raca.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= Raca.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Raca, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Raca, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_pessoa_raca(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Raca.objects.filter(id=pk).update(
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

    def check_raca(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return Raca.objects.filter(
            Q(nome__iexact=nome, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_pessoa_raca(self, id):
        pessoa = Pessoa.objects.filter(Q(raca=id, excluido=False)).exists()
        if pessoa:
            return pessoa
        return Servidor.objects.filter(Q(raca=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class ReligiaoViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = ReligiaoSerializer
    pagination_class = Paginacao
    queryset = Religiao.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("nome",)
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_religiao(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(ReligiaoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base().check_registro_exists(Religiao, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Religiao, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_religiao(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_inativo(Religiao, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(ReligiaoViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(ReligiaoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in Religiao.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= Religiao.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Religiao, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Religiao, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_pessoa_religiao(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Religiao.objects.filter(id=pk).update(
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

    def check_religiao(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return Religiao.objects.filter(
            Q(nome__iexact=nome, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_pessoa_religiao(self, id):
        pessoa = Pessoa.objects.filter(Q(religiao=id, excluido=False)).exists()
        if pessoa:
            return pessoa
        return Servidor.objects.filter(Q(religiao=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())
