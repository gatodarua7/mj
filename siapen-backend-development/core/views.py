from re import T
from django.db.models import Q
from django.db import transaction
from django.db import reset_queries
from rest_framework import status
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import LogSerializer
from .models import Log
from util.paginacao import Paginacao, paginacao_list, paginacao, ordena_lista
from util.busca import trata_campo, trata_campo_ativo, trata_telefone, check_duplicidade, formata_data, formata_data_hora
from rest_framework import status, viewsets

from util import mensagens, validador, user
from util.busca import (
    trata_campo,
    trata_campo_ativo,
    trata_telefone,
    check_duplicidade,
    formata_data,
    formata_data_hora,
    converte_string_data_hora
)
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import ast
from uuid import UUID


class LogViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = LogSerializer
    pagination_class = Paginacao
    queryset = Log.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("requested_at", "username_persistent", "method", "path", "status_code", "view_method")
    filter_fields = ("requested_at", "username_persistent", "method", "path", "status_code", "view_method")
    ordering_fields = ("requested_at", "username_persistent", "method","path", "status_code", "view_method")
    ordering = ("requested_at", "username_persistent", "method", "path", "status_code", "view_method")

    def filter_queryset(self, queryset):
        queryset = super(LogViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params
        data_inicio, hora_inicio, data_fim, hora_fim, data_hora_inicio, data_hora_fim = "", "", "", "", "", ""

        for key, value in parametros_busca.items():
            if key == "hora_inicio":
                hora_inicio = parametros_busca["hora_inicio"]
            if key == "data_inicio":
                data_inicio = parametros_busca["data_inicio"]
            if key == "data_fim":
                data_fim = parametros_busca["data_fim"]
            if key == "hora_fim":
                hora_fim = parametros_busca["hora_fim"]
        
        if parametros_busca.get('usuario'):
            queryset = queryset.filter(Q(username_persistent__contains=parametros_busca.get('usuario')))
        if parametros_busca.get('ip'):
            queryset = queryset.filter(Q(remote_addr__contains=parametros_busca.get('ip')))
        if parametros_busca.get('resposta'):
            queryset = queryset.filter(Q(response__contains=parametros_busca.get('resposta')))


        if data_inicio:
            data_hora_inicio = converte_string_data_hora(data_inicio, hora_inicio)

        if data_fim:
            if not hora_fim:
                hora_fim = "23:59"
            data_hora_fim = converte_string_data_hora(data_fim, hora_fim)

        if data_hora_inicio and data_hora_fim:
            queryset = queryset.filter(Q(requested_at__range=[data_hora_inicio, data_hora_fim]))
        elif data_hora_inicio:
            queryset = queryset.filter(Q(requested_at__gte=data_hora_inicio))
        elif data_hora_fim:
            queryset = queryset.filter(Q(requested_at__lte=data_hora_fim))

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

class Base():
    @staticmethod
    def check_registro_exists(classe, id):
        return classe.objects.filter(id=id).exists()

    @staticmethod
    def check_registro_excluido(classe, id):
        return classe.objects.filter(Q(id=id, excluido=True)).exists()

    @staticmethod
    def check_registro_inativo(classe, requisicao):
        return not requisicao.get("ativo") and classe.objects.filter(
            Q(id=requisicao.get("id"), ativo=False)
        )