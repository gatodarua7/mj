from django.db.models import Q
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from comum.models import Endereco, Telefone
from cadastros.models import Pessoa, Setor
from comum.serializers import EnderecoSerializer, TelefoneSerializer
from util import mensagens, user
from util.busca import trata_campo, trata_campo_ativo, trata_telefone
from util.paginacao import Paginacao
from datetime import datetime
from core.views import Base


class EnderecoViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = EnderecoSerializer
    pagination_class = Paginacao
    queryset = Endereco.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ('cidade', 'logradouro', 'bairro', 'ativo',
                     'numero', 'complemento', 'cep')
    filter_fields = ('cidade', 'logradouro', 'bairro', 'ativo',
                     'numero', 'complemento', 'cep')
    ordering_fields = ('cep', 'cidade', 'logradouro', 'bairro', 'ativo',
                        'numero', 'complemento')
    ordering = ('cep', 'cidade', 'logradouro', 'bairro', 'ativo',
                'numero', 'complemento')

    def create(self, request, *args, **kwargs):
        try:
            return super(EnderecoViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response({"non_field_errors": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST)

        
    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(Endereco, requisicao["id"]):
                return Response({"non_field_errors": mensagens.NAO_PERMITIDO}, status=status.HTTP_400_BAD_REQUEST)
            if Base().check_registro_inativo(Endereco, requisicao):
                return Response({"non_field_errors": mensagens.INATIVO}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"non_field_errors": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST)

        return super(EnderecoViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(EnderecoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get('search'))
        ativo = trata_campo_ativo(parametros_busca.get('ativo'))

        for query in Endereco.objects.filter(Q(excluido=False)):
            endereco_list = list()
            endereco_list.append(trata_campo(query.logradouro))
            endereco_list.append(trata_campo(query.bairro))
            endereco_list.append(trata_campo(query.numero))
            endereco_list.append(trata_campo(query.complemento))
            endereco_list.append(trata_campo(query.cep))
            endereco_list.append(trata_campo(query.andar))
            endereco_list.append(trata_campo(query.sala))
            endereco_list.append(trata_campo(query.observacao))
            endereco_list.append(trata_campo(query.cidade.nome))
            endereco_list.append(trata_campo(query.estado.nome))

            for endereco in endereco_list:
                if busca in endereco:
                    queryset |= Endereco.objects.filter(pk=query.pk)
                        
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)
        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if Base().check_registro_excluido(Endereco, pk):
                return Response({"non_field_errors": mensagens.NAO_PERMITIDO}, status=status.HTTP_400_BAD_REQUEST)
            Endereco.objects.filter(id=pk).update(excluido=True, 
                                                    usuario_exclusao=user.get_user(self), 
                                                    delete_at=datetime.now())
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"non_field_errors": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self),
                        updated_at=datetime.now())


class TelefoneViewSet(LoggingMixin, Base, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = TelefoneSerializer
    pagination_class = Paginacao
    queryset = Telefone.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ('numero', 'tipo', 'privado')
    filter_fields = ('numero', 'tipo', 'privado')
    ordering = ('numero', 'tipo')

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_tamanho_telefone(requisicao=requisicao):
                return Response({"detail": mensagens.MSG4}, status=status.HTTP_400_BAD_REQUEST)
            if self.check_telefone_exists(requisicao=requisicao):
                return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)

            return super(TelefoneViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response({"non_field_errors": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(Telefone, requisicao["id"]):
                return Response({"non_field_errors": mensagens.NAO_PERMITIDO}, status=status.HTTP_400_BAD_REQUEST)
            if self.check_tamanho_telefone(requisicao=requisicao):
                return Response({"detail": mensagens.MSG4}, status=status.HTTP_400_BAD_REQUEST) 
            if self.check_telefone_exists(requisicao):
                return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)
                
            return super(TelefoneViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response({"non_field_errors": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST)

    def filter_queryset(self, queryset):
        queryset = super(TelefoneViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get('search'))
        privado = trata_campo_ativo(parametros_busca.get('privado'))

        for query in Telefone.objects.filter(Q(excluido=False)):
            telefone_list = list()
            localizado = False
            telefone_list.append(trata_campo(query.tipo))
            telefone_list.append(trata_campo(query.andar))
            telefone_list.append(trata_campo(query.sala))
            telefone_list.append(trata_campo(query.observacao))
            numero = trata_campo(query.numero)

            for telefone in telefone_list:
                if busca in telefone:
                    localizado = True
                    break

            if localizado or trata_telefone(busca) in numero:
                queryset |= Telefone.objects.filter(pk=query.pk)
 
        if privado is not None:
            queryset=queryset.filter(Q(privado=privado, excluido=False))
        
        if parametros_busca.get('tipo'):
            tipo_telefone = trata_campo(parametros_busca.get('tipo'))
            queryset=queryset.filter(Q(tipo=tipo_telefone, excluido=False))
        
        if parametros_busca.get('numero'):
            numero = trata_campo(parametros_busca.get('numero'))
            queryset=queryset.filter(Q(numero=trata_telefone(numero), excluido=False))
        
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)
        return queryset
    
    def check_tamanho_telefone(self, requisicao):
        tamanho_telefone = len(requisicao.get('numero')) > 11
        return tamanho_telefone

    def check_telefone_exists(self, requisicao):
        numero = trata_campo(requisicao.get('numero'))
        return Telefone.objects.filter(Q(numero=numero) &
                                       (~Q(id=requisicao.get('id')) & ~Q(excluido=True)))
    
    def check_vinculos(self, id):
        vinculo = Pessoa.objects.filter(telefones=id, excluido=False).exists()
        is_ramal = Telefone.objects.filter(id=id, tipo='RAMAL').exists()
        if not vinculo and is_ramal:
            vinculo = Setor.objects.filter(telefones=id, excluido=False).exists()
        return vinculo

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if Base().check_registro_excluido(Telefone, pk):
                return Response({"non_field_errors": mensagens.NAO_PERMITIDO}, status=status.HTTP_400_BAD_REQUEST)
            if not Base().check_registro_exists(Telefone, pk):
                return Response({"detail": mensagens.NAO_ENCONTRADO},
                                status=status.HTTP_404_NOT_FOUND)
            if self.check_vinculos(pk):
                return Response({"non_field_errors": mensagens.MSG16}, status=status.HTTP_400_BAD_REQUEST)
            Telefone.objects.filter(id=pk).update(excluido=True, 
                                                    usuario_exclusao=user.get_user(self), 
                                                    delete_at=datetime.now())
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"non_field_errors": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self),
                        updated_at=datetime.now())
