from localizacao.serializers import PaisSerializer, EstadoSerializer
from rest_framework.fields import SerializerMethodField
from rest_framework import serializers
from orcrim.models import FaccaoGrupo, FaccaoPessoa, Faccao, FaccaoCargo
from util import mensagens


class FaccaoPessoaSerializer(serializers.ModelSerializer):
    faccao_nome = SerializerMethodField()
    pessoa_nome = SerializerMethodField()

    class Meta:
        model = FaccaoPessoa
        fields = [
            "id",
            "faccao",
            "faccao_nome",
            "pessoa",
            "pessoa_nome",
            "data_filiacao_faccao",
            "data_desfiliacao_faccao",
            "ativo",
            "observacao",
        ]

    def get_faccao_nome(self, obj):
        try:
            return obj.faccao.nome
        except Exception:
            pass

    def get_pessoa_nome(self, obj):

        try:
            return obj.pessoa.nome
        except Exception:
            pass


class FaccaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faccao
        fields = ["id", "nome", "sigla", "pais", "estado", "ativo", "observacao"]


    def __init__(self, *args, **kwargs):
        super(FaccaoSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "sigla": mensagens.MSG2.format(u"sigla"),
            "nome": mensagens.MSG2.format(u"nome")
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value


    def to_representation(self, instance):
        """
        Representa o valor de um objeto.
        """
        representacao = super(FaccaoSerializer, self).to_representation(instance)
        representacao["pais_nome"] = [
            PaisSerializer(pais).data["nome"] for pais in instance.pais.all()
        ]
        representacao["estado_nome"] = [
            EstadoSerializer(estado).data["nome"] for estado in instance.estado.all()
        ]
        return representacao

    def validate(self, data):
        """
        Regras de validação de orcrim.
        """

        brasil_exist = [pais for pais in data["pais"] if "Brasil" in pais.nome]

        if not brasil_exist and data["estado"]:
            raise serializers.ValidationError(
                "Os estados só estão disponíveis para o Brasil."
            )

        return data


class FaccaoGrupoSerializer(serializers.ModelSerializer):
    faccao_nome = SerializerMethodField()

    class Meta:
        model = FaccaoGrupo
        fields = ["id", "faccao", "faccao_nome", "nome", "observacao", "ativo"]


    def __init__(self, *args, **kwargs):
        super(FaccaoGrupoSerializer, self).__init__(*args, **kwargs)
        mandatory_fields = {
            "faccao": mensagens.MSG2.format(u"facção"),
            "nome": mensagens.MSG2.format(u"grupo")
        }
        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_faccao_nome(self, obj):
        try:
            return f"{obj.faccao.nome} - {obj.faccao.sigla}"
        except Exception:
            pass

class FaccaoCargoSerializer(serializers.ModelSerializer):
    faccao_nome = SerializerMethodField()

    class Meta:
        model = FaccaoCargo
        fields = ["id", "faccao", "faccao_nome", "nome", "observacao", "ativo"]

    def __init__(self, *args, **kwargs):
        super(FaccaoCargoSerializer, self).__init__(*args, **kwargs)
        mandatory_fields = {
            "faccao": mensagens.MSG2.format(u"facção"),
            "nome": mensagens.MSG2.format(u"nome")
        }
        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_faccao_nome(self, obj):
        try:
            return f"{obj.faccao.nome} - {obj.faccao.sigla}"
        except Exception:
            pass
