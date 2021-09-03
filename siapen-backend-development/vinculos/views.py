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
from pessoas.interno.models import Contatos
from vinculos.serializers import TipoVinculoSerializer
from vinculos.models import TipoVinculo
from util.paginacao import Paginacao
from util import mensagens, user
from util.busca import trata_campo, trata_campo_ativo, check_duplicidade
from rest_framework import viewsets, status
from datetime import datetime
from core.views import Base


class TipoVinculoViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = TipoVinculoSerializer
    pagination_class = Paginacao
    queryset = TipoVinculo.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("nome",)
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_tipo_vinculo(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": "Erro na requisição"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(TipoVinculoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(TipoVinculo, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(TipoVinculo, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not Base().check_registro_exists(TipoVinculo, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if self.check_tipo_vinculo(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": "Erro na requisição"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(TipoVinculoViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(TipoVinculoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in TipoVinculo.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= TipoVinculo.objects.filter(pk=query.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(TipoVinculo, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(TipoVinculo, pk):
                return Response(
                    {"detail": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_vinculos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            TipoVinculo.objects.filter(id=pk).update(
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

    def check_tipo_vinculo(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return TipoVinculo.objects.filter(
            Q(nome__iexact=nome, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_vinculos(self, id):
        return Contatos.objects.filter(Q(tipo_vinculo_id=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())
