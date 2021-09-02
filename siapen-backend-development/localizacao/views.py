from django.db.models import Q
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from util.paginacao import Paginacao
from util.busca import trata_campo
from localizacao.serializers import PaisSerializer
from localizacao.serializers import EstadoSerializer
from localizacao.serializers import CidadeSerializer
from localizacao.models import Pais, Estado, Cidade
from itertools import chain


class PaisViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = PaisSerializer
    pagination_class = Paginacao
    queryset = Pais.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "sigla")
    filter_fields = ("nome", "sigla")
    ordering_fields = ("nome",)
    ordering = ("nome",)

    def filter_queryset(self, queryset):
        queryset = super(PaisViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))

        for query in Pais.objects.all():
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= Pais.objects.filter(pk=query.pk)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)
        queryset_br = None
        queryset_br = queryset.filter(Q(nome="Brasil"))
        if queryset_br:
            queryset = queryset.filter(~Q(nome="Brasil"))
            queryset_ordenado = list(chain(queryset_br, queryset))
        else:
            queryset_ordenado = queryset

        return queryset_ordenado


class EstadoViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = EstadoSerializer
    pagination_class = Paginacao
    queryset = Estado.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "sigla")
    filter_fields = ("pais", "sigla")
    ordering_fields = ("nome",)
    ordering = ("nome",)


class CidadeViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = CidadeSerializer
    pagination_class = Paginacao
    queryset = Cidade.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("estado", "estado__sigla", "nome")
    ordering_fields = ("nome",)
    ordering = ("nome",)

    # Sobrescrevendo o método de listar
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        response_list = serializer.data

        return Response(response_list)
