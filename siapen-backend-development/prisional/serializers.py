from typing import BinaryIO
from django.db.models.fields import CommaSeparatedIntegerField
from rest_framework.fields import SerializerMethodField
from prisional.models import (
    Bloco,
    Cela,
    DefeitoCela,
    Defeito,
    DesignacaoFuncaoServidor,
    ReparoCela,
    SistemaPenal,
    Unidade,
    UsuarioSistema,
)
from rest_framework import serializers
from util import mensagens


class BlocoSerializer(serializers.ModelSerializer):
    unidade_nome = SerializerMethodField()
    bloco_pai_nome = SerializerMethodField()
    sistema_nome = SerializerMethodField()

    class Meta:
        model = Bloco
        ordering = ["nome"]
        fields = [
            "id",
            "sistema_nome",
            "unidade_nome",
            "bloco_pai",
            "nome",
            "bloco_pai_nome",
            "ativo",
            "unidade",
            "sistema",
        ]

    def get_unidade_nome(self, obj):
        try:
            return obj.unidade.nome
        except Exception:
            pass

    def get_bloco_pai_nome(self, obj):
        try:
            return obj.bloco_pai.nome
        except Exception:
            pass

    def get_sistema_nome(self, obj):
        try:
            return obj.unidade.sistema.nome
        except Exception:
            pass


class CelaSerializer(serializers.ModelSerializer):
    bloco_nome = SerializerMethodField()
    unidade_nome = SerializerMethodField()
    sistema_nome = SerializerMethodField()

    class Meta:
        model = Cela
        ordering = ["nome", "ativo"]
        fields = [
            "id",
            "bloco",
            "nome",
            "capacidade",
            "ativo",
            "excluido",
            "observacao",
            "bloco_nome",
            "unidade_nome",
            "sistema_nome",
            "unidade",
            "sistema",
        ]

    def __init__(self, *args, **kwargs):
        super(CelaSerializer, self).__init__(*args, **kwargs)

        self.fields["bloco"].error_messages["blank"] = mensagens.MSG2.format(u"bloco")
        self.fields["nome"].error_messages["blank"] = mensagens.MSG2.format(u"nome")
        self.fields["capacidade"].error_messages["blank"] = mensagens.MSG2.format(
            u"capacidade"
        )

    def get_bloco_nome(self, obj):
        try:
            return obj.bloco.nome
        except Exception:
            pass

    def get_unidade_nome(self, obj):
        try:
            return obj.unidade.nome
        except Exception:
            pass

    def get_sistema_nome(self, obj):
        try:
            return obj.sistema.nome
        except Exception:
            pass


class DefeitoCelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefeitoCela
        fields = "__all__"


class DefeitoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defeito
        ordering = ["descricao", "ativo"]
        fields = ["id", "descricao", "ativo", "excluido"]

    def __init__(self, *args, **kwargs):
        super(DefeitoSerializer, self).__init__(*args, **kwargs)

        self.fields["descricao"].error_messages["blank"] = mensagens.MSG2.format(
            u"descrição"
        )
        self.fields["descricao"].error_messages["unique"] = mensagens.MSG4.format(
            u"descrição"
        )


class DesignacaoFuncaoServidorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignacaoFuncaoServidor
        fields = "__all__"


class ReparoCelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReparoCela
        fields = "__all__"


class SistemaPenalSerializer(serializers.ModelSerializer):
    pais_nome = SerializerMethodField()
    estado_nome = SerializerMethodField()

    class Meta:
        model = SistemaPenal
        ordering = ["nome", "sigla"]
        fields = [
            "id",
            "nome",
            "sigla",
            "ativo",
            "excluido",
            "pais",
            "estado",
            "pais_nome",
            "estado_nome",
        ]

    def __init__(self, *args, **kwargs):
        super(SistemaPenalSerializer, self).__init__(*args, **kwargs)

        # Mensagens de validação customizadas
        self.fields["nome"].error_messages["blank"] = mensagens.MSG2.format(u"nome")
        self.fields["sigla"].error_messages["blank"] = mensagens.MSG2.format(u"sigla")

    def validate(self, data):
        """
        Regras de validação de prisional.
        """

        if (
            data.get("pais")
            and data.get("pais").nome != "Brasil"
            and data.get("estado")
        ):
            raise serializers.ValidationError(
                "Os estados só estão disponíveis para o Brasil."
            )

        return data

    def get_pais_nome(self, obj):
        try:
            return obj.pais.nome
        except Exception:
            pass

    def get_estado_nome(self, obj):
        try:
            return obj.estado.nome
        except Exception:
            pass


class UnidadeSerializer(serializers.ModelSerializer):
    cidade_nome = SerializerMethodField()
    estado_nome = SerializerMethodField()
    sistema_nome = SerializerMethodField()
    total_celas = serializers.SerializerMethodField()

    class Meta:
        model = Unidade
        ordering = ["nome", "sigla"]
        fields = [
            "id",
            "nome",
            "sigla",
            "ativo",
            "excluido",
            "sistema",
            "sistema_nome",
            "estado",
            "cidade",
            "estado_nome",
            "cidade_nome",
            "total_celas",
        ]

    def __init__(self, *args, **kwargs):
        super(UnidadeSerializer, self).__init__(*args, **kwargs)

        # Mensagens de validação customizadas
        self.fields["nome"].error_messages["blank"] = mensagens.MSG2.format(u"nome")
        self.fields["sigla"].error_messages["blank"] = mensagens.MSG2.format(u"sigla")
        self.fields["sistema_nome"].error_messages["null"] = mensagens.MSG2.format(
            u"sistema"
        )

    def get_sistema_nome(self, obj):
        try:
            return obj.sistema.nome
        except Exception:
            pass

    def get_cidade_nome(self, obj):
        return obj.cidade.nome

    def get_status(self, obj):
        return str(obj.ativo).lower()

    def get_estado_nome(self, obj):
        return obj.estado.nome

    # Retorna o total de celas na unidade
    def get_total_celas(self, obj):
        return Cela.objects.filter(bloco__unidade=obj.id).count()


class UsuarioSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioSistema
        fields = "__all__"
