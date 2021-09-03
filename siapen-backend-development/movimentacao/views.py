from re import T
from django.db import transaction
from django.db import reset_queries
from juridico.models import NormasJuridicas, TituloLei
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
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
from movimentacao.serializers import (
    FasesPedidoSerializer,
    PedidoInclusaoSerializer,
    PedidoInclusaoOutroNomeSerializer,
    PedidoInclusaoMovimentacaoSerializer,
    AnalisePedidoSerializer,
)
from movimentacao.models import (
    AnalisePedido,
    PedidoInclusaoMotivos,
    FasesPedido,
    PedidoInclusao,
    PedidoInclusaoOutroNome,
    VulgosThroughModel,
    NormasJuridicasMotivosThroughModel,
    PedidoInclusaoMovimentacao,
)
from pessoas.interno.models import Interno, Vulgo
from pessoas.servidor.models import Servidor
from util.paginacao import Paginacao, paginacao_list, paginacao, ordena_lista
from util.busca import (
    trata_campo,
    trata_campo_ativo,
    trata_telefone,
    check_duplicidade,
    formata_data,
    formata_data_hora,
)
from util.image import get_thumbnail
from rest_framework import status, viewsets
from core.views import Base
from util import mensagens, validador, user
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import ast
from uuid import UUID


class FasesPedidoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = FasesPedidoSerializer
    pagination_class = Paginacao
    queryset = FasesPedido.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("nome", "grupo", "fase", "ativo")
    filter_fields = ("nome", "grupo", "fase", "ativo")
    ordering_fields = ("ordem", "grupo", "ativo")
    ordering = ("ordem", "grupo", "ativo")

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            if not self.check_item_primeira_fase(request.data):
                return Response(
                    {
                        "non_field_errors": "O primeiro item cadastrado deve está na Ordem 1 e como fase inicial e não deve ter as opções CGIN e ultima fase marcadas."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not self.check_item(request.data):
                return Response(
                    {
                        "non_field_errors": "O item Informado não é ultima fase ou não está localizado como ultimo item do grupo de fases."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(FasesPedidoViewSet, self).create(request, *args, **kwargs)

        if not self.check_fase_inicial(request.data):
            return Response(
                {
                    "non_field_errors": "A fase inicial deve ser o primeiro item do grupo."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self.check_ordem_ultimas_fase(request.data):
            return Response(
                {
                    "non_field_errors": "As fases sinalizadas como ultima fase devem esta localizadas no fim da lista."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self.qtd_fase_inicial_incorreta(request.data):
            return Response(
                {"non_field_errors": "O grupo de fases deve ter uma fase inicial."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self.check_duplicado(request.data):
            return Response({"detail": mensagens.MSG4}, status=status.HTTP_409_CONFLICT)

        if self.check_fase_cgin(request.data):
            return Response(
                {
                    "non_field_errors": "A fase marcada como CGIN deve ser única e não está marcada como ultima fase."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not self.check_ultima_fase_is_valid(request.data):
            return Response(
                {
                    "non_field_errors": "A fase marcada como ULTIMA FASE deve possuir a opção de FAVORÁVEL ou DESFAVORÁVEL."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializers = self.get_serializer(data=request.data, many=True)
        serializers.is_valid(raise_exception=True)
        self.perform_create(serializers)
        headers = self.get_success_headers(serializers.data)
        return Response(
            serializers.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, pk, *args, **kwargs):
        try:

            if Base().check_registro_excluido(FasesPedido, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(FasesPedidoViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(FasesPedido, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(FasesPedido, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if self.check_vinculos(pk):
                return Response(
                    {"non_field_errors": mensagens.MSG16},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            FasesPedido.objects.filter(id=pk).update(
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
        queryset = super(FasesPedidoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        grupo = trata_campo(parametros_busca.get("grupo"))
        movimentacao = trata_campo(parametros_busca.get("movimentacao"))
        if grupo:
            queryset = queryset.filter(grupo=grupo)

        if movimentacao and movimentacao.upper() == "INICIAL":
            queryset = queryset.filter(fase_inicial=False, excluido=False, ativo=True)
        elif movimentacao and movimentacao.upper() == "FINAL":
            queryset = queryset.filter(ultima_fase=True, excluido=False, ativo=True)

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    @action(detail=False, methods=["get"], url_path="grupos", url_name="grupos")
    def get_grupos(self, request):
        grupo_fase_list = [
            {
                "grupo": "EMERGENCIAL",
                "total_fases": FasesPedido.objects.filter(
                    grupo="EMERGENCIAL", excluido=False
                ).count(),
            },
            {
                "grupo": "DEFINITIVO",
                "total_fases": FasesPedido.objects.filter(
                    grupo="DEFINITIVO", excluido=False
                ).count(),
            },
        ]

        retorno = {
            "count": len(grupo_fase_list),
            "next": None,
            "previous": None,
            "results": grupo_fase_list,
        }

        return Response(retorno, status=status.HTTP_200_OK)

    def perform_create(self, serializer, **kwargs):
        kwargs["usuario_cadastro"] = user.get_user(self)
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["usuario_edicao"] = user.get_user(self)
        kwargs["updated_at"] = datetime.now()
        if requisicao.get("motivo_inativacao"):
            kwargs["data_inativacao"] = datetime.now()
            kwargs["usuario_inativacao"] = user.get_user(self)
        elif requisicao.get("motivo_ativacao"):
            kwargs["data_ativacao"] = datetime.now()
            kwargs["usuario_ativacao"] = user.get_user(self)
        serializer.save(**kwargs)

    def check_ultima_fase_is_valid(self, fases):
        for fase in fases:
            if fase.get("fase") == "ULTIMA_FASE" and not fase.get("ultima_fase"):
                return False
        return True

    def qtd_fase_inicial_incorreta(self, fases):
        try:
            fase_inicial = [
                i for i, _ in enumerate(fases) if _.get("fase_inicial") is True
            ]
            return len(fase_inicial) != 1
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def check_fase_inicial(self, fases):
        try:
            fase_inicial = [
                1 for i, _ in enumerate(fases) if _.get("fase_inicial") is True
            ]
            return fase_inicial and (fase_inicial[0] > 0)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def check_ordem_ultimas_fase(self, fases):
        try:
            ultima_fase = [
                i for i, _ in enumerate(fases) if _.get("fase") == "ULTIMA_FASE"
            ]
            fase_intermediaria = [
                i for i, _ in enumerate(fases) if _.get("fase") != "ULTIMA_FASE"
            ]
            return (ultima_fase and fase_intermediaria) and (
                fase_intermediaria[-1] > ultima_fase[0]
            )
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def check_fase_cgin(self, fases):
        try:
            ultima_fase = [
                i for i, _ in enumerate(fases) if _.get("fase") == "ULTIMA_FASE"
            ]
            cgin_ultima_fase = [
                i
                for i, _ in enumerate(fases)
                if _.get("ultima_fase") and _.get("fase") == "CGIN"
            ]
            cgin_fase = [i for i, _ in enumerate(fases) if _.get("fase") == "CGIN"]
            return cgin_fase and (
                len(cgin_fase) > 1
                or cgin_ultima_fase
                or (ultima_fase and cgin_fase[-1] > ultima_fase[0])
            )
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def check_duplicado(self, fases):
        try:
            nome_fases = [row["nome"].upper() for row in fases]
            fases_set = set(nome_fases)
            return len(nome_fases) != len(fases_set)
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def check_item(self, fases):
        try:
            queryset = (
                FasesPedido.objects.filter(
                    grupo=fases["grupo"], excluido=False, ativo=True
                )
                .order_by("ordem")
                .last()
            )
            if queryset:
                next_item = queryset.ordem + 1
                return next_item == fases["ordem"]
            return fases["ordem"] > 0
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def check_item_primeira_fase(self, fases):
        """Verifica se não possui nenhum item no grupo, e se é primeira fase."""
        try:
            queryset = FasesPedido.objects.filter(
                grupo=fases["grupo"], excluido=False, ativo=True
            ).count()
            return (
                queryset == 0
                and fases["ordem"] == 1
                and (
                    fases.get("primeira_fase")
                    and not fases.get("ultima_fase")
                    and not fases.get("fase")
                )
            )
        except Exception:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def check_vinculos(self, pk):
        return PedidoInclusao.objects.filter(
            Q(fase_pedido_id=pk, excluido=False)
        ).exists()


class PedidoInclusaoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = PedidoInclusaoSerializer
    pagination_class = Paginacao
    queryset = PedidoInclusao.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    ordering_fields = (
        "nome",
        "created_at",
        "estado_solicitante__nome",
        "tipo_inclusao",
        "fase_pedido__nome",
        "unidade__nome",
        "data_movimentacao",
        "tipo_escolta",
    )
    ordering = ("created_at", "nome", "estado_solicitante__nome")

    def create(self, request, *args, **kwargs):
        requisicao = request.data
        try:
            data_nascimento = (
                requisicao.get("data_nascimento")
                if requisicao.get("data_nascimento")
                else None
            )

            tipo_inclusao = (
                requisicao.get("tipo_inclusao")
                if requisicao.get("tipo_inclusao")
                else None
            )

            if self.check_interno_exists(requisicao):
                return Response(
                    {"cpf": mensagens.MSG32}, status=status.HTTP_400_BAD_REQUEST
                )

            if data_nascimento and not self.check_maioridade_penal(data_nascimento):
                return Response(
                    {"data_nascimento": mensagens.MSG30},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if tipo_inclusao:
                try:
                    FasesPedido.objects.get(grupo=tipo_inclusao, fase_inicial=True)
                except Exception:
                    return Response(
                        {"non_field_errors": mensagens.MSG34},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if not self.check_fase_exists(requisicao):
                return Response(
                    {"non_field_errors": mensagens.MSG34},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super(PedidoInclusaoViewSet, self).create(request, *args, **kwargs)
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
                    {"cpf": mensagens.MSG32}, status=status.HTTP_400_BAD_REQUEST
                )

            if data_nascimento and not self.check_maioridade_penal(data_nascimento):
                return Response(
                    {"data_nascimento": mensagens.MSG30},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not self.check_fase_exists(requisicao):
                return Response(
                    {"tipo_inclusao": mensagens.MSG34},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if requisicao.get(
                "motivo_exclusao"
            ) and not self.check_fase_iniciado_exists(requisicao.get("id")):
                pedido = PedidoInclusao.objects.get(id=requisicao.get("id"))
                return Response(
                    {
                        "non_field_errors": mensagens.MSG31.format(
                            pedido.fase_pedido.nome
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return super(PedidoInclusaoViewSet, self).update(request, *args, **kwargs)
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(PedidoInclusao, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(PedidoInclusao, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            PedidoInclusao.objects.filter(id=pk).update(
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
        queryset = super(PedidoInclusaoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        busca = trata_campo(parametros_busca.get("search"))
        exclude_id = (
            parametros_busca.get("exclude_ids").split(",")
            if parametros_busca.get("exclude_ids")
            else None
        )
        busca_sem_especial = trata_telefone(busca)

        queryset_pedido = PedidoInclusao.objects.none()
        for query in PedidoInclusao.objects.filter(Q(excluido=False)):
            qs = PedidoInclusao.objects.none()
            pedido_list = list()

            cpf = trata_telefone(query.cpf) if query.cpf else ""
            numero_sei = trata_telefone(query.numero_sei)

            pedido_list.append(trata_campo(query.nome))
            pedido_list.append(trata_campo(query.nome_social))
            pedido_list.append(formata_data(trata_campo(query.data_nascimento)))
            pedido_list.append(formata_data_hora(query.created_at))
            pedido_list.append(formata_data(trata_campo(query.data_pedido_sei)))
            pedido_list.append(trata_campo(query.nome_pai) if query.nome_pai else "")
            pedido_list.append(trata_campo(query.nome_mae) if query.nome_mae else "")
            pedido_list.append(
                formata_data_hora(query.data_movimentacao)
                if query.data_movimentacao
                else ""
            )
            pedido_list.append(
                trata_campo(query.fase_pedido.nome) if query.fase_pedido else ""
            )
            pedido_list.append(trata_campo(query.unidade.nome) if query.unidade else "")
            pedido_list.append(
                trata_campo(query.genero.descricao) if query.genero else ""
            )
            pedido_list.append(trata_campo(query.estado.nome) if query.estado else "")
            pedido_list.append(trata_campo(query.estado_solicitante.nome))
            pedido_list.append(
                trata_campo(query.regime_prisional.nome)
                if query.regime_prisional
                else ""
            )
            pedido_list.append(
                trata_campo(query.naturalidade.nome) if query.naturalidade else ""
            )
            pedido_list.append(trata_campo(query.get_tipo_inclusao_display()))
            pedido_list.append(trata_campo(query.get_tipo_escolta_display()))
            pedido_list.append(trata_campo(query.get_interesse_display()))

            pedido_list.extend(
                [
                    trata_campo(necessidade.nome)
                    for necessidade in query.necessidade_especial.all()
                ]
            )

            pedido_list.extend(
                [
                    trata_campo(nacionalidade.nome)
                    for nacionalidade in query.nacionalidade.all()
                ]
            )

            pedido_list.extend(
                [
                    trata_campo(vulgo)
                    for vulgo in VulgosThroughModel.objects.filter(
                        pedido_inclusao_id=query.id
                    )
                ]
            )

            pedido_list.extend(
                [
                    trata_campo(outros_nomes.nome)
                    for outros_nomes in PedidoInclusaoOutroNome.objects.filter(
                        pedido_inclusao_id=query.id, excluido=False
                    )
                ]
            )

            for analise in AnalisePedido.objects.filter(pedido_inclusao_id=query.id):
                pedido_list.append(trata_campo(analise.get_posicionamento_display()))
                pedido_list.append(trata_campo(analise.penitenciaria.nome))
                pedido_list.append(trata_campo(analise.parecer))
                pedido_list.append(trata_campo(analise.usuario_cadastro.username))

            for motivo in PedidoInclusaoMotivos.objects.filter(
                pedido_inclusao_id=query.id
            ):
                pedido_list.append(trata_campo(motivo.get_norma_juridica_display()))
                pedido_list.append(trata_campo(motivo.titulo.nome))

                pedido_list.extend(
                    [
                        (trata_campo(descricao_motivo.descricao))
                        for descricao_motivo in motivo.descricao.all()
                    ]
                )

            for pedido in pedido_list:
                if busca in pedido:
                    qs = PedidoInclusao.objects.filter(pk=query.pk)
                    break

            if not qs and (
                busca_sem_especial in numero_sei or busca_sem_especial in cpf
            ):
                qs = PedidoInclusao.objects.filter(pk=query.pk)

            if not queryset_pedido:
                queryset_pedido = qs
                queryset = queryset_pedido
            elif qs:
                queryset = queryset | qs

        if parametros_busca.get("fase") and parametros_busca["fase"] == "cgin":
            fases_list = FasesPedido.objects.filter(
                fase="CGIN", excluido=False
            ).values_list("id", flat=True)
            queryset = queryset.filter(fase_pedido__in=fases_list, excluido=False)
        elif parametros_busca.get("fase") and parametros_busca["fase"] == "escolta":
            fases_list = FasesPedido.objects.filter(
                fase="ULTIMA_FASE", ultima_fase="DEFERIDO", excluido=False
            ).values_list("id", flat=True)
            queryset = queryset.filter(
                fase_pedido__in=fases_list, aguardando_escolta=True, excluido=False
            )

        if exclude_id:
            queryset = queryset.filter(~Q(pk__in=exclude_id))

        if not self.request.query_params.get("ordering"):
            queryset = queryset.order_by("-created_at")
        else:
            queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset

    def check_interno_exists(self, requisicao):
        cpf = check_duplicidade(requisicao.get("cpf"))
        return Interno.objects.filter(
            Q(cpf__iexact=cpf, excluido=False, ativo=True)
        ).exists()

    def check_maioridade_penal(self, nascimento):

        maioridade_penal = True
        idade = validador.idade(nascimento)

        if idade and idade < 18 or idade == 0:
            maioridade_penal = False

        return maioridade_penal

    def check_fase_exists(self, requisicao):
        grupo = requisicao.get("tipo_inclusao")
        return FasesPedido.objects.filter(
            Q(grupo__exact=grupo, fase_inicial=True, excluido=False)
        ).exists()

    def check_fase_iniciado_exists(self, id):
        return PedidoInclusao.objects.filter(
            Q(pk=id, fase_pedido__fase_inicial=True)
        ).exists()

    def perform_create(self, serializer, **kwargs):
        kwargs["usuario_cadastro"] = user.get_user(self)
        kwargs["created_at"] = datetime.now()
        kwargs["fase_pedido_id"] = FasesPedido.objects.get(
            grupo=self.request.data["tipo_inclusao"], fase_inicial=True
        ).pk
        serializer.save(**kwargs)
        self.create_many_fields(serializer=serializer)

    def perform_update(self, serializer, **kwargs):
        requisicao = self.request.data
        kwargs["usuario_edicao"] = user.get_user(self)
        kwargs["updated_at"] = datetime.now()
        if requisicao.get("motivo_inativacao"):
            kwargs["data_inativacao"] = datetime.now()
            kwargs["usuario_inativacao"] = user.get_user(self)
        elif requisicao.get("motivo_ativacao"):
            kwargs["data_ativacao"] = datetime.now()
            kwargs["usuario_ativacao"] = user.get_user(self)
        serializer.save(**kwargs)
        pk = serializer.data.get("id")
        self.update_many_fields(pk=pk)

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

        try:

            motivos_inclusao = ast.literal_eval(requisicao.get("motivos_inclusao"))
        except Exception:
            motivos_inclusao = (
                self.request.data.get("motivos_inclusao")
                if self.request.data.get("motivos_inclusao")
                else None
            )

        if vulgo_nome:
            for nome_vulgo in vulgo_nome:
                if nome_vulgo.strip():
                    outro_nome = nome_vulgo.strip()
                    id_vulgo, created = Vulgo.objects.get_or_create(nome=nome_vulgo)
                    VulgosThroughModel.objects.get_or_create(
                        pedido_inclusao_id=serializer.data["id"], vulgo_id=id_vulgo.id
                    )

        if outros_nomes:
            for outro_nome in outros_nomes:
                if outro_nome.strip():
                    outro_nome = outro_nome.strip()
                    PedidoInclusaoOutroNome.objects.update_or_create(
                        nome=outro_nome,
                        usuario_cadastro=user.get_user(self),
                        pedido_inclusao_id=serializer.data["id"],
                        ativo=True,
                    )

        if motivos_inclusao:
            for motivo in motivos_inclusao:
                pedido_motivo, created = PedidoInclusaoMotivos.objects.get_or_create(
                    norma_juridica=motivo["norma_juridica"],
                    pedido_inclusao_id=serializer.data["id"],
                    titulo_id=motivo["titulo"],
                )
            [
                pedido_motivo.descricao.add(norma)
                for norma in NormasJuridicas.objects.filter(id__in=motivo["descricao"])
            ]
        fase = FasesPedido.objects.get(
            grupo=serializer.data["tipo_inclusao"], fase_inicial=True
        )
        PedidoInclusaoMovimentacao.objects.create(
            pedido_inclusao_id=serializer.data["id"],
            usuario_cadastro=user.get_user(self),
            fase_pedido=fase,
            motivo=fase.descricao,
            created_at=serializer.data["data_movimentacao"],
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

        try:
            motivos_inclusao = ast.literal_eval(requisicao.get("motivos_inclusao"))
        except Exception:
            motivos_inclusao = (
                self.request.data.get("motivos_inclusao")
                if self.request.data.get("motivos_inclusao")
                else None
            )

        if vulgo_nome:
            for nome_vulgo in vulgo_nome:
                if nome_vulgo.strip():
                    nome = nome_vulgo.strip()
                    id_vulgo, created = Vulgo.objects.get_or_create(nome=nome)
                    VulgosThroughModel.objects.get_or_create(
                        pedido_inclusao_id=pk, vulgo_id=id_vulgo.id
                    )
            novos_vulgos = Vulgo.objects.filter(nome__in=vulgo_nome).values_list(
                "id", flat=True
            )
            for vulgo in VulgosThroughModel.objects.filter(
                ~Q(vulgo_id__in=novos_vulgos) & Q(pedido_inclusao_id=pk)
            ):
                VulgosThroughModel.objects.filter(Q(pk=vulgo.pk)).delete()
        elif not vulgo_nome and VulgosThroughModel.objects.filter(
            Q(pedido_inclusao_id=pk)
        ):
            VulgosThroughModel.objects.filter(Q(pedido_inclusao_id=pk)).delete()

        if outros_nomes:
            for outro_nome in PedidoInclusaoOutroNome.objects.filter(
                ~Q(nome__in=outros_nomes) & Q(pedido_inclusao_id=pk)
            ):
                PedidoInclusaoOutroNome.objects.filter(Q(pk=outro_nome.pk)).delete()
            for outro_nome in outros_nomes:
                if outro_nome.strip():
                    outro_nome = outro_nome.strip()
                    PedidoInclusaoOutroNome.objects.update_or_create(
                        nome=outro_nome,
                        usuario_cadastro=user.get_user(self),
                        pedido_inclusao_id=UUID(pk),
                        ativo=True,
                    )
        elif not outros_nomes and PedidoInclusaoOutroNome.objects.filter(
            pedido_inclusao_id=pk
        ):
            PedidoInclusaoOutroNome.objects.filter(Q(pedido_inclusao_id=pk)).delete()

        if motivos_inclusao:
            motivos = [
                motivo.pk
                for motivo in PedidoInclusaoMotivos.objects.filter(
                    pedido_inclusao_id=UUID(pk)
                )
            ]
            motivos_list = list()
            for motivo in motivos_inclusao:
                pedido_motivo, created = PedidoInclusaoMotivos.objects.get_or_create(
                    norma_juridica=motivo["norma_juridica"],
                    pedido_inclusao_id=UUID(pk),
                    titulo_id=motivo["titulo"],
                )
                pedido_motivo.descricao.clear()
                [
                    pedido_motivo.descricao.add(norma)
                    for norma in NormasJuridicas.objects.filter(
                        id__in=motivo["descricao"]
                    )
                ]
                motivos_list.append(pedido_motivo.pk)
            itens_removidos = [item for item in motivos if item not in motivos_list]
            if itens_removidos:
                for pedido in PedidoInclusaoMotivos.objects.filter(
                    Q(id__in=itens_removidos)
                ):
                    NormasJuridicasMotivosThroughModel.objects.filter(
                        Q(motivo=pedido)
                    ).delete()
                    PedidoInclusaoMotivos.objects.filter(
                        Q(pk=pedido.pk, pedido_inclusao_id=pk)
                    ).delete()
        elif not motivos_inclusao and PedidoInclusaoMotivos.objects.filter(
            pedido_inclusao_id=pk
        ):
            for pedido in PedidoInclusaoMotivos.objects.filter(
                Q(pedido_inclusao_id=pk)
            ):
                NormasJuridicasMotivosThroughModel.objects.filter(
                    Q(motivo=pedido)
                ).delete()
            PedidoInclusaoMotivos.objects.filter(Q(pedido_inclusao_id=pk)).delete()

    @action(detail=False, methods=["get"], url_path="pessoas", url_name="pessoas")
    def get_pessoas(self, request):
        lista_pessoa = list()
        busca = dict()
        busca["cpf"] = (
            trata_telefone(self.request.query_params.get("cpf"))
            if self.request.query_params.get("cpf")
            else None
        )
        busca["nome"] = trata_campo(self.request.query_params.get("nome"))
        busca["nome_mae"] = trata_campo(self.request.query_params.get("nome_mae"))
        filter_all = True
        if busca["cpf"] or busca["nome"] or busca["nome_mae"]:
            filter_all = False

        lista_pessoa.extend(
            self.get_list_pessoas(
                queryset=Interno.objects.filter(excluido=False),
                tipo="INTERNO",
                busca=busca,
                filter_all=filter_all,
            )
        )

        lista_pessoa.extend(
            self.get_list_pessoas(
                queryset=Servidor.objects.filter(excluido=False),
                tipo="SERVIDOR",
                busca=busca,
                filter_all=filter_all,
            )
        )

        if lista_pessoa:
            lista = ordena_lista(
                lista_pessoa, self.request.query_params.get("ordering")
            )
            page_size = paginacao(self.request.query_params.get("page_size"))
            lista_paginada = paginacao_list(lista, page_size)

            page = 1
            if self.request.query_params.get("page"):
                page = (
                    len(lista_paginada)
                    if int(self.request.query_params.get("page")) > len(lista_paginada)
                    else int(self.request.query_params.get("page"))
                )

        retorno = {
            "count": len(lista_pessoa),
            "next": None,
            "previous": None,
            "results": lista_paginada[page - 1] if lista_pessoa else lista_pessoa,
        }

        return Response(retorno, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["get"], url_path="total-fases", url_name="total-fases"
    )
    def get_total_fases(self, request):
        retorno = {
            "pendente": PedidoInclusao.objects.filter(
                fase_pedido__fase_inicial=True, excluido=False
            ).count(),
            "em_analise": PedidoInclusao.objects.filter(
                fase_pedido__fase="CGIN", excluido=False
            ).count(),
            "remetido": PedidoInclusao.objects.filter(
                fase_pedido__fase="REMETIDO", excluido=False
            ).count(),
            "arquivado": PedidoInclusao.objects.filter(
                fase_pedido__fase="ARQUIVADO", excluido=False
            ).count(),
        }
        return Response(retorno, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="total-fases-mes",
        url_name="total-fases-mes",
    )
    def get_fase_pedido_ano(self, request):

        now = datetime.now()

        retorno = {
            "labels": self.get_mes_ano(now),
            "datasets": [
                {
                    "label": "Concluídos",
                    "data": self.get_total_pedido_por_fase_mes(
                        "ULTIMA_FASE", now.month
                    ),
                },
                {
                    "label": "Arquivados",
                    "data": self.get_total_pedido_por_fase_mes("ARQUIVAR", now.month),
                },
                {
                    "label": "Deferido pelo Juízo Corregedor",
                    "data": self.get_total_pedido_por_fases_finais_mes(
                        "ULTIMA_FASE", "DEFERIDO", now.month
                    ),
                },
                {
                    "label": "Indeferido pelo Juízo Corregedor",
                    "data": self.get_total_pedido_por_fases_finais_mes(
                        "ULTIMA_FASE", "INDEFERIDO", now.month
                    ),
                },
                {
                    "label": "Parecer Favorável da CGIN ",
                    "data": self.get_total_parecer_cgin_mes("FAVORAVEL", now.month),
                },
                {
                    "label": "Parecer Desfavorável da CGIN ",
                    "data": self.get_total_parecer_cgin_mes("DESFAVORAVEL", now.month),
                },
            ],
        }
        return Response(retorno, status=status.HTTP_200_OK)

    def get_mes_ano(self, data_atual):

        meses = [
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]

        if data_atual.month == 12:
            list_mes = [f"{mes} - {data_atual.year}" for mes in meses]
        else:
            list_atual = [
                f"{mes} - {data_atual.year}" for mes in meses[: data_atual.month]
            ]
            list_passado = [
                f"{mes} - {data_atual.year-1}" for mes in meses[data_atual.month :]
            ]
            list_mes = list_passado + list_atual
        return list_mes

    def get_total_pedido_por_fase_mes(self, fase, mes):
        data_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        data_fim = datetime.now()
        data_inicio = data_fim - relativedelta(years=1)
        pedidos_mes = (
            PedidoInclusao.objects.filter(
                fase_pedido__fase=fase,
                data_movimentacao__range=[data_inicio, data_fim],
                excluido=False,
            )
            .annotate(month=TruncMonth("data_movimentacao"))
            .values("data_movimentacao__month")
            .annotate(total=Count("id"))
        )

        for pedido in pedidos_mes:
            data_list[pedido["data_movimentacao__month"] - 1] = pedido["total"]

        if data_list and mes != 12:
            list_atual = data_list[:mes]
            list_passado = data_list[mes:]
            data_list = list_passado + list_atual

        return data_list

    def get_total_pedido_por_fases_finais_mes(self, fase, ultima_fase, mes):
        data_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        data_fim = datetime.now()
        data_inicio = data_fim - relativedelta(years=1)
        pedidos_mes = (
            PedidoInclusao.objects.filter(
                fase_pedido__fase=fase,
                fase_pedido__ultima_fase=ultima_fase,
                data_movimentacao__range=[data_inicio, data_fim],
                excluido=False,
            )
            .annotate(month=TruncMonth("data_movimentacao"))
            .values("data_movimentacao__month")
            .annotate(total=Count("id"))
        )

        for pedido in pedidos_mes:
            data_list[pedido["data_movimentacao__month"] - 1] = pedido["total"]

        if data_list and mes != 12:
            list_atual = data_list[:mes]
            list_passado = data_list[mes:]
            data_list = list_passado + list_atual

        return data_list

    def get_total_parecer_cgin_mes(self, parecer, mes):
        data_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        data_fim = datetime.now()
        data_inicio = data_fim - relativedelta(years=1)
        analises_mes = (
            AnalisePedido.objects.filter(
                posicionamento=parecer,
                created_at__range=[data_inicio, data_fim],
                excluido=False,
            )
            .annotate(month=TruncMonth("created_at"))
            .values("created_at__month")
            .annotate(total=Count("id"))
        )

        for analise in analises_mes:
            data_list[analise["created_at__month"] - 1] = analise["total"]

        if data_list and mes != 12:
            list_atual = data_list[:mes]
            list_passado = data_list[mes:]
            data_list = list_passado + list_atual

        return data_list

    @action(
        detail=False,
        methods=["get"],
        url_path="total-parecer-cgin",
        url_name="total-parecer-cgin",
    )
    def get_parecer_cgin(self, request):
        data_list = [0, 0]

        for pedido in PedidoInclusao.objects.all():
            qs = None
            qs = AnalisePedido.objects.filter(pedido_inclusao=pedido.pk, excluido=False)
            if not qs:
                continue
            qs = qs.latest("created_at")
            if qs.posicionamento == "FAVORAVEL":
                data_list[0] += 1
            else:
                data_list[1] += 1

        retorno = {
            "labels": ["Favorável", "Desfavorável"],
            "datasets": [{"data": data_list}],
        }
        return Response(retorno, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="total-unidades-cgin",
        url_name="total-unidades-cgin",
    )
    def get_unidades_parecer_cgin(self, request):
        labels_list = list()
        data_list = list()
        for unidade in (
            PedidoInclusao.objects.filter(excluido=False)
            .values("unidade__nome")
            .order_by("unidade")
            .annotate(count=Count("unidade"))
        ):
            if unidade.get("unidade__nome"):
                labels_list.append(unidade["unidade__nome"])
                data_list.append(unidade["count"])
        retorno = {"labels": labels_list, "datasets": [{"data": data_list}]}
        return Response(retorno, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="total-estado-solicitante",
        url_name="total-estado-solicitante",
    )
    def get_grupos(self, request):
        retorno = dict()
        for pedido in (
            PedidoInclusao.objects.filter(excluido=False)
            .values("estado_solicitante__sigla")
            .order_by("estado_solicitante")
            .annotate(count=Count("estado_solicitante"))
        ):
            if pedido.get("estado_solicitante__sigla"):
                retorno[pedido["estado_solicitante__sigla"]] = pedido["count"]
        return Response(retorno, status=status.HTTP_200_OK)

    def get_list_pessoas(self, queryset, tipo, busca, filter_all):

        lista_pessoa = list()
        for query in queryset:
            encontrado = True if filter_all else False
            if encontrado is False:
                pessoa_cpf = query.cpf
                pessoa_nome = trata_campo(query.nome)
                pessoa_nome_mae = trata_campo(query.nome_mae)
                if (
                    (busca["cpf"] and busca["cpf"] in pessoa_cpf)
                    or (busca["nome"] and busca["nome"] in pessoa_nome)
                    or (busca["nome_mae"] and busca["nome_mae"] in pessoa_nome_mae)
                ):
                    encontrado = True

            if encontrado is True:
                paises = ""
                if query.nacionalidade.all():
                    pais_list = [pais.nome for pais in query.nacionalidade.all()]
                    paises = ", ".join(pais_list)
                    estado = query.estado.sigla if query.estado else None
                    paises = paises.replace("Brasil", f"Brasil - {estado}")
                dict_pessoa = {
                    "tipo": tipo,
                    "id": query.pk,
                    "nome": query.nome,
                    "cpf": query.cpf,
                    "nome_mae": query.nome_mae,
                    "data_nascimento": query.data_nascimento
                    if query.data_nascimento
                    else "",
                    "naturalidade": paises,
                    "foto": get_thumbnail(query.foto_id),
                }
                lista_pessoa.append(dict_pessoa)

        return lista_pessoa

    def get_thumbnail(self, foto_id=None):
        thumbnail = None
        crypt = AESCipher()

        if foto_id:
            foto = Foto.objects.get(id=foto_id)
            if foto:
                thumbnail = crypt.decrypt(foto.thumbnail)
        return thumbnail


class PedidoInclusaoOutroNomeViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = PedidoInclusaoOutroNomeSerializer
    pagination_class = Paginacao
    queryset = PedidoInclusaoOutroNome.objects.filter(excluido=False)
    filter_backends = (SearchFilter,)
    search_fields = ("outro", "pessoa__nome", "data_cadastro")

    def create(self, request, *args, **kwargs):

        try:
            return super(PedidoInclusaoOutroNomeViewSet, self).create(
                request, *args, **kwargs
            )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def perform_create(self, serializer, **kwargs):
        kwargs["usuario_cadastro"] = user.get_user(self)
        kwargs["created_at"] = datetime.now()
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        kwargs["usuario_edicao"] = user.get_user(self)
        kwargs["updated_at"] = datetime.now()
        serializer.save(**kwargs)


class AnalisePedidoViewSet(LoggingMixin, viewsets.ModelViewSet, Base):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = AnalisePedidoSerializer
    pagination_class = Paginacao
    queryset = AnalisePedido.objects.filter(excluido=False)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = (
        "parecer",
        "penitenciaria",
        "posicionamento",
        "pedido_inclusao",
        "ativo",
    )
    filter_fields = (
        "parecer",
        "penitenciaria",
        "posicionamento",
        "pedido_inclusao",
        "ativo",
    )
    ordering_fields = (
        "created_at",
        "parecer",
        "penitenciaria",
        "posicionamento",
        "pedido_inclusao",
        "ativo",
    )
    ordering = (
        "created_at",
        "parecer",
        "penitenciaria",
        "posicionamento",
        "pedido_inclusao",
        "ativo",
    )

    def create(self, request, *args, **kwargs):

        with transaction.atomic():
            try:
                pedido = PedidoInclusao.objects.select_for_update().get(
                    pk=self.request.data.get("pedido_inclusao")
                )
            except Exception:
                return Response(
                    {"non_field_errors": mensagens.MSG_ERRO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            pedido.unidade_id = self.request.data.get("penitenciaria")
            pedido.save()
            return super(AnalisePedidoViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                if self.request.data.get("penitenciaria"):
                    pedido = PedidoInclusao.objects.select_for_update().get(
                        pk=self.request.data.get("pedido_inclusao")
                    )
                    pedido.unidade_id = self.request.data.get("penitenciaria")
                    pedido.posicionamento = self.request.data.get("posicionamento")
                    pedido.save()
                return super(AnalisePedidoViewSet, self).update(
                    request, *args, **kwargs
                )
        except KeyError:
            return Response(
                {"non_field_errors": mensagens.MSG_ERRO},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        try:
            if not Base().check_registro_exists(AnalisePedido, pk):
                return Response(
                    {"detail": mensagens.NAO_ENCONTRADO},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if Base().check_registro_excluido(AnalisePedido, pk):
                return Response(
                    {"non_field_errors": mensagens.NAO_PERMITIDO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            AnalisePedido.objects.filter(id=pk).update(
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

    def perform_create(self, serializer, **kwargs):
        kwargs["usuario_cadastro"] = user.get_user(self)
        kwargs["created_at"] = datetime.now()
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        kwargs["usuario_edicao"] = user.get_user(self)
        kwargs["updated_at"] = datetime.now()
        serializer.save(**kwargs)

    def filter_queryset(self, queryset):
        queryset = super(AnalisePedidoViewSet, self).filter_queryset(queryset)
        parametros_busca = self.request.query_params

        analise = trata_campo(parametros_busca.get("analise_id"))
        if analise:
            queryset = queryset.filter(~Q(id=analise))

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset


class PedidoInclusaoMovimentacaoViewSet(LoggingMixin, viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = PedidoInclusaoMovimentacaoSerializer
    pagination_class = Paginacao
    queryset = PedidoInclusaoMovimentacao.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("motivo", "pedido_inclusao")
    filter_fields = ("motivo", "pedido_inclusao")
    ordering_fields = ("created_at", "pedido_inclusao")
    ordering = ("created_at", "pedido_inclusao")

    def create(self, request, *args, **kwargs):

        if not request.data.get("fase_pedido"):
            return Response(
                {"non_field_errors": mensagens.MOVTO_PEDIDO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            data_movto = datetime.now()
            self.request.data["created_at"] = data_movto
            try:
                pedido = PedidoInclusao.objects.select_for_update().get(
                    pk=self.request.data.get("pedido_inclusao")
                )
                fase = FasesPedido.objects.get(pk=self.request.data.get("fase_pedido"))
            except Exception:
                return Response(
                    {"non_field_errors": mensagens.MSG_ERRO},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            pedido.data_movimentacao = data_movto
            pedido.fase_pedido_id = self.request.data.get("fase_pedido")

            if fase.fase == "ULTIMA_FASE":
                autos_recebidos, autos_remetidos = False, False
                analise = None

                try:
                    movimentacao_pedido = PedidoInclusaoMovimentacao.objects.filter(
                        pedido_inclusao_id=self.request.data.get("pedido_inclusao")
                    )
                    analise = AnalisePedido.objects.get(
                        pedido_inclusao_id=self.request.data.get("pedido_inclusao")
                    )
                except Exception:
                    return Response(
                        {"non_field_errors": mensagens.ERRO_FINALIZAR},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                for movimentacao in movimentacao_pedido:
                    if movimentacao.fase_pedido.fase == "RECEBIDO":
                        autos_recebidos = True
                    if movimentacao.fase_pedido.fase == "REMETIDO":
                        autos_remetidos = True
                if fase.ultima_fase == "DEFERIDO":
                    pedido.tipo_escolta = "INCLUSAO"
                    pedido.aguardando_escolta = True
                if analise and autos_recebidos and autos_remetidos:
                    pedido.fase_pedido_id = self.request.data.get("fase_pedido")
                else:
                    return Response(
                        {"non_field_errors": mensagens.ERRO_FINALIZAR},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            pedido.save()
            return super(PedidoInclusaoMovimentacaoViewSet, self).create(
                request, *args, **kwargs
            )

    def filter_queryset(self, queryset):
        queryset = super(PedidoInclusaoMovimentacaoViewSet, self).filter_queryset(
            queryset
        )

        queryset = OrderingFilter().filter_queryset(self.request, queryset, self)

        return queryset
