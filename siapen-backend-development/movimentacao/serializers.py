import re
from core.models import BaseModel
from django.forms.models import model_to_dict
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField
from rest_flex_fields import FlexFieldsModelSerializer
from movimentacao.models import (
    AnalisePedido,
    PedidoInclusaoMotivos,
    FasesPedido,
    PedidoInclusao,
    PedidoInclusaoOutroNome,
    NormasJuridicasMotivosThroughModel,
    PedidoInclusaoMovimentacao,
)
from cadastros.models import Foto
from juridico.models import TituloLei
from localizacao.serializers import PaisSerializer
from rest_framework import serializers
from util import mensagens
from mj_crypt.mj_crypt import AESCipher
from pessoas.interno.serializers import VulgoSerializer
from validate_docbr import CPF
from uuid import UUID


class FasesPedidoListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        with transaction.atomic():
            itens = []
            for item in self.context["request"].data:
                if item.get("usuario_cadastro"):
                    item["usuario_cadastro"] = User.objects.get(
                        pk=item.get("usuario_cadastro")
                    )
                if item.get("usuario_edicao"):
                    item["usuario_edicao"] = User.objects.get(
                        pk=item.get("usuario_edicao")
                    )
                if item.get("usuario_ativacao"):
                    item["usuario_ativacao"] = User.objects.get(
                        pk=item.get("usuario_ativacao")
                    )
                if item.get("usuario_inativacao"):
                    item["usuario_inativacao"] = User.objects.get(
                        pk=item.get("usuario_inativacao")
                    )

                obj, created = FasesPedido.objects.update_or_create(
                    pk=item.get("id"), defaults=item
                )

                itens.append(obj)
            return itens


class FasesPedidoSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = FasesPedido
        fields = "__all__"
        list_serializer_class = FasesPedidoListSerializer

    def __init__(self, *args, **kwargs):
        super(FasesPedidoSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "nome": mensagens.MSG2.format(u"nome"),
            "grupo": mensagens.MSG2.format(u"grupo"),
            "ordem": mensagens.MSG2.format(u"ordem"),
            "descricao": mensagens.MSG2.format(u"descrição"),
            "cor": mensagens.MSG2.format(u"cor"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value


class PedidoInclusaoOutroNomeSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = PedidoInclusaoOutroNome
        ordering = ["id", "nome", "pedido_inclusao"]
        fields = ["id", "nome", "pedido_inclusao"]

    def get_pedido_inclusao(self, obj):
        return obj.pedido_inclusao


class PedidoInclusaoMotivosSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = PedidoInclusaoMotivos
        ordering = ["id", "norma_juridica", "pedido_inclusao", "titulo", "descricao"]
        fields = ["id", "norma_juridica", "pedido_inclusao", "titulo", "descricao"]

    def get_pedido_inclusao(self, obj):
        return obj.pedido_inclusao

    def to_representation(self, instance):
        data = super(PedidoInclusaoMotivosSerializer, self).to_representation(instance)
        titulo = TituloLei.objects.get(id=data["titulo"])
        normas_juridicas = NormasJuridicasMotivosThroughModel.objects.filter(
            motivo=data["id"]
        )
        ids_normas = list()
        nomes_normas = list()
        normas = ""
        for norma in normas_juridicas:
            ids_normas.append(norma.norma_id)
            nomes_normas.append(norma.norma.descricao)
            normas = norma.norma.get_norma_juridica_display()
        return {
            "norma_juridica": data["norma_juridica"],
            "norma_juridica_nome": normas,
            "titulo": data["titulo"],
            "titulo_nome": titulo.nome,
            "descricao": ids_normas,
            "descricao_nome": nomes_normas,
        }


class PedidoInclusaoSerializer(FlexFieldsModelSerializer):
    vulgo = VulgoSerializer(source="vulgo_set", many=True, read_only=True)
    outros_nomes = PedidoInclusaoOutroNomeSerializer(
        source="nome_set", many=True, read_only=True
    )
    motivos_inclusao = PedidoInclusaoMotivosSerializer(
        source="motivos_set", many=True, read_only=True
    )
    fase_pedido = SerializerMethodField()
    thumbnail = SerializerMethodField()
    imagem = SerializerMethodField()
    ultima_fase = SerializerMethodField()
    fase_cgin = SerializerMethodField()
    estado_solicitante_nome = SerializerMethodField()
    analise_cgin = SerializerMethodField()
    unidade_nome = SerializerMethodField()
    tipo_escolta = SerializerMethodField()

    class Meta:
        model = PedidoInclusao
        exclude = ("usuario_cadastro",)

    def __init__(self, *args, **kwargs):
        super(PedidoInclusaoSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "nome": mensagens.MSG2.format("Nome"),
            "genero": mensagens.MSG2.format("Gênero"),
            "nacionalidade": mensagens.MSG2.format("Nacionalidade"),
            "interesse": mensagens.MSG2.format("Interesse"),
            "numero_sei": mensagens.MSG2.format("Nº SEI"),
            "data_pedido_sei": mensagens.MSG2.format("Data Pedido SEI"),
            "motivos_inclusao": mensagens.MSG2.format("Motivos inclusão"),
            "tipo_inclusao": mensagens.MSG2.format("Tipo Inclusão"),
            "estado_solicitante": mensagens.MSG2.format("Estado Solicitante"),
            "data_nascimento": mensagens.MSG2.format("Data Nascimento"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_thumbnail(self, obj):
        thumbnail = None
        crypt = AESCipher()

        try:
            if obj.foto:
                queryset = Foto.objects.get(id=obj.foto.id)
                thumbnail = crypt.decrypt(queryset.thumbnail)
            return thumbnail
        except Exception:
            pass

    def get_imagem(self, obj):
        imagem = None
        crypt = AESCipher()

        try:
            if obj.foto and obj.foto.ativo:
                queryset = Foto.objects.get(id=obj.foto.id)
                imagem = crypt.decrypt(queryset.foto)
            return imagem
        except Exception:
            pass

    def get_fase_pedido(self, obj):
        fase = dict()
        if obj.fase_pedido:
            fase = model_to_dict(FasesPedido.objects.get(pk=obj.fase_pedido_id))
            fase["id"] = obj.fase_pedido_id
        return fase

    def get_ultima_fase(self, obj):
        if obj.fase_pedido:
            return obj.fase_pedido.ultima_fase

    def get_fase_cgin(self, obj):
        if obj.fase_pedido and obj.fase_pedido.fase == "CGIN":
            return True

    def get_estado_solicitante_nome(self, obj):
        return obj.estado_solicitante.nome

    def get_analise_cgin(self, obj):
        pedido = PedidoInclusao.objects.get(id=obj.id)
        try:
            analise_pedido = AnalisePedido.objects.filter(
                pedido_inclusao=obj.id
            ).latest("created_at")

            if analise_pedido:
                if pedido.data_movimentacao < analise_pedido.created_at:
                    return analise_pedido.pk
                else:
                    return None
        except Exception:
            None

    def get_unidade_nome(self, obj):
        if obj.unidade:
            return obj.unidade.nome

    def get_tipo_escolta(self, obj):
        return obj.get_tipo_escolta_display()

    def to_representation(self, instance):
        """
        Representa o valor de um objeto.
        """

        representacao = super(PedidoInclusaoSerializer, self).to_representation(
            instance
        )
        representacao["nacionalidade_nome"] = [
            PaisSerializer(pais).data["nome"] for pais in instance.nacionalidade.all()
        ]

        representacao["vulgo"] = [
            VulgoSerializer(v).data["nome"] for v in instance.vulgo.all()
        ]

        representacao["outros_nomes"] = [
            PedidoInclusaoOutroNomeSerializer(on).data["nome"]
            for on in PedidoInclusaoOutroNome.objects.filter(
                pedido_inclusao_id=instance.id, ativo=True
            )
        ]

        representacao["motivos_inclusao"] = [
            PedidoInclusaoMotivosSerializer(on).data
            for on in PedidoInclusaoMotivos.objects.filter(
                pedido_inclusao_id=instance.id
            )
        ]

        if representacao["vulgo"]:
            parametros = self.context["request"].query_params
            if (parametros and parametros.get("ordering")) and parametros.get(
                "ordering"
            ) == "-vulgo":
                representacao["vulgo"].sort(reverse=True)

        return representacao

    def validate(self, data):
        if data.get("cpf") and not CPF().validate(data.get("cpf")):
            raise serializers.ValidationError({"cpf": "CPF inválido."})
        return data


class PedidoInclusaoMovimentacaoSerializer(FlexFieldsModelSerializer):
    fase_nome = SerializerMethodField()
    fase_cor = SerializerMethodField()
    usuario = SerializerMethodField()

    class Meta:
        model = PedidoInclusaoMovimentacao
        fields = "__all__"

    def get_fase_nome(self, obj):
        return obj.fase_pedido.nome

    def get_fase_cor(self, obj):
        return obj.fase_pedido.cor

    def get_usuario(self, obj):
        return obj.usuario_cadastro.username


class AnalisePedidoSerializer(FlexFieldsModelSerializer):
    penitenciaria_nome = SerializerMethodField()
    usuario = SerializerMethodField()

    class Meta:
        model = AnalisePedido
        fields = [
            "id",
            "parecer",
            "penitenciaria",
            "posicionamento",
            "pedido_inclusao",
            "penitenciaria_nome",
            "created_at",
            "usuario",
        ]

    def __init__(self, *args, **kwargs):
        super(AnalisePedidoSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "parecer": mensagens.MSG2.format(u"parecer"),
            "penitenciaria": mensagens.MSG2.format(u"penitenciária"),
            "posicionamento": mensagens.MSG2.format(u"posicionamento"),
            "pedido_inclusao": mensagens.MSG2.format(u"pedido inclusao"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_penitenciaria_nome(self, obj):
        return obj.penitenciaria.nome

    def get_usuario(self, obj):
        return obj.usuario_cadastro.username
