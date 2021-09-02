from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from juridico.serializers import TituloLeiSerializer, NormasJuridicasSerializer
from juridico.models import TituloLei, NormasJuridicas
from movimentacao.models import PedidoInclusaoMotivos
from django.db.models import Q
from rest_framework import viewsets
from util.paginacao import Paginacao
from util import mensagens, user
from datetime import datetime
from util.busca import (
    trata_campo,
    trata_campo_ativo,
    check_duplicidade
)
from core.views import Base

class TituloLeiViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = TituloLeiSerializer
    pagination_class = Paginacao
    queryset = TituloLei.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "norma_juridica", "ativo")
    filter_fields = ("norma_juridica", "nome", "ativo")
    ordering_fields = ("nome", "norma_juridica", "ativo")
    ordering = ("nome", "norma_juridica", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_nome(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": "Erro na requisição"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(TituloLeiViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_nome(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_excluido(TituloLei, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except KeyError:
            return Response(
                {"non_field_errors": "Erro na requisição"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(TituloLeiViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(TituloLei, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(TituloLei, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_dependencia_registro(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            TituloLei.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(TituloLeiViewSet,
                         self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in TituloLei.objects.filter(Q(excluido=False)):
            titulos = list()
            titulos.append(trata_campo(query.nome))
            titulos.append(trata_campo(query.get_norma_juridica_display()))
            for titulo in titulos:
                if busca in titulo:
                    queryset |= TituloLei.objects.filter(pk=query.pk)
                    break

        if parametros_busca.get("norma_juridica"):
            queryset = queryset.filter(norma_juridica=parametros_busca.get("norma_juridica"))

        if ativo is not None:
            queryset = queryset.filter(Q(id=parametros_busca.get("titulo_id")) | Q(ativo=ativo))

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["usuario_edicao"] = user.get_user(self)
        kwargs["updated_at"] = datetime.now()
        if requisicao.get('motivo_inativacao'):
            kwargs["data_inativacao"] = datetime.now()
            kwargs["usuario_inativacao"] = user.get_user(self)
        elif requisicao.get('motivo_ativacao'):
            kwargs["data_ativacao"] = datetime.now()
            kwargs["usuario_ativacao"] = user.get_user(self)
        serializer.save(**kwargs)

    def check_nome(self, requisicao):
        """Verifica se existe registro com o mesmo nome (título)"""
        nome = check_duplicidade(requisicao.get("nome"))
        norma_juridica = check_duplicidade(requisicao.get("norma_juridica"))
        return TituloLei.objects.filter(Q(nome__iexact=nome, 
                                            norma_juridica__iexact=norma_juridica, 
                                            excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_dependencia_registro(self, id):
        return NormasJuridicas.objects.filter(Q(titulo=id, excluido=False)).exists()


class NormasJuridicasViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = NormasJuridicasSerializer
    pagination_class = Paginacao
    queryset = NormasJuridicas.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("norma_juridica", "descricao", "ativo")
    filter_fields = ("norma_juridica", "descricao", "ativo")
    ordering_fields = ("norma_juridica", "titulo", "descricao", "ativo")
    ordering = ("norma_juridica", "titulo", "descricao", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_normas_juridicas_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(NormasJuridicasViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        try:
            requisicao = request.data
            if Base().check_registro_excluido(NormasJuridicas, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(NormasJuridicas, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if self.check_normas_juridicas_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(NormasJuridicasViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(NormasJuridicas, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(NormasJuridicas, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_vinculos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            NormasJuridicas.objects.filter(id=pk).update(
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
        queryset = super(NormasJuridicasViewSet,
                         self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))
        nomas_id = list()
        if parametros_busca.get("norma_id"):
            nomas_id = parametros_busca['norma_id'].split(',')

        for query in NormasJuridicas.objects.filter(Q(excluido=False)):
            normas = list()
            normas.append(trata_campo(query.titulo.nome))
            normas.append(trata_campo(query.get_norma_juridica_display()))
            normas.append(trata_campo(query.descricao))
            for norma in normas:
                if busca in norma:
                    queryset |= NormasJuridicas.objects.filter(pk=query.pk)
                    break
      
        if parametros_busca.get("norma_juridica") and parametros_busca.get("titulo"):
            queryset = queryset.filter(norma_juridica=parametros_busca.get("norma_juridica"),
                                         titulo_id=parametros_busca.get("titulo"))

        if ativo is not None:
                queryset = queryset.filter(Q(id__in=nomas_id) | Q(ativo=ativo))

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_normas_juridicas_exists(self, requisicao):
        try:
            descricao = check_duplicidade(requisicao.get("descricao"))
            norma_juridica = check_duplicidade(
                requisicao.get("norma_juridica"))
            return NormasJuridicas.objects.filter(
                Q(titulo_id=requisicao.get("titulo"), 
                    norma_juridica__iexact=norma_juridica,
                    descricao__iexact=descricao)
                & (~Q(id=requisicao.get("id")) & Q(excluido=False))
            ).exists()
        except Exception:
            raise serializers.ValidationError({"non_field_errors": mensagens.MSG_ERRO})
    
    def check_vinculos(self, id):
        return PedidoInclusaoMotivos.objects.filter(descricao=id).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["usuario_edicao"] = user.get_user(self)
        kwargs["updated_at"] = datetime.now()
        if requisicao.get('motivo_inativacao'):
            kwargs["data_inativacao"] = datetime.now()
            kwargs["usuario_inativacao"] = user.get_user(self)
        elif requisicao.get('motivo_ativacao'):
            kwargs["data_ativacao"] = datetime.now()
            kwargs["usuario_ativacao"] = user.get_user(self)
        serializer.save(**kwargs)
