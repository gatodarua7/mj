from cadastros.models import OrgaoExpedidor

from django.db import transaction
from rest_framework.decorators import action
from comum.models import Telefone
from cadastros.models import Documentos
import datetime
from localizacao.models import Cidade, Pais
from util.busca import check_duplicidade, formata_data, trata_campo, trata_campo_ativo, trata_email, trata_telefone, formata_data_hora, get_ids
from visitante.models import (Visitante, 
                                EmailVisitante, 
                                RgVisitante, 
                                Anuencia, 
                                VisitanteMovimentacao, 
                                PLAIN_FASES, 
                                FASES_INFOR_SOLICITANTE,
                                Manifestacao,
                                DocumentosVisitante,
                                VisitanteRecurso,
                                ManifestacaoDiretoria)
from django.db.models import Q
from visitante.serializers import (VisitanteSerializer, 
                                    EmailVisitanteSerializer, 
                                    RgVisitanteSerializer, 
                                    AnuenciaSerializer, 
                                    VisitanteMovimentacaoSerializer, 
                                    ManifestacaoSerializer, 
                                    DocumentosVisitantePostSerializer, 
                                    DocumentosVisitanteSerializer,
                                    VisitanteRecursoSerializer,
                                    ManifestacaoDiretoriaSerializer)
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
from rest_framework.exceptions import ValidationError
from rest_framework import status, viewsets
from util.paginacao import Paginacao
from mj_crypt.mj_crypt import AESCipher
from django.http import HttpResponse
from imagehelpers.image import image_size
from util.datas import get_proximo_dia_util, sum_years_date, cast_datetime_date
from util import mensagens
from util.user import get_user 
from util.busca import (
    trata_campo,
    trata_campo_ativo,
    trata_telefone,
    check_duplicidade,
    formata_data,
    formata_data_hora
)
from datetime import datetime
from uuid import UUID
import ast
from core.views import Base


class VisitanteViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = VisitanteSerializer
    pagination_class = Paginacao
    queryset = Visitante.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "cpf", "data_nascimento","atendimento","created_at", "ativo")
    filter_fields = ("nome","cpf", "data_nascimento","atendimento","created_at","ativo")
    ordering_fields = ("nome", "cpf", "data_nascimento","atendimento", "created_at", "fase",
                         "situacao", "data_validade", "data_movimentacao")
    ordering = ("nome","cpf", "data_nascimento", "atendimento", "ativo")

    def create(self, request, *args, **kwargs):
        
        try:      
            requisicao = request.data
            if requisicao.get("cpf") and self.check_visitante_exists(requisicao): 
                return Response(
                    {"cpf": mensagens.MSG4},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.request.data['fase'] = 'INICIADO'
            return super(VisitanteViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

    def update(self, request, *args, **kwargs):
        requisicao = request.data

        try:
            if  requisicao.get("cpf") and self.check_visitante_exists(requisicao):
                return Response(
                    {"cpf": mensagens.MSG4},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if Base().check_registro_excluido(Visitante, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Visitante, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(VisitanteViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
    

        try:
            if not Base().check_registro_exists(Visitante, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Visitante, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not self.check_fase_iniciado(pk):
                return Response(
                    {"non_field_errors": "Apenas solicitações na fase INICIADO pode ser excluída."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Visitante.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def filter_queryset(self, queryset):
        queryset = super(VisitanteViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        queryset_visitante = Visitante.objects.none()
        for query in Visitante.objects.filter(Q(excluido=False)):
            qs = Visitante.objects.none()
            visitante_list = list()
            visitante_list2 = list()

            visitante_list2.append(trata_telefone(query.numero_sei) if query.numero_sei else "")
            visitante_list.append(trata_campo(query.nome))
            visitante_list2.append(trata_campo(query.cpf))
            visitante_list.append(formata_data_hora(query.data_movimentacao))
            visitante_list.append(formata_data(trata_campo(query.data_nascimento)))
            visitante_list.append(formata_data(trata_campo(query.data_validade)) if query.data_validade else "")
            visitante_list.append(formata_data(trata_campo(query.recurso) if query.recurso else ""))
            visitante_list.append(trata_campo(query.recurso.observacao) if query.recurso else "")
            visitante_list.append(trata_campo(query.idade))
            visitante_list.append(trata_campo(query.nome_pai))
            visitante_list.append(trata_campo(query.nome_mae))
            visitante_list.append(trata_campo(query.get_fase_display()))
            visitante_list.append(formata_data_hora(query.created_at))
            visitante_list.append(trata_campo(
                query.genero.descricao) if query.genero else "")
            visitante_list.append(
                trata_campo(
                    query.estado_civil.nome) if query.estado_civil else ""
            )
            visitante_list.append(trata_campo(query.estado.nome) if query.estado else "")
            visitante_list.append(
                trata_campo(
                    query.naturalidade.nome) if query.naturalidade else ""
            )
            visitante_list.append(
                trata_campo(
                    query.grau_instrucao.nome) if query.grau_instrucao else ""
            )
            visitante_list.append(trata_campo(
                query.profissao.nome) if query.profissao else "")

            visitante_list.append(trata_campo(query.genero.descricao) if query.genero else "")
            visitante_list.append(trata_campo(query.estado.nome) if query.estado else "")
            visitante_list.append(
                trata_campo(query.naturalidade.nome) if query.naturalidade else "")
            visitante_list.extend([
                trata_campo(necessidade.nome)
                for necessidade in query.necessidade_especial.all()
            ])

            visitante_list.extend([
                    trata_campo(pais.nome) for pais in query.nacionalidade.all()
                ])

            for rg in RgVisitante.objects.filter(visitante_id=query.id, excluido=False):
                visitante_list2.append(trata_telefone(rg.numero) if rg.numero else "")
                visitante_list.append(trata_campo(rg.orgao_expedidor.nome))
                visitante_list.append(trata_campo(rg.orgao_expedidor.sigla))
                visitante_list.append(trata_campo(rg.orgao_expedidor.estado))

            for endereco in query.enderecos.all():
                visitante_list2.append(trata_telefone(endereco.cep) if endereco.cep else "")
                visitante_list.append(trata_campo(endereco.logradouro))
                visitante_list.append(trata_campo(endereco.bairro))
                visitante_list.append(trata_campo(endereco.numero))
                visitante_list.append(trata_campo(endereco.cidade.nome))
                visitante_list.append(trata_campo(endereco.estado.nome))
                visitante_list.append(trata_campo(endereco.estado.sigla))
                visitante_list.append(trata_campo(endereco.observacao))
                visitante_list.append(trata_campo(endereco.complemento))
                visitante_list.append(trata_campo(endereco.cep.replace("-", "").replace(".", "")))
                visitante_list.append(trata_campo(endereco.andar))
                visitante_list.append(trata_campo(endereco.sala))

            for telefone in query.telefones.all():
                visitante_list.append(trata_campo(telefone.tipo))
                visitante_list2.append(trata_telefone(telefone.numero))
                visitante_list.append(trata_campo(telefone.observacao))

            for email in EmailVisitante.objects.filter(visitante_id=query.id, excluido=False):
                visitante_list.append(trata_campo(email.email))

            for anuencia in Anuencia.objects.filter(visitante_id=query.id, excluido=False):
                visitante_list.append(trata_campo(anuencia.observacao))
                visitante_list.append(trata_campo(anuencia.tipo_vinculo.nome))
                visitante_list.append(formata_data_hora(anuencia.created_at))
                if anuencia.updated_at:
                    visitante_list.append(formata_data_hora(anuencia.updated_at))
                visitante_list.append(trata_campo(anuencia.interno.nome))
                visitante_list.append(trata_campo(anuencia.interno.cpf))
            
            for manifestacao in Manifestacao.objects.filter(visitante_id=query.id, excluido=False):
                visitante_list.append(trata_campo(manifestacao.parecer))
                visitante_list.append(formata_data_hora(manifestacao.created_at))
                visitante_list.append(trata_campo(manifestacao.usuario_cadastro.username))

            for documento in query.documentos.all():
                visitante_list.append(trata_campo(documento.tipo.nome))
                visitante_list.append(trata_campo(documento.num_cod))
                visitante_list.append(trata_campo(documento.observacao))
                visitante_list.append(formata_data_hora(documento.created_at))
                if documento.updated_at:
                    visitante_list.append(formata_data_hora(documento.updated_at))
                visitante_list.append(formata_data(trata_campo(documento.data_validade)))

            for item in visitante_list:
                if busca in item:
                    qs = Visitante.objects.filter(pk=query.pk)
                    break

            if not qs:
                for item in visitante_list2:
                    if trata_telefone(busca) in item:
                        qs = Visitante.objects.filter(pk=query.pk)
                        break
            
            if queryset_visitante:
                queryset_visitante = qs
                queryset = queryset_visitante
            elif qs:
                queryset = queryset | qs

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)
        
        if parametros_busca.get("fase"):
            fases = parametros_busca.get("fase").split(',')
            queryset = queryset.filter(fase__in=fases)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset
    
    def check_fase_iniciado(self, id):
        """Verifica se situacao iniciada"""
        return Visitante.objects.filter(Q(id=id, fase='INICIADO')).exists()

    def check_visitante_exists(self, requisicao):
        cpf = check_duplicidade(requisicao.get("cpf"))
        return Visitante.objects.filter(
            Q(cpf__iexact=cpf, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def check_brasil_exists(self, requisicao):
        brasil_exist = None
        if requisicao.get("nacionalidade"):
            for pais in requisicao.get("nacionalidade"):
                pais = Pais.objects.get(id=pais)
                if pais.nome == "Brasil":
                    brasil_exist = True
        return brasil_exist

    def check_cidade(self, requisicao):
        return Cidade.objects.filter(
            Q(id=requisicao["naturalidade"], estado_id=requisicao["estado"])
        ).exists()

    def check_cadastro(self, requisicao):
        completo = False
        return completo

    def check_tipo_atendimento(self, requisicao):
        idade = int(requisicao.get("idade"))
        tipo_atendimento = None

        if (idade >= 60) or (idade < 18) or requisicao.get("necessidade_especial"):
            tipo_atendimento = 'PREFERENCIAL'
        else:
           tipo_atendimento = 'NORMAL' 
        return tipo_atendimento

    def perform_create(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["telefones"] = self.get_telefones(requisicao)
        kwargs["enderecos"] = get_ids(requisicao.get("enderecos"))
        kwargs["atendimento"] = self.check_tipo_atendimento(requisicao)
        kwargs["documentos"] = get_ids(requisicao.get("documentos"))
        kwargs["usuario_cadastro"] = get_user(self)
        obj = serializer.save(**kwargs)

        visitante = Visitante.objects.get(id=obj.id)

        if requisicao.get("emails"):
            for email in requisicao["emails"]:
                EmailVisitante.objects.create(visitante_id=obj.id, email=email, usuario_cadastro=get_user(self))

        if requisicao.get("rg"):
            for rg in requisicao["rg"]:
                orgao_exp = OrgaoExpedidor.objects.get(id=rg.get("orgao_expedidor"))
                rg_obj, created = RgVisitante.objects.get_or_create(numero=rg.get("numero"), orgao_expedidor_id=orgao_exp.id)
                rg_obj.visitante = visitante
                rg_obj.usuario_cadastro = get_user(self)
                rg_obj.save()
        self.create_many_fields(serializer=serializer)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["updated_at"] = datetime.now()
        if requisicao.get('telefones'):
            kwargs["telefones"] = self.get_telefones(requisicao)
        if requisicao.get('enderecos'):
            kwargs["enderecos"] = get_ids(requisicao.get("enderecos"))
        if requisicao.get('necessidade_especial') and requisicao.get('idade'):
            kwargs["atendimento"] = self.check_tipo_atendimento(requisicao)
        if requisicao.get('documentos'):
            kwargs["documentos"] = get_ids(requisicao.get("documentos"))
        kwargs["usuario_edicao"] = get_user(self)
        serializer.save(**kwargs)
        self.update_many_fields(pk=serializer.data.get("id"))

    def create_many_fields(self, serializer):
        requisicao = self.request.data

        if self.request.data.get("rgs"):
            for rg in self.request.data.get("rgs"):
                RgVisitante.objects.filter(id=rg.get("id")).update(
                    visitante_id=serializer.data["id"]
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
                if trata_email(email):
                    email = email.strip()
                    EmailVisitante.objects.update_or_create(
                        email=email,
                        usuario_cadastro=get_user(self),
                        visitante_id=serializer.data["id"],
                        ativo=True,
                    )
                else:
                    raise ValidationError({"emails": mensagens.EMAIL_INVALIDO},status.HTTP_400_BAD_REQUEST)

        VisitanteMovimentacao.objects.create(visitante_id=serializer.data["id"],
                                                usuario_cadastro=get_user(self),
                                                fase='INICIADO',
                                                created_at=serializer.data["data_movimentacao"])
        
        for anuencia in self.request.data.get("anuencias"):                               
            Anuencia.objects.filter(id=anuencia.get("id")).update(visitante_id=serializer.data["id"])


    def update_many_fields(self, pk):
        requisicao = self.request.data

        if self.request.data.get("rgs"):
            for rg in self.request.data.get("rgs"):
                RgVisitante.objects.filter(id=rg.get("id")).update(
                    visitante_id=pk
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
            for email in EmailVisitante.objects.filter(~Q(email__in=emails) & Q(visitante_id=pk)):
                EmailVisitante.objects.filter(Q(pk=email.pk)).delete()
            for email in emails:
                if(trata_email(email)):
                    if email.strip():
                        email = email.strip()
                        EmailVisitante.objects.update_or_create(
                            email=email,
                            usuario_cadastro=get_user(self),
                            visitante_id=UUID(pk),
                            ativo=True,
                        )
                else:
                    raise ValidationError({"emails": mensagens.EMAIL_INVALIDO},status.HTTP_400_BAD_REQUEST)
        else:
            for email in EmailVisitante.objects.filter(Q(visitante_id=pk)):
                EmailVisitante.objects.filter(Q(pk=email.pk)).delete()            

    def get_telefones(self, request):
        list_telefones = list()
        for telefone in request.get("telefones"):
            privado = True
            Telefone.objects.filter(
                Q(id=telefone["id"]) & (
                    Q(tipo="CELULAR") | Q(tipo="RESIDENCIAL"))
            ).update(privado=privado)
            list_telefones.append(telefone["id"])
        return list_telefones


class RgVisitanteViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = RgVisitanteSerializer
    pagination_class = Paginacao
    queryset = RgVisitante.objects.filter(excluido=False)
    filter_backends = (SearchFilter,)
    search_fields = "numero"

    def create(self, request, *args, **kwargs):
        try:
            return super(RgVisitanteViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super(RgVisitanteViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            RgVisitante.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save(
            usuario_cadastro=get_user(self),
        )

    def perform_update(self, serializer):
        serializer.save(
            usuario_edicao=get_user(self),
        )


class EmailVisitanteViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = EmailVisitanteSerializer
    pagination_class = Paginacao
    queryset = EmailVisitante.objects.filter(excluido=False)
    filter_backends = (SearchFilter,)
    search_fields = "email"

    def create(self, request, *args, **kwargs):
        try:
            return super(EmailVisitanteViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super(EmailVisitanteViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            EmailVisitante.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save(
            usuario_cadastro=get_user(self),
        )

    def perform_update(self, serializer):
        serializer.save(
            usuario_edicao=get_user(self),
        )


class AnuenciaViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = AnuenciaSerializer
    pagination_class = Paginacao
    queryset = Anuencia.objects.filter(excluido=False)
    search_fields = ("data_declaracao","created_at", "ativo", "visitante")
    filter_fields = ("data_declaracao","created_at", "ativo")
    ordering_fields = ("data_declaracao","created_at", "ativo")
    ordering = ("data_declaracao","created_at", "ativo")


    def create(self, request, *args, **kwargs):
        try:
            return super(AnuenciaViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super(AnuenciaViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            Anuencia.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def filter_queryset(self, queryset):
        queryset = super(AnuenciaViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))
        if busca:
            queryset = Anuencia.objects.none()
            
            for query in Anuencia.objects.filter(Q(excluido=False)):
                anuencia_list = list()

                anuencia_list.append(trata_campo(query.observacao))
                anuencia_list.append(trata_campo(query.tipo_vinculo.nome))
                anuencia_list.append(formata_data_hora(query.created_at))
                if query.updated_at:
                    anuencia_list.append(formata_data_hora(query.updated_at))
                anuencia_list.append(trata_campo(query.interno.nome))
                anuencia_list.append(trata_campo(query.interno.cpf))
            
                for item in anuencia_list:
                    if busca in item:
                        queryset |= Anuencia.objects.filter(pk=query.pk)
                        break

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)
        
        if parametros_busca.get("id_visitante"):
            queryset = queryset.filter(visitante_id=parametros_busca.get("id_visitante"))

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            usuario_cadastro=get_user(self),
        )

    def perform_update(self, serializer):
        serializer.save(
            usuario_edicao=get_user(self),
        )


class VisitanteMovimentacaoViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = VisitanteMovimentacaoSerializer
    pagination_class = Paginacao
    queryset = VisitanteMovimentacao.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("motivo", "visitante")
    filter_fields = ("motivo", "visitante")
    ordering_fields = ("created_at","visitante")
    ordering = ("created_at","visitante")

    def create(self, request, *args, **kwargs):
        if not request.data.get('fase'):
            return Response(
                {"non_field_errors": mensagens.MOVTO_PEDIDO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            data_movto = datetime.now()
            self.request.data['created_at'] = data_movto
            requisicao = self.request.data
            try:
                visitante = Visitante.objects.select_for_update().get(pk=requisicao.get('visitante'))
            except Exception:
                return Response({"non_field_errors": mensagens.MSG_ERRO},
                                status=status.HTTP_400_BAD_REQUEST)

            if (requisicao.get('fase') != 'SOLICITANTE_INFORMADO' and 
                not self.check_movimentacao_is_valid(visitante.fase, requisicao.get('fase'))):
                return Response({"non_field_errors": "Movimentacao Não Permitida"},
                                status=status.HTTP_400_BAD_REQUEST)
            if (requisicao.get('fase') == 'SOLICITANTE_INFORMADO' and 
                not self.check_informacao_is_valid(visitante.fase)):
                return Response({"non_field_errors": "Não é permitido informar solicitante na fase atual."},
                                status=status.HTTP_400_BAD_REQUEST)
            if (visitante.fase == 'ANALISE_INTELIGENCIA' and 
                not self.check_manifestacao_inteligencia(requisicao)):
                return Response({"non_field_errors": "Não é permitido movimentar solitações sem manifestação da inteligência."},
                                status=status.HTTP_400_BAD_REQUEST)
            if requisicao.get('fase') == 'SOLICITANTE_INFORMADO':
                visitante.solicitante_informado = True
            elif requisicao.get('fase') == 'RECURSO':
                if not self.check_recurso_is_valid(requisicao.get('visitante')):
                    return Response({"non_field_errors": "Não é permitido cadastrar um recurso após 5 dias utéis da comunicação do solicitante."},
                                    status=status.HTTP_400_BAD_REQUEST)
                visitante.data_movimentacao = data_movto
                visitante.fase = requisicao.get('fase')
                visitante.recurso_id = requisicao.get('recurso')
            else:
                visitante.data_movimentacao = data_movto
                visitante.fase = requisicao.get('fase')
            if requisicao.get('fase') == 'DEFERIDO' or requisicao.get('fase') == 'RECURSO_DEFERIDO':
                visitante.data_validade = cast_datetime_date(sum_years_date(data_movto, 1))
                visitante.situacao = True
                visitante.solicitante_informado = False
            if requisicao.get('fase') == 'RECURSO_INDEFERIDO':
                visitante.solicitante_informado = False

            visitante.save()

            return super(VisitanteMovimentacaoViewSet, self).create(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(VisitanteMovimentacaoViewSet, self).filter_queryset(queryset)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path=r"get_fases/(?P<fase>[^/.]+)",
        url_name="get_fases",
    )
    def get_fases(self, request, fase):
        
        items = {'fases': PLAIN_FASES[fase]}
        return Response(items, status=status.HTTP_200_OK)

    def check_movimentacao_is_valid(self, situacao_atual, situacao_mvto):
        """Verifica se movimentação de Fase é válida"""
        return True if situacao_mvto in PLAIN_FASES[situacao_atual] else False
    
    def check_informacao_is_valid(self, situacao_atual):
        """Verifica se é permitido a ação de informar visitante"""
        return True if situacao_atual in FASES_INFOR_SOLICITANTE else False
    
    def check_manifestacao_inteligencia(self, requisicao):
        """Verifica se existe manifestação da inteligencia"""
        return Manifestacao.objects.filter(visitante=requisicao.get('visitante')).exists()
    
    def check_recurso_is_valid(self, visitante_id):
        """Verifica se é permitido a ação de informar visitante"""
        
        visitante = Visitante.objects.get(pk=UUID(visitante_id))
        if visitante.fase == 'INDEFERIDO':
            movimentacao = VisitanteMovimentacao.objects.get(visitante=visitante, fase='SOLICITANTE_INFORMADO')
            if not movimentacao:
                return True
            dia = 5 if movimentacao.data_contato.isoweekday() in [6, 7] else 4
            return datetime.today().date() <= get_proximo_dia_util(data=movimentacao.data_contato, dia=dia)
        return False 


class ManifestacaoViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = ManifestacaoSerializer
    pagination_class = Paginacao
    queryset = Manifestacao.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("parecer", "visitante","created_at", "ativo")
    filter_fields = ("parecer","visitante", "created_at","ativo")
    ordering_fields = ("parecer","visitante", "created_at","ativo")

    def create(self, request, *args, **kwargs):
        
        try:      
            return super(ManifestacaoViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
    def update(self, request, *args, **kwargs):
        requisicao = request.data
        try:
            user = get_user(self)
            manifestacao = Manifestacao.objects.get(id=requisicao.get("id"), ativo=True)
            pode_editar = False

            if user != manifestacao.usuario_cadastro:
                return Response(
                    {"non_field_errors": mensagens.ERRO_USUARIO_EDITAR},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            for visitante in VisitanteMovimentacao.objects.filter(visitante_id=requisicao.get("visitante")):
                if visitante.fase == "ANALISE_INTELIGENCIA":
                    pode_editar = True

            if not pode_editar:
                return Response(
                {"non_field_errors": mensagens.ERRO_MOVIMENTAR},
                status=status.HTTP_400_BAD_REQUEST,
            )

            return super(ManifestacaoViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(ManifestacaoViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            user = get_user(self)
            manifestacao = Manifestacao.objects.get(id=pk, ativo=True)
            pode_excluir = False

            if user != manifestacao.usuario_cadastro:
                return Response(
                    {"non_field_errors": mensagens.ERRO_USUARIO_EXCLUIR},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            for visitante in VisitanteMovimentacao.objects.filter(visitante_id=manifestacao.visitante):
                if visitante.fase == "ANALISE_INTELIGENCIA":
                    pode_excluir = True

            if not pode_excluir:
                return Response(
                {"non_field_errors": mensagens.ERRO_EXCLUIR},
                status=status.HTTP_400_BAD_REQUEST,
            )

            Manifestacao.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def filter_queryset(self, queryset):
        queryset = super(ManifestacaoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))
        if busca:
            queryset = Manifestacao().objects.none()
            
            for query in Manifestacao.objects.filter(Q(excluido=False)):
                manifestacao_list = list()
                manifestacao_list.append(formata_data_hora(query.created_at))
            
                for item in manifestacao_list:
                    if busca in item:
                        queryset |= Manifestacao.objects.filter(pk=query.pk)
                        break

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)
            
        if not self.request.query_params.get("ordering"):
           queryset = queryset.order_by('-created_at')
        else:
            queryset = OrderingFilter().filter_queryset(self.request, queryset, self)
        

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_vinculos(self, id):
        manifestacao = Manifestacao.objects.filter(Q(id=id, excluido=False)).exists()
        return Visitante.objects.filter(Q(id=manifestacao.visitante, excluido=False)).exists()

    def perform_create(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["documentos"] = get_ids(requisicao.get("documentos_list"))
        kwargs["usuario_cadastro"] = get_user(self)
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["updated_at"] = datetime.now()
        kwargs["documentos"] = get_ids(requisicao.get("documentos_list"))
        kwargs["usuario_edicao"] = get_user(self)
        serializer.save(**kwargs)


class DocumentosVisitanteViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    pagination_class = Paginacao
    queryset = DocumentosVisitante.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("id", "ativo")
    filter_fields = ("id", "ativo")
    ordering_fields = ()
    ordering = ("created_at", "updated_at")
    DEFAULT_PDF_FILE_SIZE = 15 * 1024 * 1024
    DEFAULT_IMG_FILE_SIZE = 1 * 1024 * 1024
    DEFAULT_IMAGE_SIZE = (720, 480)
    FORMATOS_VALIDOS = ["png", "jpeg", "jpg", "pdf"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DocumentosVisitanteSerializer
        return DocumentosVisitantePostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if (
            request.data.get("arquivo_temp").name.split(".")[-1].lower()
            not in self.FORMATOS_VALIDOS
        ):
            return Response(
                {
                    "arquivo_temp": mensagens.TIPO_PERMITIDO
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.data.get("arquivo_temp").content_type == "application/pdf":
            if request.data.get("arquivo_temp").size > self.DEFAULT_PDF_FILE_SIZE:
                return Response(
                    {
                        "arquivo_temp": mensagens.TAM_PDF
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            if (
                image_size(request.data.get("arquivo_temp"))
                < self.DEFAULT_IMAGE_SIZE
            ):
                if (
                    request.data.get("arquivo_temp").size
                    < self.DEFAULT_IMG_FILE_SIZE
                ):
                    self.perform_create(serializer)
                    headers = self.get_success_headers(serializer.data)
                    response_data = {}
                    response_data.update(serializer.data)
                    response_data.update({"detail": mensagens.IMG_BAIXA_RESOLUCAO})

                    return Response(
                        response_data,
                        status=status.HTTP_201_CREATED,
                        headers=headers,
                    )
                else:
                    return Response(
                        {
                            "arquivo_temp": mensagens.TAM_IMAGEM
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
  
        response_data = {}
        response_data.update(serializer.data)
        if not response_data.get('filename'):
            DOC="documentos/"
            DOC_VIST="documentos_visitante/"
            if DOC in response_data['arquivo_temp']:
                    response_data['filename'] = response_data['arquivo_temp'].split(DOC)[-1]
            elif DOC_VIST in response_data['arquivo_temp']:
                response_data['filename'] = response_data['arquivo_temp'].split(DOC_VIST)[-1]
        return Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers
        )
            

    def update(self, request, pk, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if request.data.get("arquivo_temp"):
            if (
                request.data.get("arquivo_temp").name.split(".")[-1].lower()
                not in self.FORMATOS_VALIDOS
            ):
                return Response(
                    {
                        "arquivo_temp": mensagens.TIPO_PERMITIDO
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request.data.get("arquivo_temp").content_type == "application/pdf":
                if request.data.get("arquivo_temp").size > self.DEFAULT_PDF_FILE_SIZE:
                    return Response(
                        {
                            "arquivo_temp": mensagens.TAM_PDF
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                if (
                    image_size(request.data.get("arquivo_temp"))
                    < self.DEFAULT_IMAGE_SIZE
                ):
                    return Response(
                            {
                                "arquivo_temp": mensagens.TAM_IMAGEM
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                elif (
                        request.data.get("arquivo_temp").size
                        < self.DEFAULT_IMG_FILE_SIZE
                    ):
                        self.perform_update(serializer)
                        headers = self.get_success_headers(serializer.data)
                        response_data = {}
                        response_data.update(serializer.data)
                        response_data.update({"detail": mensagens.IMG_BAIXA_RESOLUCAO})
                        return Response(
                            response_data,
                            status=status.HTTP_201_CREATED,
                            headers=headers,
                        )

        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = {}
        response_data.update(serializer.data)
        return Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, pk, *args, **kwargs):
        try:

            if not Base().check_registro_exists(DocumentosVisitante, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            DocumentosVisitante.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(DocumentosVisitanteViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))
        for query in DocumentosVisitante.objects.filter(Q(excluido=False)):
            documento_list = list()
            documento_list.append(formata_data_hora(query.created_at))
            if query.updated_at:
                documento_list.append(formata_data_hora(query.updated_at))

            for item in documento_list:
                if busca in item:
                    queryset |= DocumentosVisitante.objects.filter(pk=query.pk)
                    break

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=get_user(self), updated_at=datetime.now())

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"content/(?P<documento_id>[^/.]+)",
        url_name="content",
    )
    def get_content(self, request, documento_id):
        import base64
        import io as BytesIO

        crypt = AESCipher()

        try:
            obj = DocumentosVisitante.objects.get(id=documento_id, excluido=False)
            buffer = BytesIO.BytesIO()

            nome_arquivo = obj.arquivo_temp.name.split("/")[-1]
            obj = crypt.decrypt(obj.arquivo)
            obj = obj.split(";base64,")[1]

            buffer.write(base64.decodebytes(bytes(obj, "utf-8")))

            response = HttpResponse(
                buffer.getvalue(),
            )
            response["Content-Disposition"] = "attachment;filename={0}".format(
                nome_arquivo
            )
            return response

        except Exception:
            return Response(
                {"detail": mensagens.MSG3}, status=status.HTTP_404_NOT_FOUND
            )


class VisitanteRecursoViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = VisitanteRecursoSerializer
    pagination_class = Paginacao
    queryset = VisitanteRecurso.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("observacao", "ativo")
    filter_fields = ("observacao", "ativo")

    def create(self, request, *args, **kwargs):
        
        try:
            if not request.data.get('documentos_list'):
                return Response(
                    {"non_field_errors": "Para cadastrar um recurso é obrigatório o anexo de pelo menos um documento."},
                    status=status.HTTP_400_BAD_REQUEST,
                )      
            return super(VisitanteRecursoViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
    def update(self, request, *args, **kwargs):
        try:
            if not request.data.get('documentos_list'):
                return Response(
                    {"non_field_errors": "Para cadastrar um recurso é obrigatório o anexo de pelo menos um documento."},
                    status=status.HTTP_400_BAD_REQUEST,
                )   
            return super(VisitanteRecursoViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def perform_create(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["documentos"] = get_ids(requisicao.get("documentos_list"))
        kwargs["usuario_cadastro"] = get_user(self)
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["updated_at"] = datetime.now()
        kwargs["documentos"] = get_ids(requisicao.get("documentos_list"))
        kwargs["usuario_edicao"] = get_user(self)
        serializer.save(**kwargs)


class ManifestacaoDiretoriaViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = ManifestacaoDiretoriaSerializer
    pagination_class = Paginacao
    queryset = ManifestacaoDiretoria.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("parecer", "visitante","created_at", "ativo")
    filter_fields = ("parecer","visitante", "created_at","ativo")
    ordering_fields = ("parecer","visitante", "created_at","ativo")

    def create(self, request, *args, **kwargs):
        try:      
            return super(ManifestacaoDiretoriaViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def update(self, request, *args, **kwargs):
        requisicao = request.data
        try:
            user = get_user(self)
            manifestacao = ManifestacaoDiretoria.objects.get(id=requisicao.get("id"), ativo=True)
            pode_editar = False

            if user != manifestacao.usuario_cadastro:
                return Response(
                    {"non_field_errors": mensagens.ERRO_USUARIO_EDITAR},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            for visitante in VisitanteMovimentacao.objects.filter(visitante_id=requisicao.get("visitante")):
                if visitante.fase == "ANALISE_DIRETORIA":
                    pode_editar = True

            if not pode_editar:
                return Response(
                {"non_field_errors": mensagens.ERRO_MOVIMENTAR},
                status=status.HTTP_400_BAD_REQUEST,
            )

            return super(ManifestacaoDiretoriaViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(ManifestacaoDiretoriaViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            user = get_user(self)
            manifestacao = ManifestacaoDiretoria.objects.get(id=pk, ativo=True)
            pode_excluir = False

            if user != manifestacao.usuario_cadastro:
                return Response(
                    {"non_field_errors": mensagens.ERRO_USUARIO_EXCLUIR},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            for visitante in VisitanteMovimentacao.objects.filter(visitante_id=manifestacao.visitante):
                if visitante.fase == "ANALISE_INTELIGENCIA":
                    pode_excluir = True

            if not pode_excluir:
                return Response(
                {"non_field_errors": mensagens.ERRO_EXCLUIR},
                status=status.HTTP_400_BAD_REQUEST,
            )

            ManifestacaoDiretoria.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def filter_queryset(self, queryset):
        queryset = super(ManifestacaoDiretoriaViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params 

        manifestacao = trata_campo(parametros_busca.get("manifestacao_diretoria"))
        if manifestacao:
            queryset = queryset.filter(~Q(id=manifestacao))
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)
        return queryset

    def perform_create(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["documentos"] = get_ids(requisicao.get("documentos_list"))
        kwargs["usuario_cadastro"] = get_user(self)
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["updated_at"] = datetime.now()
        kwargs["documentos"] = get_ids(requisicao.get("documentos_list"))
        kwargs["usuario_edicao"] = get_user(self)
        serializer.save(**kwargs)