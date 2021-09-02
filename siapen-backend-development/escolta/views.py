from prisional.models import Unidade
from pessoas.servidor.models import Servidor
from movimentacao.models import PedidoInclusao
from re import T
from django.db import transaction
from django.db import reset_queries
from django.db.models import Q
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
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from escolta.serializers import (EscoltasSerializer)
from escolta.models import (Escoltas, VoosEscolta)
from util.paginacao import Paginacao, paginacao_list, paginacao, ordena_lista
from util.busca import (formata_data_hora, trata_campo, formata_hora, concatena_data_hora, 
                        formata_data, converte_string_data_hora, trata_telefone, cast_string_in_datetime)
from util.image import get_thumbnail
from rest_framework import status, viewsets
import ast

from util import mensagens, validador, user
from datetime import date, datetime, timezone, timedelta
from uuid import UUID
from core.views import Base

class EscoltasViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = EscoltasSerializer
    pagination_class = Paginacao
    queryset = Escoltas.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("created_at", "ativo")
    filter_fields = ("created_at", "ativo")
    ordering_fields = ("created_at", "numero_escolta", "tipo_escolta", "data_inicio_aerea", "hora_inicio_aerea",
                        "data_inicio_terrestre", "hora_inicio_terrestre", "responsavel", "fase_escolta_terrestre",
                        "fase_escolta_aerea")
    ordering = ("created_at", "ativo")

    def create(self, request, *args, **kwargs):
        requisicao = self.request.data
        if not requisicao.get('pedidos_inclusao'):
                return Response({"non_field_errors": mensagens.MSG36},
                                        status=status.HTTP_400_BAD_REQUEST)
        if requisicao.get('tipo_aeronave') == 'COMERCIAL' and not requisicao.get('voos'):
            return Response({"tipo_aeronave": mensagens.MSG_VOOS},
                                    status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            for p_inclusao in requisicao.get('pedidos_inclusao'):
                try:
                    pedido = PedidoInclusao.objects.select_for_update().get(pk=UUID(p_inclusao['id']))
                except Exception:
                    return Response({"non_field_errors": mensagens.MSG_ERRO},
                                    status=status.HTTP_400_BAD_REQUEST)
                if not self.check_pedido_aguardando_escolta(pedido):
                    return Response({"non_field_errors": "Há pedidos de inclusão nesta escolta já associados a outro agendamento."},
                                     status=status.HTTP_400_BAD_REQUEST)
                erro_data = dict()
                erro_data.update(self.check_data_inicio_escolta(requisicao, pedido))
                if erro_data:
                    return Response(erro_data, status=status.HTTP_400_BAD_REQUEST)
                pedido.aguardando_escolta = False
                pedido.save()
            self.request.data['fase_escolta_aerea'] = 'AGENDADA' if requisicao.get('data_inicio_aerea') else ""
            self.request.data['fase_escolta_terrestre'] = 'AGENDADA' if requisicao.get('data_inicio_terrestre') else ""
            self.request.data['numero_escolta'] = self.get_numero_escolta() if requisicao.get('responsavel') == 'DEPEN' else "-"
            self.request.data['tipo_escolta'] = 'INCLUSAO'
            return super(EscoltasViewSet, self).create(request, *args, **kwargs)


    def update(self, request, pk, *args, **kwargs):
        requisicao = self.request.data
        if not requisicao.get('pedidos_inclusao'):
            return Response({"non_field_errors": mensagens.MSG36},
                                    status=status.HTTP_400_BAD_REQUEST)
        pedidos_inclusao_list = [UUID(p_inclusao['id']) for p_inclusao in requisicao.get('pedidos_inclusao')]
        servidor_aerea_list = list()
        if requisicao.get('servidores_escolta_aerea'):
            servidor_aerea_list = [s.get('id') for s in requisicao.get('servidores_escolta_aerea')]
        servidor_terrestre_list = list()
        if requisicao.get('servidores_escolta_terrestre'):
            servidor_terrestre_list = [s.get('id') for s in requisicao.get('servidores_escolta_terrestre')]

        
        if requisicao.get('tipo_aeronave') == 'COMERCIAL' and not requisicao.get('voos'):
            return Response({"tipo_aeronave": mensagens.MSG_VOOS},
                                    status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            try:
                for p in pedidos_inclusao_list:
                    p_inclusao = PedidoInclusao.objects.select_for_update().get(pk=p)
                    erro_data = dict()
                    erro_data.update(self.check_data_inicio_escolta(requisicao, p_inclusao))
                    if erro_data:
                        return Response(erro_data, status=status.HTTP_400_BAD_REQUEST)
                    p_inclusao.aguardando_escolta = False
                    p_inclusao.save()
                for escolta in Escoltas.objects.filter(Q(id=UUID(pk))):
                    for pedido in escolta.pedidos_inclusao.all():
                        if pedido.pk not in pedidos_inclusao_list:
                            pedido_inclusao = PedidoInclusao.objects.select_for_update().get(pk=pedido.pk)
                            pedido_inclusao.aguardando_escolta = True
                            pedido_inclusao.save()
                    escolta.pedidos_inclusao.clear()
                    for pedidos_add in PedidoInclusao.objects.filter(id__in=pedidos_inclusao_list):
                        escolta.pedidos_inclusao.add(pedidos_add)
                    escolta.servidores_escolta_terrestre.clear()
                    for servidor in Servidor.objects.filter(id__in=servidor_terrestre_list):
                        escolta.servidores_escolta_terrestre.add(servidor)
                    escolta.servidores_escolta_aerea.clear()
                    for servidor in Servidor.objects.filter(id__in=servidor_aerea_list):
                        escolta.servidores_escolta_aerea.add(servidor)
            except Exception:
                return Response({"non_field_errors": mensagens.MSG_ERRO},
                                status=status.HTTP_400_BAD_REQUEST)
            self.request.data['fase_escolta_aerea'] = requisicao.get('fase_escolta_aerea') if requisicao.get('data_inicio_aerea') else ""
            self.request.data['fase_escolta_terrestre'] = requisicao.get('fase_escolta_terrestre') if requisicao.get('data_inicio_terrestre') else ""
            self.request.data['numero_escolta'] = self.get_numero_escolta() if requisicao.get('responsavel') == 'DEPEN' else "-"
            return super(EscoltasViewSet, self).update(request, *args, **kwargs)


    def destroy(self, request, pk, *args, **kwargs):
        if not Base().check_registro_exists(Escoltas, pk):
            return Response(
                {"detail": mensagens.NAO_ENCONTRADO},
                status=status.HTTP_404_NOT_FOUND,
            )
        if Base().check_registro_excluido(Escoltas, pk):
            return Response(
                {"non_field_errors": mensagens.NAO_PERMITIDO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            try:
                for escolta in Escoltas.objects.filter(Q(id=UUID(pk))):
                    for pedido in escolta.pedidos_inclusao.all():
                        pedido_inclusao = PedidoInclusao.objects.select_for_update().get(pk=pedido.pk)
                        pedido_inclusao.aguardando_escolta = True
                        pedido_inclusao.save()
                Escoltas.objects.filter(id=pk).update(
                        excluido=True,
                        usuario_exclusao=user.get_user(self),
                        delete_at=datetime.now(),
                    )
                return Response(status=status.HTTP_200_OK)
            except Exception:
                return Response({"non_field_errors": mensagens.MSG_ERRO},
                                status=status.HTTP_400_BAD_REQUEST)


    def filter_queryset(self, queryset):
        queryset = super(EscoltasViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        busca_sem_especial = trata_telefone(busca)

        queryset_escolta = Escoltas.objects.none()
        for query in Escoltas.objects.filter(Q(excluido=False)):
            qs = Escoltas.objects.none()
            escolta_list = list()

            numero_sei = trata_telefone(query.numero_sei)

            escolta_list.append(trata_campo(query.numero_escolta))
            escolta_list.append(formata_data_hora(query.created_at))
            escolta_list.append(formata_data(trata_campo(query.data_inicio_aerea)) if query.data_inicio_aerea else "")
            escolta_list.append(formata_data(trata_campo(query.data_fim_aerea)) if query.data_fim_aerea else "")
            escolta_list.append(formata_data(trata_campo(query.data_inicio_terrestre)) if query.data_inicio_terrestre else "")
            escolta_list.append(formata_data(trata_campo(query.data_fim_terrestre)) if query.data_fim_terrestre else "")
            escolta_list.append(formata_hora(query.hora_inicio_aerea) if query.hora_inicio_aerea else "")
            escolta_list.append(formata_hora(query.hora_fim_aerea) if query.hora_fim_aerea else "")
            escolta_list.append(formata_hora(query.hora_inicio_terrestre) if query.hora_inicio_terrestre else "")
            escolta_list.append(formata_hora(query.hora_fim_terrestre) if query.hora_fim_terrestre else "")


            escolta_list.append(trata_campo(query.ordem_missao))
            escolta_list.append(trata_campo(query.numero_documento_sei))
            escolta_list.append(trata_campo(query.descricao_terrestre))
            escolta_list.append(trata_campo(query.descricao_aerea))
            escolta_list.append(trata_campo(query.nome_missao))
            escolta_list.append(trata_campo(query.get_tipo_aeronave_display()))
            escolta_list.append(trata_campo(query.get_tipo_escolta_display()))
            escolta_list.append(trata_campo(query.get_instituicao_display()))
            escolta_list.append(trata_campo(query.get_fase_escolta_aerea_display()))
            escolta_list.append(trata_campo(query.get_fase_escolta_terrestre_display()))
            escolta_list.append(trata_campo(query.get_responsavel_display()))
            
            for servidor in query.servidores_escolta_terrestre.all():
                escolta_list.append(trata_campo(servidor.nome))
                escolta_list.append(trata_campo(servidor.matricula))
                escolta_list.append(trata_campo(servidor.cpf))
                escolta_list.append(trata_campo(servidor.cargos.cargo if servidor.cargos else ""))

            for servidor in query.servidores_escolta_aerea.all():
                escolta_list.append(trata_campo(servidor.nome))
                escolta_list.append(trata_campo(servidor.matricula))
                escolta_list.append(trata_campo(servidor.cpf))
                escolta_list.append(trata_campo(servidor.cargos.cargo if servidor.cargos else ""))
            
            for pedido in query.pedidos_inclusao.all():
                escolta_list.append(trata_campo(pedido.get_tipo_inclusao_display()))
                escolta_list.append(trata_campo(pedido.nome))
                escolta_list.append(trata_campo(pedido.cpf))
                escolta_list.append(trata_campo(pedido.unidade.nome if pedido.unidade else ""))
                escolta_list.append(trata_campo(pedido.estado_solicitante.nome if pedido.estado_solicitante else ""))

             
            for escolta in escolta_list:
                if busca in escolta:
                    qs = Escoltas.objects.filter(pk=query.pk)
                    break

            if not qs and (busca_sem_especial in numero_sei):
                qs = Escoltas.objects.filter(pk=query.pk)

            if not queryset_escolta:
                queryset_escolta = qs
                queryset = queryset_escolta
            elif qs:
                queryset = queryset | qs

        if not self.request.query_params.get("ordering"):
            queryset = queryset.order_by('-created_at')
        else:
            queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_pedido_aguardando_escolta(self, pedido):
        return PedidoInclusao.objects.filter(id=pedido.pk, aguardando_escolta=True).exists()
    
    def get_numero_escolta(self):
        escolta = None
        now = datetime.now()
        ano = rf"/{now.year}"
        try:
            escolta = Escoltas.objects.filter(responsavel='DEPEN', numero_escolta__contains=ano).latest('created_at')
        except Exception:
            return f'{"1".zfill(3)}/{str(now.year)}'
            
        numero = escolta.numero_escolta.split('/')
        if str(now.year) == numero[1]:
            inicio = int(numero[0]) + 1
            numero_escolta = f'{str(inicio).zfill(3)}/{numero[1]}'
        else:
            numero_escolta = f'{"1".zfill(3)}/{str(now.year)}'
        
        return numero_escolta
    
    def check_data_inicio_escolta(self, requisicao, pedido):
        """Verifica se data de inicio da escolta < data de deferimento"""
        data_inicio_terrestre = None
        data_inicio_aereo = None
        erro = dict()
        fuso_horario = timezone(timedelta(hours=-3))
        data_hora = pedido.data_movimentacao.astimezone(fuso_horario)
        if requisicao.get('data_inicio_aerea'):
            data_inicio_aereo = converte_string_data_hora(requisicao.get('data_inicio_aerea'), 
                                                            requisicao.get('hora_inicio_aerea'))
            if (data_inicio_aereo and
                 (data_inicio_aereo < data_hora.replace(tzinfo=None))):
                erro['data_inicio_aerea'] = mensagens.MSG39
                erro['hora_inicio_aerea'] = mensagens.MSG39
        if requisicao.get('data_inicio_terrestre'):
            data_inicio_terrestre = converte_string_data_hora(requisicao.get('data_inicio_terrestre'), 
                                                                requisicao.get('hora_inicio_terrestre'))
            if (data_inicio_terrestre and
                 (data_inicio_terrestre < data_hora.replace(tzinfo=None))):
                erro['data_inicio_terrestre'] = mensagens.MSG39
                erro['hora_inicio_terrestre'] = mensagens.MSG39
        return erro

    @action(
        detail=False,
        methods=["get"],
        url_path="pedidos-inclusao",
        url_name="pedidos-inclusao",
    )
    def get_pedidos_inclusao(self, request):
        lista_pedidos = list()
        pedido_list = self.request.query_params.get("pedido").split(',') if self.request.query_params.get("pedido") else []

        queryset = PedidoInclusao.objects.filter(pk__in=pedido_list, excluido=False)
        if queryset:
            lista_pedidos.extend(self.get_pedidos(queryset))


        if lista_pedidos:
            lista = ordena_lista(lista_pedidos, ordenacao='nome')
            page_size = paginacao(self.request.query_params.get('page_size'))
            lista_paginada = paginacao_list(lista, page_size)

            page = 1
            if self.request.query_params.get('page'):
                page = len(lista_paginada) if int(self.request.query_params.get('page')) > len(lista_paginada) else int(self.request.query_params.get('page'))

        
        retorno = {"count": len(lista_pedidos),
                    "next": None,
                    "previous": None,
                    "results": lista_paginada[page-1] if lista_pedidos else lista_pedidos
                    }

        return Response(retorno, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="calendario",
        url_name="calendario",
    )
    def get_calendario(self, request):
        lista_escolta = list()
        data_inicio = datetime.strptime(self.request.query_params.get("data_inicio"), '%Y-%m-%d').date()
        data_fim = datetime.strptime(self.request.query_params.get("data_fim"), '%Y-%m-%d').date()
        
        for escolta in Escoltas.objects.filter((Q(data_inicio_aerea__range=[data_inicio, data_fim]) | 
                                                Q(data_inicio_terrestre__range=[data_inicio, data_fim]) | 
                                                Q(data_fim_aerea__range=[data_inicio, data_fim]) | 
                                                Q(data_fim_terrestre__range=[data_inicio, data_fim]) | 
                                                Q(data_inicio_aerea__lte=data_inicio, data_fim_aerea__gte=data_inicio) | 
                                                Q(data_inicio_terrestre__lte=data_inicio, data_fim_terrestre__gte=data_inicio)) &
                                                Q(excluido=False)):
            dia_inicio = None
            dia_fim = None
            data_inicio_aereo = concatena_data_hora(escolta.data_inicio_aerea, escolta.hora_inicio_aerea) if escolta.data_inicio_aerea else None
            data_fim_aereo = concatena_data_hora(escolta.data_fim_aerea, escolta.hora_fim_aerea) if escolta.data_fim_aerea else None
            data_inicio_terrestre = concatena_data_hora(escolta.data_inicio_terrestre, escolta.hora_inicio_terrestre) if escolta.data_inicio_terrestre else None
            data_fim_terrestre = concatena_data_hora(escolta.data_fim_terrestre, escolta.hora_fim_terrestre) if escolta.data_fim_terrestre else None
            if data_inicio_aereo and not data_inicio_terrestre:
                fase = escolta.fase_escolta_aerea
            elif data_inicio_terrestre and not data_inicio_aereo:
                fase = escolta.fase_escolta_terrestre
            else:
                fase = self.get_fase_calendario(escolta)
            dia_inicio = self.get_dia_inicio(data_inicio_aereo, data_inicio_terrestre)
            dia_fim = self.get_dia_fim(data_fim_aereo, data_fim_terrestre)
            unidade_nome = [pedido.unidade.nome for pedido in escolta.pedidos_inclusao.all() if pedido.unidade]
            escolta_dict =   {
                    'id': escolta.id,
                    'name': escolta.nome_missao,
                    'start': dia_inicio[:10] if dia_fim[:10] != dia_inicio[:10] else dia_inicio,
                    'hora_inicio': dia_inicio[11:],
                    'end': dia_fim[:10] if dia_fim[:10] != dia_inicio[:10] else dia_fim,
                    'fase': fase,
                    'unidade_nome': sorted(set(unidade_nome)) if unidade_nome else unidade_nome,
                    'tipo_escolta_nome': escolta.get_tipo_escolta_display() if escolta.tipo_escolta else None
            }
            lista_escolta.append(escolta_dict)

        return Response(lista_escolta, status=status.HTTP_200_OK)

    def get_fase_calendario(self, escolta):
        terrestre = escolta.fase_escolta_terrestre
        aerea = escolta.fase_escolta_aerea
        if terrestre == aerea:
            return terrestre
        elif aerea == 'INICIADA_AEREA' and terrestre == 'INICIADA_TERRESTRE':
            return aerea
        elif aerea == 'FINALIZADA' or aerea == 'AGENDADA':
            return terrestre
        elif terrestre == 'FINALIZADA' or terrestre == 'AGENDADA':
            return aerea

    def get_dia_fim(self, aereo=None, terrestre=None):
        if not aereo:
            return terrestre
        if not terrestre:
            return aereo
        aereo_time = cast_string_in_datetime(aereo)
        terrestre_time = cast_string_in_datetime(terrestre)
        return aereo if aereo_time > terrestre_time else terrestre

    def get_dia_inicio(self, aereo=None, terrestre=None):
        if not aereo:
            return terrestre
        if not terrestre:
            return aereo
        aereo_time = cast_string_in_datetime(aereo)
        terrestre_time = cast_string_in_datetime(terrestre)
        return aereo if aereo_time < terrestre_time else terrestre
        
    
    def get_pedidos(self, queryset):
        
        lista_pedidos = list()
        for query in queryset:
            dict_pedido = {
                "tipo_inclusao": query.tipo_inclusao,
                "id": query.pk,
                "nome": query.nome,
                "cpf": query.cpf,
                "unidade_nome": query.unidade.nome if query.unidade else "",
                "estado_solicitante_nome": query.estado_solicitante.nome if query.estado_solicitante else "",
                "foto": get_thumbnail(query.foto_id)
            }
            lista_pedidos.append(dict_pedido)
        
        return lista_pedidos

    def perform_create(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["usuario_cadastro"] = user.get_user(self)
        kwargs["created_at"] = datetime.now()
        kwargs["pedidos_inclusao"] = [UUID(p_inclusao['id']) for p_inclusao in requisicao.get('pedidos_inclusao')]
        if requisicao.get('servidores_escolta_aerea'):
                kwargs['servidores_escolta_aerea'] = [s['id'] for s in requisicao.get('servidores_escolta_aerea')]
        if requisicao.get('servidores_escolta_terrestre'):
                kwargs['servidores_escolta_terrestre'] = [s['id'] for s in requisicao.get('servidores_escolta_terrestre')]
        serializer.save(**kwargs)
        self.create_many_fields(serializer=serializer)

    def perform_update(self, serializer, **kwargs):
        kwargs["usuario_edicao"] = user.get_user(self)
        kwargs["updated_at"] = datetime.now()
        serializer.save(**kwargs)
        pk = serializer.data.get("id")
        self.update_many_fields(pk=pk)


    def create_many_fields(self, serializer):
        requisicao = self.request.data
        voos = [voo.get("numero_voo") for voo in requisicao.get("voos")]
       
        for voo in voos:
            if len(voo) > 20:
                raise ValidationError({"non_field_errors": mensagens.MSG_TAM_VOOS},status.HTTP_400_BAD_REQUEST)
            VoosEscolta.objects.get_or_create(
                voo=voo,
                escolta_id=serializer.data["id"],
                usuario_cadastro=user.get_user(self)
            )
     
    def update_many_fields(self, pk):
        requisicao = self.request.data
        voos = None
        if requisicao.get("voos"):
            voos = [voo.get("numero_voo") for voo in requisicao.get("voos")]
        voos_base = VoosEscolta.objects.filter(Q(escolta_id=pk)).values_list('voo', flat=True)
        if voos:
            for voos_escolta in VoosEscolta.objects.filter(~Q(voo__in=voos) & Q(escolta_id=pk)):
                VoosEscolta.objects.filter(Q(pk=voos_escolta.pk)).delete()
            if not voos_base:
                for voo in voos:
                    if len(voo) > 20:
                        raise ValidationError({"non_field_errors": mensagens.MSG_TAM_VOOS},status.HTTP_400_BAD_REQUEST)
                    VoosEscolta.objects.create(voo=voo, escolta_id=pk, usuario_cadastro=user.get_user(self))                            
            else:
                for voo in voos:
                    if len(voo) > 20:
                        raise ValidationError({"non_field_errors": mensagens.MSG_TAM_VOOS},status.HTTP_400_BAD_REQUEST)
                    if voo not in voos_base:
                        VoosEscolta.objects.get_or_create(
                            voo=voo,
                            escolta_id=pk,
                            usuario_cadastro=user.get_user(self)
                        )
        elif not voos and VoosEscolta.objects.filter(Q(escolta_id=pk)):
            VoosEscolta.objects.filter(Q(interno_id=pk)).delete()