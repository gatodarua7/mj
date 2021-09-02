from pessoas.advogado.models import Advogado, RgAdvogado
from movimentacao.models import PedidoInclusao
from django.core.validators import ProhibitNullCharactersValidator
from django.db.models import Q
from mj_crypt.mj_crypt import AESCipher
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
from rest_framework.filters import SearchFilter, OrderingFilter
from cadastros.serializers import (
    FotoSerializer,
    GeneroSerializer,
    PessoaSerializer,
    TipoDocumentoSerializer,
    FuncaoSerializer,
    CargosSerializer,
    OrgaoExpedidorSerializer,
    RegimePrisionalSerializer,
    PericulosidadeSerializer,
    DocumentosSerializer,
    DocumentosPostSerializer,
    SetorSerializer,
    ComportamentoInternoSerializer
)
from cadastros.models import (
    Foto,
    Genero,
    Pessoa,
    TipoDocumento,
    Funcao,
    Cargos,
    OrgaoExpedidor,
    RegimePrisional,
    Periculosidade,
    Documentos,
    Setor,
    ComportamentoInterno
)
from comum.models import Telefone, Endereco
from localizacao.models import Cidade
from pessoas.servidor.models import Servidor
from visitante.models import Visitante
from pessoas.interno.models import Interno
from rest_framework import status, viewsets
from util.paginacao import Paginacao
from util.busca import (
    trata_campo,
    trata_campo_ativo,
    trata_telefone,
    check_duplicidade,
    formata_data,
    formata_data_hora
)
from util import mensagens, validador, user
from validate_docbr import CPF
from uuid import UUID
from datetime import datetime
from imagehelpers.image import image_size
from core.views import Base


class FotoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = FotoSerializer
    pagination_class = Paginacao
    queryset = Foto.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("id", "ativo")
    filter_fields = ("id", "ativo")
    ordering_fields = ("id", "ativo")
    ordering = ("id", "ativo")
    DEFAULT_IMAGE_SIZE = (720, 480)
    FORMATOS_VALIDOS = ["png", "jpeg", "jpg"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if (
            request.data.get("foto_temp").name.split(".")[-1].lower()
            not in self.FORMATOS_VALIDOS
        ):
            return Response(
                {"non_field_errors": "Apenas formatos png, jpeg e jpg são permitidos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if image_size(request.data.get("foto_temp")) < self.DEFAULT_IMAGE_SIZE:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response_data = {}
            response_data.update(serializer.data)
            response_data.update({"detail": mensagens.IMG_BAIXA_RESOLUCAO})
            return Response(
                response_data, status=status.HTTP_201_CREATED, headers=headers
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, pk, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if request.data.get("foto_temp"):
            if (
                request.data.get("foto_temp").name.split(".")[-1].lower()
                not in self.FORMATOS_VALIDOS
            ):
                return Response(
                    {
                        "non_field_errors": "Apenas formatos png, jpeg e jpg são permitidos."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if image_size(request.data.get("foto_temp")) < self.DEFAULT_IMAGE_SIZE:
                self.perform_update(serializer)
                headers = self.get_success_headers(serializer.data)
                response_data = {}
                response_data.update(serializer.data)
                response_data.update({"detail": mensagens.IMG_BAIXA_RESOLUCAO})
                return Response(
                    response_data, status=status.HTTP_201_CREATED, headers=headers
                )

        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Foto, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            Foto.objects.filter(id=pk).update(
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
        queryset = super(FotoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        queryset = Foto.objects.filter(Q(excluido=False))
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self), ativo=True)

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class GeneroViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = GeneroSerializer
    pagination_class = Paginacao
    queryset = Genero.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("descricao",)
    filter_fields = ("descricao",)
    ordering_fields = ("descricao", "ativo")
    ordering = ("descricao", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_genero_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(GeneroViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(Genero, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Genero, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_genero_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(GeneroViewSet, self).update(request, *args, **kwargs)


    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Genero, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Genero, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_pessoa_genero(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Genero.objects.filter(id=pk).update(
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
        queryset = super(GeneroViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for genero in Genero.objects.filter(Q(excluido=False)):
            descricao = trata_campo(genero.descricao)
            if busca in descricao:
                queryset |= Genero.objects.filter(pk=genero.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_genero_exists(self, requisicao):
        genero = check_duplicidade(requisicao.get("descricao"))
        return Genero.objects.filter(
            Q(descricao__iexact=genero)
            & (~Q(id=requisicao.get("id")) & Q(excluido=False))
        )

    def check_pessoa_genero(self, id):
        pessoa = Pessoa.objects.filter(Q(genero=id, excluido=False)).exists()
        if pessoa:
            return pessoa
        return Servidor.objects.filter(Q(genero=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class FuncaoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = FuncaoSerializer
    pagination_class = Paginacao
    queryset = Funcao.objects.filter(excluido=False)
    filter_backends = (SearchFilter,)
    filter_fields = ("descricao",)
    search_fields = ("descricao", "ativo")
    ordering = ("descricao", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_funcao_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

        return super(FuncaoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(Funcao, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Funcao, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_funcao_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(FuncaoViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Funcao, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Funcao, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_vinculos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Funcao.objects.filter(id=pk).update(
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
        queryset = super(FuncaoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for funcao in Funcao.objects.filter(Q(excluido=False)):
            descricao = trata_campo(funcao.descricao)
            if busca in descricao:
                queryset |= Funcao.objects.filter(pk=funcao.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_vinculos(self, id):
        return Servidor.objects.filter(Q(funcao=id, excluido=False)).exists()

    def check_funcao_exists(self, requisicao):
        funcao = check_duplicidade(requisicao.get("descricao"))
        return Funcao.objects.filter(
            Q(descricao__iexact=funcao)
            & (~Q(id=requisicao.get("id")) & Q(excluido=False))
        )

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class PessoaViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = PessoaSerializer
    pagination_class = Paginacao
    queryset = Pessoa.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)

    filter_fields = (
        "nome",
        "nome_social",
        "cpf",
        "rg",
        "orgao_expedidor",
        "genero__descricao",
        "raca__nome",
        "estado_civil__nome",
        "nacionalidade",
        "estado",
        "naturalidade",
        "nome_mae",
        "nome_pai",
        "grau_instrucao",
        "profissao",
        "necessidade_especial",
        "orientacao_sexual",
        "religiao",
        "enderecos",
        "telefones",
    )

    search_fields = (
        "nome",
        "nome_social",
        "cpf",
        "rg",
        "orgao_expedidor",
        "genero__descricao",
        "raca__nome",
        "estado_civil__nome",
        "nacionalidade__nome",
        "estado__nome",
        "naturalidade__nome",
        "nome_mae",
        "nome_pai",
        "grau_instrucao__nome",
        "profissao__nome",
        "necessidade_especial__nome",
        "orientacao_sexual__nome",
        "religiao__nome",
        "enderecos__logradouro",
        "telefones__numero",
    )

    ordering_fields = ("nome", "cpf", "ativo")
    ordering = ("nome", "ativo")
    cpf = CPF()

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data

            if requisicao.get("cpf") and not self.cpf.validate(requisicao.get("cpf")):
                return Response(
                    {"non_field_errors": "CPF inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if (
                requisicao.get("cidade") and requisicao.get("estado")
            ) and not self.check_cidade(requisicao):
                return Response(
                    {"non_field_errors": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(PessoaViewSet, self).create(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data

            if requisicao.get("cpf") and not self.cpf.validate(requisicao.get("cpf")):
                return Response(
                    {"non_field_errors": "CPF inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if (
                requisicao.get("cidade") and requisicao.get("estado")
            ) and not self.check_cidade(requisicao):
                return Response(
                    {"non_field_errors": mensagens.ERRO_CIDADE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_excluido(Pessoa, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Pessoa, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(PessoaViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Pessoa, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Pessoa, pk):
                return Response(
                    {"detail": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Pessoa.objects.filter(id=pk).update(excluido=True)
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG_ERRO}, status=status.HTTP_400_BAD_REQUEST
            )

    def filter_queryset(self, queryset):
        queryset = super(PessoaViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        queryset_pessoa = Pessoa.objects.none()
        for query in Pessoa.objects.filter(Q(excluido=False)):
            qs = None
            pessoa_list = list()
            pessoa_list2 = list()
            pessoa_list.append(trata_campo(query.nome))
            pessoa_list.append(trata_campo(query.nome_social))
            pessoa_list2.append(trata_campo(query.cpf))
            pessoa_list.append(trata_campo(query.rg))
            pessoa_list.append(formata_data(trata_campo(query.data_nascimento)))
            pessoa_list.append(trata_campo(query.nome_pai))
            pessoa_list.append(trata_campo(query.nome_mae))
            pessoa_list.append(trata_campo(query.orgao_expedidor))
            pessoa_list.append(trata_campo(query.genero.descricao) if query.genero else "")
            pessoa_list.append(trata_campo(query.raca.nome) if query.raca else "")
            pessoa_list.append(
                trata_campo(query.estado_civil.nome) if query.estado_civil else ""
            )
            pessoa_list.append(
                trata_campo(query.nacionalidade.nome) if query.nacionalidade else ""
            )
            pessoa_list.append(trata_campo(query.estado.nome) if query.estado else "")
            pessoa_list.append(
                trata_campo(query.naturalidade.nome) if query.naturalidade else ""
            )
            pessoa_list.append(
                trata_campo(query.grau_instrucao.nome) if query.grau_instrucao else ""
            )
            pessoa_list.append(trata_campo(query.profissao.nome) if query.profissao else "")
            pessoa_list.append(
                trata_campo(query.orientacao_sexual.nome)
                if query.orientacao_sexual
                else ""
            )
            pessoa_list.append(trata_campo(query.religiao.nome) if query.religiao else "")

            pessoa_list.extend([
                trata_campo(necessidade.nome)
                for necessidade in query.necessidade_especial.all()
            ])

            for endereco in query.enderecos.all():
                pessoa_list.append(trata_campo(endereco.logradouro))
                pessoa_list.append(trata_campo(endereco.bairro))
                pessoa_list.append(trata_campo(endereco.numero))
                pessoa_list.append(trata_campo(endereco.cidade.nome))
                pessoa_list.append(trata_campo(endereco.estado.nome))
                pessoa_list.append(trata_campo(endereco.estado.sigla))
                pessoa_list.append(trata_campo(endereco.observacao))
                pessoa_list.append(trata_campo(endereco.complemento))
                pessoa_list2.append(trata_campo(endereco.cep.replace("-", "").replace(".", "")))
                pessoa_list.append(trata_campo(endereco.andar))
                pessoa_list.append(trata_campo(endereco.sala))

            for telefone in query.telefones.all():
                pessoa_list.append(trata_campo(telefone.tipo))
                pessoa_list2.append(trata_campo(telefone.numero))
                pessoa_list.append(trata_campo(telefone.observacao))
                pessoa_list.append(trata_campo(telefone.andar))
                pessoa_list.append(trata_campo(telefone.sala))

            for pessoa in pessoa_list:
                if busca in pessoa:
                    qs = Pessoa.objects.filter(pk=query.pk)
                    break

            if not qs:
                for pessoa in pessoa_list2:
                    if trata_telefone(busca) in pessoa:
                        qs = Pessoa.objects.filter(pk=query.pk)
                        break

            if queryset_pessoa:
                queryset_pessoa = qs
                queryset = queryset_pessoa
            elif qs:
                queryset = queryset | qs

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset


    def check_cidade(self, requisicao):
        return Cidade.objects.filter(
            Q(id=requisicao["cidade"], estado_id=requisicao["estado"])
        ).exists()

    def perform_create(self, serializer):
        list_telefones = self.get_telefones(self.request.data)
        enderecos = self.get_endereco(self.request.data)

        serializer.save(
            usuario_cadastro=user.get_user(self),
            telefones=list_telefones,
            enderecos=enderecos,
        )

    def perform_update(self, serializer):
        list_telefones = self.get_telefones(self.request.data)
        enderecos = self.get_endereco(self.request.data)
        serializer.save(
            usuario_edicao=user.get_user(self),
            telefones=list_telefones,
            enderecos=enderecos,
            updated_at=datetime.now(),
        )


    def get_telefones(self, request):
        list_telefones = list()
        for telefone in request.get("telefones"):
            telefone_data = None
            telefone_data = (
                Telefone.objects.filter(
                    Q(numero=telefone["numero"]) & Q(excluido=False)
                )
                .values("id")
                .first()
            )
            if telefone_data:
                telefone_data = telefone_data["id"]
                Telefone.objects.filter(
                    Q(id=telefone_data) & (Q(tipo="CELULAR") | Q(tipo="RESIDENCIAL"))
                ).update(privado=True)
            else:
                privado = True
                if telefone["tipo"] == "RAMAL" or telefone["tipo"] == "FUNCIONAL":
                    privado = False
                telefone_data = Telefone.objects.create(
                    numero=telefone["numero"],
                    tipo=telefone["tipo"],
                    observacao=telefone["observacao"],
                    andar=telefone["andar"],
                    sala=telefone["sala"],
                    created_at=datetime.now(),
                    privado=privado,
                    usuario_cadastro=user.get_user(self),
                )
            list_telefones.append(telefone_data)
        return list_telefones

    def get_endereco(self, request):
        list_enderecos = list()
        for requisicao in request.get("enderecos"):
            endereco = Endereco.objects.create(
                cep=requisicao.get("cep"),
                logradouro=requisicao.get("logradouro"),
                numero=requisicao.get("numero"),
                bairro=requisicao.get("bairro"),
                cidade_id=requisicao.get("cidade"),
                estado_id=requisicao.get("estado"),
                complemento=requisicao.get("complemento"),
                andar=requisicao.get("andar"),
                sala=requisicao.get("sala"),
                observacao=requisicao.get("observacao"),
                usuario_cadastro=user.get_user(self),
            )
            list_enderecos.append(endereco)
        return list_enderecos

    @action(
        detail=False,
        methods=["get"],
        url_path=r"usuarios_telefone/(?P<telefone>\d+)",
        url_name="usuarios_telefone",
    )
    def get_usuarios_telefone(self, request, telefone):
        try:
            nome_pessoas = dict()
            servidor = Servidor.objects.filter(
                (
                    Q(telefones__numero__iexact=trata_telefone(telefone))
                    | Q(
                        telefones_funcionais__numero__iexact=trata_telefone(telefone)
                    )
                )
                & Q(excluido=False)
            ).values_list("nome", flat=True)
            nome_pessoas["nome"] = servidor
            return Response(nome_pessoas, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TipoDocumentoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = TipoDocumentoSerializer
    pagination_class = Paginacao
    queryset = TipoDocumento.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filter_fields = ("nome", "ativo")
    search_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_documento_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(TipoDocumentoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(TipoDocumento, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(TipoDocumento, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_documento_exists(requisicao=requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(TipoDocumentoViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if Base().check_registro_excluido(TipoDocumento, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if self.check_vinculos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            TipoDocumento.objects.filter(id=pk).update(excluido=True)
            return Response({"detail": mensagens.MSG5}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(TipoDocumentoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))
        for tipo_documento in TipoDocumento.objects.filter(Q(excluido=False)):
            nome = trata_campo(tipo_documento.nome)
            if busca in nome:
                queryset |= TipoDocumento.objects.filter(pk=tipo_documento.pk)

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_vinculos(self, id):
        return Documentos.objects.filter(Q(tipo_id=id, excluido=False)).exists()

    def check_documento_exists(self, requisicao):
        documento = check_duplicidade(requisicao.get("nome"))
        return TipoDocumento.objects.filter(
            Q(nome__iexact=documento)
            & (~Q(id=requisicao.get("id")) & Q(excluido=False))
        ).exists()


class CargosViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = CargosSerializer
    pagination_class = Paginacao
    queryset = Cargos.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filter_fields = ("cargo",)
    search_fields = ("cargo",)
    ordering = ("cargo",)

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(CargosViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_inativo(Cargos, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_excluido(Cargos, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(CargosViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Cargos, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Cargos, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_vinculos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Cargos.objects.filter(id=pk).update(
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
        queryset = super(CargosViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for cargo in Cargos.objects.filter(Q(excluido=False)):
            descricao = trata_campo(cargo.cargo)
            if busca in descricao:
                queryset |= Cargos.objects.filter(pk=cargo.pk)

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_vinculos(self, id):
        return Servidor.objects.filter(Q(cargos=id, excluido=False)).exists()

    def check_exists(self, requisicao):
        cargo = check_duplicidade(requisicao.get("cargo"))
        return Cargos.objects.filter(
            Q(cargo__iexact=cargo) & (~Q(id=requisicao.get("id")) & Q(excluido=False))
        ).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class OrgaoExpedidorViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = OrgaoExpedidorSerializer
    pagination_class = Paginacao
    queryset = OrgaoExpedidor.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "estado__nome", "sigla", "ativo")
    filter_fields = ("nome", "estado__nome", "estado", "sigla", "ativo")
    ordering_fields = ("nome", "estado__sigla", "sigla", "ativo")
    ordering = ("nome", "estado__sigla", "sigla", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_orgao_expedidor_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(OrgaoExpedidorViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(OrgaoExpedidor, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(OrgaoExpedidor, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_orgao_expedidor_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(OrgaoExpedidorViewSet, self).update(request, *args, **kwargs)


    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(OrgaoExpedidor, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(OrgaoExpedidor, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_vinculos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_vinculo_advogado(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            OrgaoExpedidor.objects.filter(id=pk).update(
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
        queryset = super(OrgaoExpedidorViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))
        if busca:
            for query in OrgaoExpedidor.objects.filter(Q(excluido=False)):
                orgao_expedidor = list()
                orgao_expedidor.append(trata_campo(query.nome))
                orgao_expedidor.append(trata_campo(query.estado.nome))
                orgao_expedidor.append(trata_campo(query.sigla))

                for item in orgao_expedidor:
                    if busca in item:
                        queryset |= OrgaoExpedidor.objects.filter(pk=query.pk)
                        break

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)
        else:
            queryset = super(OrgaoExpedidorViewSet, self).filter_queryset(queryset)
        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="ufs",
        url_name="ufs",
    )
    def get_ufs(self, request):
        uf_list = list()
        for query in OrgaoExpedidor.objects.filter(Q(excluido=False, ativo=True)):
            nome = query.estado.nome
            if self.check_estado_list(nome, uf_list):
                orgao_dict = {"id": query.estado.id, "nome": nome}
                uf_list.append(orgao_dict)
        retorno = {
            "count": len(uf_list),
            "next": None,
            "previous": None,
            "results": sorted(uf_list, key=lambda row: row["nome"]),
        }

        return Response(retorno, status=status.HTTP_200_OK)

    def check_estado_list(self, estado, lista_estado):
        return filter(lambda uf: uf["nome"] == estado, lista_estado)

    def check_vinculos(self, id):
        return Servidor.objects.filter(Q(orgao_expedidor=id, excluido=False)).exists()

    def check_vinculo_advogado(self, id):
        return RgAdvogado.objects.filter(Q(orgao_expedidor=id, excluido=False)).exists()

    def check_orgao_expedidor_exists(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        sigla = check_duplicidade(requisicao.get("sigla"))
        return OrgaoExpedidor.objects.filter(
            Q(nome__iexact=nome)
            & Q(sigla__iexact=sigla)
            & Q(estado_id=requisicao.get("estado"))
            & (~Q(id=requisicao.get("id")) & Q(excluido=False))
        ).exists()

    def check_vinculo_orgao_expedidor(self, id):
        return OrgaoExpedidor.objects.filter(Q(nome=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class RegimePrisionalViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = RegimePrisionalSerializer
    pagination_class = Paginacao
    queryset = RegimePrisional.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "ativo")
    filter_fields = ("nome", "ativo")
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_regime_prisional_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(RegimePrisionalViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(RegimePrisional, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(RegimePrisional, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_regime_prisional_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(RegimePrisionalViewSet, self).update(request, *args, **kwargs)


    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(RegimePrisional, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(RegimePrisional, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_vinculos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            RegimePrisional.objects.filter(id=pk).update(
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
        queryset = super(RegimePrisionalViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for oe in RegimePrisional.objects.filter(Q(excluido=False)):
            nome = trata_campo(oe.nome)
            if busca in nome:
                queryset |= RegimePrisional.objects.filter(pk=oe.pk)

            if ativo is not None:
                queryset = queryset.filter(ativo=ativo)

        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_regime_prisional_exists(self, requisicao):
        oe = check_duplicidade(requisicao.get("nome"))
        return RegimePrisional.objects.filter(
            Q(nome__iexact=oe) & (~Q(id=requisicao.get("id")) & Q(excluido=False))
        )

    def check_vinculo_orgao_expedidor(self, id):
        return RegimePrisional.objects.filter(Q(nome=id, excluido=False)).exists()
    
    def check_vinculos(self, id):
        return PedidoInclusao.objects.filter(regime_prisional=id).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class PericulosidadeViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = PericulosidadeSerializer
    pagination_class = Paginacao
    queryset = Periculosidade.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "sigla", "observacao", "ativo")
    filter_fields = ("nome", "sigla", "observacao", "ativo")
    ordering_fields = ("nome", "sigla", "observacao", "ativo")
    ordering = ("nome", "sigla", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_periculosidade_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(PericulosidadeViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if Base().check_registro_excluido(Periculosidade, requisicao["id"]):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_inativo(Periculosidade, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_periculosidade_exists(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(PericulosidadeViewSet, self).update(request, *args, **kwargs)


    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(Periculosidade, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(Periculosidade, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Periculosidade.objects.filter(id=pk).update(
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
        queryset = super(PericulosidadeViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        # Transforma string para uppercase, tira apóstrofo e acentos
        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in Periculosidade.objects.filter(Q(excluido=False)):
            periculosisade = list()
            periculosisade.append(trata_campo(query.nome))
            periculosisade.append(trata_campo(query.observacao))
            periculosisade.append(trata_campo(query.sigla))

            for item in periculosisade:
                if busca in item:
                    queryset |= Periculosidade.objects.filter(pk=query.pk)
                    break
      
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        # Ordena queryset
        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_periculosidade_exists(self, requisicao):
        p = check_duplicidade(requisicao.get("nome"))
        return Periculosidade.objects.filter(
            Q(nome__iexact=p) & (~Q(id=requisicao.get("id")) & Q(excluido=False))
        )

    def check_vinculo_orgao_expedidor(self, id):
        return Periculosidade.objects.filter(Q(nome=id, excluido=False)).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())


class DocumentosViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    pagination_class = Paginacao
    queryset = Documentos.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("id", "ativo")
    filter_fields = ("id", "ativo")
    ordering_fields = ("tipo", "num_cod", "observacao")
    ordering = ("tipo", "num_cod", "observacao", "data_validade", "created_at", "updated_at")
    DEFAULT_PDF_FILE_SIZE = 15 * 1024 * 1024
    DEFAULT_IMG_FILE_SIZE = 1 * 1024 * 1024
    DEFAULT_IMAGE_SIZE = (720, 480)
    FORMATOS_VALIDOS = ["png", "jpeg", "jpg", "pdf"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DocumentosSerializer
        return DocumentosPostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.check_documento(request.data):
            return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)
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
        return Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers
        )
            

    def update(self, request, pk, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if self.check_documento(request.data):
            return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)
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

            if not Base().check_registro_exists(Documentos,pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            Documentos.objects.filter(id=pk).update(
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
        queryset = super(DocumentosViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))
        for query in Documentos.objects.filter(Q(excluido=False)):
            documento_list = list()
            documento_list.append(trata_campo(query.num_cod))
            documento_list.append(trata_campo(query.observacao))
            documento_list.append(trata_campo(query.tipo.nome))
            documento_list.append(formata_data_hora(query.created_at))
            if query.updated_at:
                documento_list.append(formata_data_hora(query.updated_at))
            if query.data_validade:
                documento_list.append(formata_data(trata_campo(query.data_validade)))

            for item in documento_list:
                if busca in item:
                    queryset |= Documentos.objects.filter(pk=query.pk)
                    break

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        if parametros_busca.get("interno"):
            documentos = Interno.objects.get(id=parametros_busca.get("interno")).documentos
            doc_list = [doc.id for doc in documentos.all()]
            queryset = queryset.filter(id__in=doc_list)
        elif parametros_busca.get("servidor"):
            documentos = Servidor.objects.get(id=parametros_busca.get("servidor")).documentos
            doc_list = [doc.id for doc in documentos.all()]
            queryset = queryset.filter(id__in=doc_list)
        elif parametros_busca.get("visitante"):
            documentos = Visitante.objects.get(id=parametros_busca.get("visitante")).documentos
            doc_list = [doc.id for doc in documentos.all()]
            queryset = queryset.filter(id__in=doc_list)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_documento(self, requisicao):
        num_cod = check_duplicidade(requisicao.get("num_cod"))
        tipo = requisicao.get("tipo")
        arquivo = requisicao.get("arquivo_temp")
        id_documento = requisicao["id"] if requisicao.get("id") else None
        if not arquivo:
            arquivo_nome = Documentos.objects.get(pk=id_documento).arquivo_temp
        else:
            arquivo_nome = "{0}{1}".format("documentos/", arquivo.name.split(".")[0])
        return Documentos.objects.filter(
            Q(
                tipo_id=tipo,
                num_cod__iexact=num_cod,
                arquivo_temp__istartswith=arquivo_nome,
            )
            & ~Q(id=id_documento)
            & Q(excluido=False)
        )

    def check_registro_excluido(self, id):
        return Documentos.objects.filter(id=id, excluido=True).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())

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
            obj = Documentos.objects.get(id=documento_id, excluido=False)
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


class SetorViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = SetorSerializer
    pagination_class = Paginacao
    queryset = Setor.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "sigla", "telefones__numero", "ativo")
    filter_fields = ("nome", "sigla", "telefones__numero", "ativo")
    ordering_fields = ("nome", "sigla", "enderecos__cep", "ativo")
    ordering = ("nome", "sigla", "enderecos__cep", "ativo")

    def create(self, request, *args, **kwargs):
        requisicao = request.data
        if self.check_setor(requisicao):
            return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)
        if requisicao.get("setor_pai") and (
            Base().check_registro_excluido(Setor, requisicao.get("setor_pai"))
            or self.check_registro_inativo(requisicao.get("setor_pai"))
        ):
            return Response(
                {"non_field_errors": mensagens.NAO_PERMITIDO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if requisicao.get("setor_pai") and not self.check_setor_exists(
            requisicao.get("setor_pai")
        ):
            return Response(
                {"non_field_errors": mensagens.NAO_PERMITIDO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super(SetorViewSet, self).create(request, *args, **kwargs)

    def update(self, request, pk, *args, **kwargs):
        requisicao = request.data
        if requisicao.get("setor_pai") and self.check_registro_pai(
            pk, requisicao.get("setor_pai")
        ):
            return Response(
                {"non_field_errors": mensagens.NAO_PERMITIDO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if self.check_setor(requisicao, pk):
            return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)
        if self.check_setor_pai_filho(pk, requisicao):
            return Response(
                {"non_field_errors": "O setor pai não pode ser igual ao setor filho."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not requisicao.get("ativo") and Base().check_registro_inativo(Setor, requisicao):
            return Response(
                {"non_field_errors": mensagens.INATIVO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not requisicao.get("ativo") and self.check_setor_pai(pk):
            return Response(
                {"non_field_errors": "Há setor filho vinculado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super(SetorViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if self.check_setor_filho_destroy(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Base().check_registro_excluido(Setor, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_vinculos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Setor.objects.filter(id=pk).update(
                excluido=True,
                usuario_exclusao=user.get_user(self),
                delete_at=datetime.now(),
            )
            return Response(
                {"detail": mensagens.MSG5}, status=status.HTTP_204_NO_CONTENT
            )
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        queryset = super(SetorViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        queryset_setor = Setor.objects.none()
        for query in Setor.objects.filter(Q(excluido=False)):
            qs = Setor.objects.none()
            setor_list = list()
            setor_list2 = list()
            setor_list.append(trata_campo(query.nome))
            setor_list.append(trata_campo(query.sigla))

            if query.enderecos:
                setor_list.append(trata_campo(query.enderecos.logradouro))
                setor_list.append(trata_campo(query.enderecos.bairro))
                setor_list.append(trata_campo(query.enderecos.numero))
                setor_list.append(trata_campo(query.enderecos.cidade.nome))
                setor_list.append(trata_campo(query.enderecos.estado.nome))
                setor_list.append(trata_campo(query.enderecos.estado.sigla))
                setor_list.append(trata_campo(query.enderecos.observacao))
                setor_list.append(trata_campo(query.enderecos.complemento))
                setor_list2.append(trata_campo(query.enderecos.cep.replace("-", "").replace(".", "")))
                setor_list.append(trata_campo(query.enderecos.andar))
                setor_list.append(trata_campo(query.enderecos.sala))

            for telefone in query.telefones.all():
                setor_list.append(trata_campo(telefone.tipo))
                setor_list2.append(trata_campo(telefone.numero))
                setor_list.append(trata_campo(telefone.observacao))
                setor_list.append(trata_campo(telefone.andar))
                setor_list.append(trata_campo(telefone.sala))

            for item in setor_list:
                if busca in item:
                    qs = Setor.objects.filter(pk=query.pk)
                    break

            if not qs:
                for item in setor_list2:
                    if trata_telefone(busca) in item:
                        qs = Setor.objects.filter(pk=query.pk)
                        break

            if queryset_setor:
                queryset_setor = qs
                queryset = queryset_setor
            elif qs:
                queryset = queryset | qs

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path=r"treeview-setor/(?P<setor_id>[^/.]+)",
        url_name="treeview-setor",
    )
    def get_arvore_setor(self, request, setor_id):
        try:
            tree = list()
            setor_treeview = self.get_setor(setor_id=setor_id)
            tree.append(setor_treeview)

            return Response(tree, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": mensagens.MSG3}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=False,
        methods=["get"],
        url_path="setor-alocacao",
        url_name="setor-alocacao",
    )
    def setor_alocacao(self, request):
        items = self.get_setor_unidade()
        return Response(items, status=status.HTTP_200_OK)

    def get_setor_unidade(self, comeco=None):
        lista = []

        setor_list = Setor.objects.filter(Q(ativo=True, excluido=False)).values()
        for setor in setor_list:
            if setor["setor_pai_id"] == comeco:
                setor_json = {
                    "id": setor["id"],
                    "name": setor["nome"],
                    "type": "Setor",
                    "key": "SE{}".format(setor["id"]),
                    "children": self.get_setor_unidade(setor["id"]),
                }

                lista.append(setor_json)

        return lista

    def get_setor(self, children=None, setor_id=None):

        setor = (
            Setor.objects.filter(id=setor_id, excluido=False)
            .values("id", "nome", "setor_pai_id")
            .first()
        )
        setor_dict = {
            "id": setor["id"],
            "name": setor["nome"],
            "type": "Setor",
            "key": rf"SE{setor['id']}",
        }
        if children:
            setor_dict["children"] = [children]

        if setor.get("setor_pai_id"):
            setor_dict = self.get_setor(setor_dict, setor.get("setor_pai_id"))

        return setor_dict

    def check_setor(self, requisicao, id_setor=None):
        nome = check_duplicidade(requisicao.get("nome"))
        sigla = check_duplicidade(requisicao.get("sigla"))
        setor_pai = requisicao["setor_pai"] if requisicao.get("setor_pai") else None
        return Setor.objects.filter(
            Q(setor_pai_id=setor_pai, nome__iexact=nome, sigla__iexact=sigla)
            & ~Q(id=id_setor)
            & Q(excluido=False)
        )

    def check_vinculos(self, id):
        return Servidor.objects.filter(
            Q(lotacao=id, excluido=False) | Q(lotacao_temporaria=id, excluido=False)
        ).exists()
    
    def check_registro_inativo(self, id_setor):
        return Setor.objects.filter(Q(id=id_setor) & Q(ativo=False) & Q(excluido=False))

    def check_setor_pai_filho(self, id, requisicao):
        return id == requisicao.get("setor_pai")

    def check_setor_pai(self, id_setor):
        return Setor.objects.filter(
            Q(setor_pai=id_setor, ativo=True, excluido=False)
        ).exists()

    def check_setor_filho_destroy(self, pk):
        return Setor.objects.filter(setor_pai=pk, excluido=False).exists()

    def check_setor_filho(self, pk):
        return Setor.objects.filter(setor_pai=pk, ativo=True, excluido=False).exists()

    def check_registro_pai(self, id_setor, setor_pai):
        setor_dict = Setor.objects.filter(Q(id=id_setor)).values("setor_pai_id").first()
        return setor_dict.get("setor_pai_id") != UUID(setor_pai)

    def check_setor_exists(self, pk):
        return Setor.objects.filter(id=pk, excluido=False).exists()

    def perform_create(self, serializer):
        list_telefones = self.get_telefones(self.request.data)
        endereco = self.get_endereco(self.request.data)
        serializer.save(
            usuario_cadastro=user.get_user(self),
            telefones=list_telefones,
            enderecos=endereco,
        )

    def get_telefones(self, request):
        list_telefones = list()
        if request.get("telefones"):
            for telefone in request.get("telefones"):
                telefone_data = None
                telefone_data = (
                    Telefone.objects.filter(
                        Q(numero=telefone["numero"]) & Q(excluido=False)
                    )
                    .values("id")
                    .first()
                )
                if telefone_data:
                    telefone_data = telefone_data["id"]
                if not telefone_data:
                    telefone_data = Telefone.objects.create(
                        numero=telefone["numero"],
                        tipo=telefone["tipo"],
                        observacao=telefone["observacao"],
                        andar=telefone["andar"],
                        sala=telefone["sala"],
                        created_at=datetime.now(),
                        usuario_cadastro=user.get_user(self),
                    )
                list_telefones.append(telefone_data)
        return list_telefones

    def get_endereco(self, request):
        endereco = None
        if request.get("enderecos"):
            for requisicao in request.get("enderecos"):
                endereco = Endereco.objects.create(
                    cep=requisicao.get("cep"),
                    logradouro=requisicao.get("logradouro"),
                    numero=requisicao.get("numero"),
                    bairro=requisicao.get("bairro"),
                    cidade_id=requisicao.get("cidade"),
                    estado_id=requisicao.get("estado"),
                    complemento=requisicao.get("complemento"),
                    andar=requisicao.get("andar"),
                    sala=requisicao.get("sala"),
                    observacao=requisicao.get("observacao"),
                    usuario_cadastro=user.get_user(self),
                )
        return endereco

    def perform_update(self, serializer):
        list_telefones = self.get_telefones(self.request.data)
        endereco = self.get_endereco(self.request.data)
        serializer.save(
            usuario_edicao=user.get_user(self),
            updated_at=datetime.now(),
            telefones=list_telefones,
            enderecos=endereco,
        )


class ComportamentoInternoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = ComportamentoInternoSerializer
    pagination_class = Paginacao
    queryset = ComportamentoInterno.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome",)
    filter_fields = ("nome",)
    ordering_fields = ("nome", "ativo")
    ordering = ("nome", "ativo")

    def create(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if self.check_comportamento(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )

        except KeyError:
            return Response(
                {"non_field_errors": "Erro na requisição"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(ComportamentoInternoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            requisicao = request.data
            if not Base().check_registro_exists(ComportamentoInterno, requisicao.get("id")):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(ComportamentoInterno, requisicao.get("id")):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_comportamento(requisicao):
                return Response(
                    {"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT
                )
            if Base().check_registro_inativo(ComportamentoInterno, requisicao):
                return Response(
                    {"non_field_errors": mensagens.INATIVO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"non_field_errors": "Erro na requisição"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(ComportamentoInternoViewSet, self).update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super(ComportamentoInternoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        ativo = trata_campo_ativo(parametros_busca.get("ativo"))

        for query in ComportamentoInterno.objects.filter(Q(excluido=False)):
            nome = trata_campo(query.nome)
            if busca in nome:
                queryset |= ComportamentoInterno.objects.filter(pk=query.pk)

        if ativo is not None:
            queryset = queryset.filter(ativo=ativo)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(ComportamentoInterno, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(ComportamentoInterno, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ComportamentoInterno.objects.filter(id=pk).update(
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

    def check_comportamento(self, requisicao):
        nome = check_duplicidade(requisicao.get("nome"))
        return ComportamentoInterno.objects.filter(
            Q(nome__iexact=nome, excluido=False) & ~Q(id=requisicao.get("id"))
        ).exists()

    def perform_create(self, serializer):
        serializer.save(usuario_cadastro=user.get_user(self))

    def perform_update(self, serializer):
        serializer.save(usuario_edicao=user.get_user(self), updated_at=datetime.now())

