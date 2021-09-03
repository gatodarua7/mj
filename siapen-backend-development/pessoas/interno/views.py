from pessoas.interno.choices import CARACTERISTICAS_DICT
from cadastros.models import Documentos
from itertools import permutations
from django.db.models import Q
from django.forms.models import model_to_dict
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
from localizacao.models import Cidade, Estado
from rest_framework.filters import SearchFilter, OrderingFilter
import collections
from pessoas.interno.serializers import (
    InternoSerializer,
    RgSerializer,
    OutroNomeSerializer,
    VulgoSerializer,
    ContatosSerializer,
    SinaisParticularesSerializer,
)
from pessoas.interno.choices import CARACTERISTICAS_DICT
from pessoas.interno.models import (
    Interno,
    OutroNome,
    Vulgo,
    Contatos,
    Rg,
    SinaisParticulares,
    InternoVulgosThroughModel,
)
from comum.models import Endereco, Telefone
from cadastros.models import OrgaoExpedidor
from rest_framework import status, viewsets
from util.paginacao import Paginacao
from util.busca import (
    trata_campo,
    trata_campo_ativo,
    trata_telefone,
    check_duplicidade,
    get_ids,
)
from util import mensagens, validador, user
from datetime import datetime, date
from uuid import UUID
import ast
from util.busca import formata_data, formata_data_hora
from core.views import Base


class InternoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = InternoSerializer
    pagination_class = Paginacao
    queryset = Interno.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "cpf", "data_nascimento", "id", "vulgo__nome")
    filter_fields = ("nome", "cpf", "data_nascimento", "id", "vulgo__nome")

    ordering_fields = ("nome", "cpf", "data_nascimento", "vulgo")
    ordering = ("nome", "cpf", "data_nascimento", "vulgo")

    def create(self, request, *args, **kwargs):
        requisicao = request.data
        try:
            data_nascimento = (
                requisicao.get("data_nascimento")
                if requisicao.get("data_nascimento")
                else None
            )

            if self.check_interno_exists(requisicao):
                return Response(
                    {"cpf": mensagens.MSG4}, status=status.HTTP_400_BAD_REQUEST
                )
            if data_nascimento and not self.check_maioridade_penal(data_nascimento):
                return Response(
                    {"data_nascimento": mensagens.MSG26},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if (
                requisicao.get("naturalidade") and requisicao.get("estado")
            ) and not self.check_cidade(requisicao):
                return Response(
                    {"naturalidade": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(InternoViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        requisicao = request.data
        try:
            data_nascimento = (
                requisicao.get("data_nascimento")
                if requisicao.get("data_nascimento")
                else None
            )

            if self.check_interno_exists(requisicao):
                return Response(
                    {"cpf": mensagens.MSG4}, status=status.HTTP_400_BAD_REQUEST
                )
            if not self.check_maioridade_penal(data_nascimento):
                return Response(
                    {"data_nascimento": mensagens.MSG26},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Interno, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if (
                requisicao.get("naturalidade") and requisicao.get("estado")
            ) and not self.check_cidade(requisicao):
                return Response(
                    {"naturalidade": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(InternoViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(InternoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        queryset_interno = Interno.objects.none()
        list_queryset = list()
        for query in Interno.objects.filter(Q(excluido=False)):
            qs = Interno.objects.none()
            interno_list = list()
            interno_list2 = list()

            interno_list.append(trata_campo(query.nome))
            interno_list.append(trata_campo(query.nome_social))
            interno_list2.append(trata_campo(query.cpf))
            interno_list.append(formata_data(trata_campo(query.data_nascimento)))
            interno_list.append(trata_campo(query.nome_pai))
            interno_list.append(trata_campo(query.nome_mae))
            interno_list.append(
                trata_campo(query.genero.descricao) if query.genero else ""
            )
            interno_list.append(trata_campo(query.raca.nome) if query.raca else "")
            interno_list.append(
                trata_campo(query.estado_civil.nome) if query.estado_civil else ""
            )
            interno_list.append(trata_campo(query.estado.nome) if query.estado else "")
            interno_list.append(
                trata_campo(query.naturalidade.nome) if query.naturalidade else ""
            )
            interno_list.append(
                trata_campo(query.grau_instrucao.nome) if query.grau_instrucao else ""
            )
            interno_list.append(
                trata_campo(query.orientacao_sexual.nome)
                if query.orientacao_sexual
                else ""
            )
            interno_list.append(
                trata_campo(query.religiao.nome) if query.religiao else ""
            )
            interno_list.extend(
                [
                    trata_campo(necessidade.nome)
                    for necessidade in query.necessidade_especial.all()
                ]
            )
            interno_list.extend(
                [
                    trata_campo(vulgo)
                    for vulgo in InternoVulgosThroughModel.objects.filter(
                        interno_id=query.id
                    )
                ]
            )
            interno_list.extend(
                [
                    trata_campo(outros_nomes.nome)
                    for outros_nomes in OutroNome.objects.filter(
                        interno_id=query.id, excluido=False
                    )
                ]
            )
            for rg in Rg.objects.filter(interno_id=query.id, excluido=False):
                interno_list.append(trata_campo(rg.numero))
                interno_list.append(trata_campo(rg.orgao_expedidor.nome))
                interno_list.append(trata_campo(rg.orgao_expedidor.sigla))
                interno_list.append(trata_campo(rg.orgao_expedidor.estado))

            interno_list.append(
                trata_campo(query.profissao.nome) if query.profissao else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_cutis)
                if query.get_caracteristicas_cutis_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_cor_cabelo)
                if query.get_caracteristicas_cor_cabelo_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_tipo_cabelo)
                if query.get_caracteristicas_tipo_cabelo_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_tipo_rosto)
                if query.get_caracteristicas_tipo_rosto_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_tipo_testa)
                if query.get_caracteristicas_tipo_testa_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_tipo_olhos)
                if query.get_caracteristicas_tipo_olhos_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_cor_olhos)
                if query.get_caracteristicas_cor_olhos_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_nariz)
                if query.get_caracteristicas_nariz_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_labios)
                if query.get_caracteristicas_labios_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_compleicao)
                if query.get_caracteristicas_compleicao_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_sobrancelhas)
                if query.get_caracteristicas_sobrancelhas_display()
                else ""
            )
            interno_list.append(
                trata_campo(query.caracteristicas_orelhas)
                if query.get_caracteristicas_orelhas_display()
                else ""
            )

            for contato in Contatos.objects.filter(interno_id=query.id, excluido=False):
                interno_list.append(trata_campo(contato.nome))
                interno_list.append(trata_campo(contato.tipo_vinculo.nome))
                for endereco in contato.enderecos.all():
                    interno_list.append(trata_campo(endereco.logradouro))
                    interno_list.append(trata_campo(endereco.bairro))
                    interno_list.append(trata_campo(endereco.numero))
                    interno_list.append(trata_campo(endereco.complemento))
                    interno_list.append(trata_campo(endereco.cep))
                    interno_list.append(trata_campo(endereco.estado))
                    interno_list.append(trata_campo(endereco.cidade.nome))
                    interno_list.append(trata_campo(endereco.andar))
                    interno_list.append(trata_campo(endereco.sala))
                    interno_list.append(trata_campo(endereco.observacao))
                for telefone in contato.telefones.all():
                    interno_list2.append(trata_campo(telefone.numero))
                    interno_list.append(trata_campo(telefone.tipo))
                    interno_list.append(trata_campo(telefone.andar))
                    interno_list.append(trata_campo(telefone.sala))
                    interno_list.append(trata_campo(telefone.observacao))
                    interno_list.append(trata_campo(telefone.privado))

            for sinais in SinaisParticulares.objects.filter(
                interno_id=query.id, excluido=False
            ):
                interno_list.append(trata_campo(sinais.tipo))
                interno_list.append(trata_campo(sinais.descricao))

            for documento in query.documentos.all():
                interno_list.append(trata_campo(documento.tipo.nome))
                interno_list.append(trata_campo(documento.num_cod))
                interno_list.append(trata_campo(documento.observacao))
                interno_list.append(formata_data_hora(documento.created_at))
                if documento.updated_at:
                    interno_list.append(formata_data_hora(documento.updated_at))
                interno_list.append(formata_data(trata_campo(documento.data_validade)))

            interno_list.extend(
                [trata_campo(pais.nome) for pais in query.nacionalidade.all()]
            )

            for interno in interno_list:
                if busca in interno:
                    qs = Interno.objects.filter(pk=query.pk)
                    break

            if not qs:
                for interno in interno_list2:
                    if trata_telefone(busca) in interno:
                        qs = Interno.objects.filter(pk=query.pk)
                        break

            if not queryset_interno:
                queryset_interno = qs
                queryset = queryset_interno
            elif qs:
                queryset = queryset | qs

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        if parametros_busca.get("fields"):
            for qf in queryset:
                if qf not in list_queryset:
                    qf.vulgo.set(qf.vulgo.all())
                    list_queryset.append(qf)

                if list_queryset:
                    queryset = list_queryset

        return queryset

    def check_interno_exists(self, requisicao):
        cpf = check_duplicidade(requisicao.get("cpf"))
        return Interno.objects.filter(
            Q(cpf__iexact=cpf, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def perform_create(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["documentos"] = get_ids(requisicao.get("documentos"))
        kwargs["usuario_cadastro"] = user.get_user(self)
        serializer.save(**kwargs)
        self.create_many_fields(serializer=serializer)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["updated_at"] = datetime.now()
        kwargs["documentos"] = get_ids(requisicao.get("documentos"))
        kwargs["usuario_edicao"] = user.get_user(self)
        serializer.save(**kwargs)
        pk = serializer.data.get("id")
        self.update_many_fields(pk=pk)

    def check_cidade(self, requisicao):
        return Cidade.objects.filter(
            Q(id=requisicao["naturalidade"], estado_id=requisicao["estado"])
        ).exists()

    def check_maioridade_penal(self, nascimento):
        maioridade_penal = True
        idade = validador.idade(nascimento)

        if idade and idade < 18:
            maioridade_penal = False

        return maioridade_penal

    def create_many_fields(self, serializer):
        requisicao = self.request.data
        try:
            vulgo_nome = ast.literal_eval(requisicao.get("vulgo"))
        except Exception:
            vulgo_nome = requisicao.get("vulgo") if requisicao.get("vulgo") else None

        try:

            outros_nomes = ast.literal_eval(requisicao.get("outros_nomes"))
        except Exception:
            outros_nomes = (
                self.request.data.get("outros_nomes")
                if self.request.data.get("outros_nomes")
                else None
            )
        if vulgo_nome:
            for nome_vulgo in vulgo_nome:
                if nome_vulgo.strip():
                    outro_nome = nome_vulgo.strip()
                    id_vulgo, created = Vulgo.objects.get_or_create(nome=nome_vulgo)
                    InternoVulgosThroughModel.objects.get_or_create(
                        interno_id=serializer.data["id"], vulgo_id=id_vulgo.id
                    )

        if outros_nomes:
            for outro_nome in outros_nomes:
                if outro_nome.strip():
                    outro_nome = outro_nome.strip()
                    OutroNome.objects.update_or_create(
                        nome=outro_nome,
                        usuario_cadastro=user.get_user(self),
                        interno_id=serializer.data["id"],
                        ativo=True,
                    )

        if self.request.data.get("contatos"):
            for contato in self.request.data.get("contatos"):
                Contatos.objects.filter(id=contato.get("id")).update(
                    interno_id=serializer.data["id"]
                )

        if self.request.data.get("sinais"):
            for sinais in self.request.data.get("sinais"):
                SinaisParticulares.objects.filter(id=sinais.get("id")).update(
                    interno_id=serializer.data["id"]
                )

        if self.request.data.get("rgs"):
            for rg in self.request.data.get("rgs"):
                Rg.objects.filter(id=rg.get("id")).update(
                    interno_id=serializer.data["id"]
                )

    def update_many_fields(self, pk):
        requisicao = self.request.data

        try:
            vulgo_nome = ast.literal_eval(requisicao.get("vulgo"))
        except Exception:
            vulgo_nome = requisicao.get("vulgo") if requisicao.get("vulgo") else None

        try:
            outros_nomes = ast.literal_eval(requisicao.get("outros_nomes"))
        except Exception:
            outros_nomes = (
                requisicao.get("outros_nomes")
                if requisicao.get("outros_nomes")
                else None
            )

        if vulgo_nome:
            for nome_vulgo in vulgo_nome:
                if nome_vulgo.strip():
                    nome = nome_vulgo.strip()
                    id_vulgo, created = Vulgo.objects.get_or_create(nome=nome)
                    InternoVulgosThroughModel.objects.get_or_create(
                        interno_id=pk, vulgo_id=id_vulgo.id
                    )
            novos_vulgos = Vulgo.objects.filter(nome__in=vulgo_nome).values_list(
                "id", flat=True
            )
            for interno_vulgo in InternoVulgosThroughModel.objects.filter(
                ~Q(vulgo_id__in=novos_vulgos) & Q(interno_id=pk)
            ):
                InternoVulgosThroughModel.objects.filter(
                    Q(pk=interno_vulgo.pk)
                ).delete()
        elif not vulgo_nome and InternoVulgosThroughModel.objects.filter(
            Q(interno_id=pk)
        ):
            InternoVulgosThroughModel.objects.filter(Q(interno_id=pk)).delete()

        if outros_nomes:
            for outro_nome in OutroNome.objects.filter(
                ~Q(nome__in=outros_nomes) & Q(interno_id=pk)
            ):
                OutroNome.objects.filter(Q(pk=outro_nome.pk)).delete()
            for outro_nome in outros_nomes:
                if outro_nome.strip():
                    outro_nome = outro_nome.strip()
                    OutroNome.objects.update_or_create(
                        nome=outro_nome,
                        usuario_cadastro=user.get_user(self),
                        interno_id=UUID(pk),
                        ativo=True,
                    )
        elif not outros_nomes and OutroNome.objects.filter(interno_id=pk):
            OutroNome.objects.filter(Q(interno_id=pk)).delete()

    @action(
        detail=False,
        methods=["get"],
        url_path="caracteristicas",
        url_name="caracteristicas",
    )
    def caracteristicas(self, request):
        return Response(CARACTERISTICAS_DICT, status=status.HTTP_200_OK)


class RgViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = RgSerializer
    pagination_class = Paginacao
    queryset = Rg.objects.filter(excluido=False)
    filter_backends = (SearchFilter,)
    search_fields = "numero"

    def create(self, request, *args, **kwargs):
        try:
            return super(RgViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super(RgViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            Rg.objects.filter(id=pk).update(
                ativo=False,
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self))


class OutroNomeViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = OutroNomeSerializer
    pagination_class = Paginacao
    queryset = OutroNome.objects.filter(excluido=False)
    filter_backends = (SearchFilter,)
    search_fields = ("outro", "pessoa__nome", "data_cadastro")

    def create(self, request, *args, **kwargs):
        try:
            return super(OutroNomeViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super(OutroNomeViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            OutroNome.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self))


class VulgoViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = VulgoSerializer
    pagination_class = Paginacao
    queryset = Vulgo.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = "nome"
    ordering_fields = "nome"
    ordering = "nome"

    def create(self, request, *args, **kwargs):
        try:
            return super(VulgoViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super(VulgoViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ContatosViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = ContatosSerializer
    pagination_class = Paginacao
    queryset = Contatos.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "tipo_vinculo__nome", "ativo")
    filter_fields = ("nome", "tipo_vinculo__nome", "ativo")
    ordering_fields = ("nome", "tipo_vinculo__nome", "ativo")
    ordering = ("nome", "tipo_vinculo__nome", "ativo")

    def create(self, request, *args, **kwargs):

        try:
            return super(ContatosViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Contatos, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if self.check_registro_excluido(pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(ContatosViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Contatos, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if self.check_registro_excluido(pk):
                return Response(
                    {"detail": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Contatos.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def filter_queryset(self, queryset):
        queryset = super(ContatosViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        contato_queryset = None
        if parametros_busca.get("interno"):
            for query in Contatos.objects.filter(
                Q(excluido=False, interno=parametros_busca.get("interno"))
            ):
                qs = None
                contato_list = list()
                contato_list2 = list()

                contato_list.append(trata_campo(query.nome))
                contato_list.append(trata_campo(query.tipo_vinculo.nome))

                for endereco in query.enderecos.all():
                    contato_list.append(trata_campo(endereco.logradouro))
                    contato_list.append(trata_campo(endereco.bairro))
                    contato_list.append(trata_campo(endereco.numero))
                    contato_list.append(trata_campo(endereco.cidade.nome))
                    contato_list.append(trata_campo(endereco.estado.nome))
                    contato_list.append(trata_campo(endereco.estado.sigla))
                    contato_list.append(trata_campo(endereco.observacao))
                    contato_list.append(trata_campo(endereco.complemento))
                    contato_list2.append(
                        trata_campo(endereco.cep.replace("-", "").replace(".", ""))
                    )
                    contato_list.append(trata_campo(endereco.andar))
                    contato_list.append(trata_campo(endereco.sala))

                for telefone in query.telefones.all():
                    contato_list.append(trata_campo(telefone.tipo))
                    contato_list2.append(trata_campo(telefone.numero))
                    contato_list.append(trata_campo(telefone.observacao))

                for contato in contato_list:
                    if busca in contato:
                        qs = Contatos.objects.filter(pk=query.pk)
                        break

                if not qs:
                    for contato in contato_list2:
                        if trata_telefone(busca) in contato:
                            qs = Contatos.objects.filter(pk=query.pk)
                            break

                if not contato_queryset:
                    contato_queryset = qs
                    queryset = contato_queryset
                elif qs:
                    queryset = queryset | qs

            queryset = queryset.filter(interno=parametros_busca.get("interno"))

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_registro_excluido(self, id):
        return Contatos.objects.filter(Q(id=id) & Q(excluido=True))

    def perform_create(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["telefones"] = self.get_telefones(requisicao)
        kwargs["enderecos"] = get_ids(requisicao.get("enderecos"))
        kwargs["usuario_cadastro"] = user.get_user(self)
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["updated_at"] = datetime.now()
        kwargs["telefones"] = self.get_telefones(requisicao)
        kwargs["enderecos"] = get_ids(requisicao.get("enderecos"))
        kwargs["usuario_edicao"] = user.get_user(self)
        serializer.save(**kwargs)

    def get_telefones(self, request):
        list_telefones = list()
        for telefone in request.get("telefones"):
            privado = True
            Telefone.objects.filter(
                Q(id=telefone["id"]) & (Q(tipo="CELULAR") | Q(tipo="RESIDENCIAL"))
            ).update(privado=privado)
            list_telefones.append(telefone["id"])
        return list_telefones


class SinaisParticularesViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = SinaisParticularesSerializer
    pagination_class = Paginacao
    queryset = SinaisParticulares.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("tipo", "ativo", "area")
    filter_fields = ("tipo", "ativo", "area")
    ordering_fields = ("tipo", "ativo")
    ordering = ("tipo", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            return super(SinaisParticularesViewSet, self).create(
                request, *args, **kwargs
            )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(SinaisParticulares, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if self.check_registro_excluido(pk):
                return Response(
                    {"detail": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(SinaisParticularesViewSet, self).update(
                request, *args, **kwargs
            )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(SinaisParticulares, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if self.check_registro_excluido(pk):
                return Response(
                    {"detail": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            SinaisParticulares.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def filter_queryset(self, queryset):
        queryset = super(SinaisParticularesViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        area = trata_campo(parametros_busca.get("area"))

        if area:
            queryset = queryset.filter(area=area)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_registro_excluido(self, id):
        return SinaisParticulares.objects.filter(Q(id=id) & Q(excluido=True))

    def perform_create(self, serializer, **kwargs):
        kwargs["usuario_cadastro"] = user.get_user(self)
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        if requisicao.get("motivo_exclusao"):
            kwargs["delete_at"] = datetime.now()
            kwargs["excluido"] = True
            kwargs["usuario_exclusao"] = user.get_user(self)
            kwargs["motivo_exclusao"] = requisicao.get("motivo_exclusao")
        else:
            kwargs["updated_at"] = datetime.now()
            kwargs["usuario_edicao"] = user.get_user(self)
        serializer.save(**kwargs)
