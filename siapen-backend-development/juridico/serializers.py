from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_flex_fields import FlexFieldsModelSerializer
from util import mensagens
from juridico.models import (
    NormasJuridicas,
    TituloLei
)


class TituloLeiSerializer(FlexFieldsModelSerializer):
    norma_juridica_nome = SerializerMethodField()

    class Meta:
        model = TituloLei
        fields = ["id", "norma_juridica", "norma_juridica_nome", "nome", "motivo_inativacao",
                  "motivo_ativacao", "data_inativacao", "data_ativacao", "ativo"]

    def __init__(self, *args, **kwargs):
        super(TituloLeiSerializer, self).__init__(*args, **kwargs)
        mandatory_fields = {
            "norma_juridica": mensagens.MSG2.format("norma jurídica"),
            "nome": mensagens.MSG2.format("título da lei"),
        }
        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_norma_juridica_nome(self, obj):
        return obj.get_norma_juridica_display()


class NormasJuridicasSerializer(FlexFieldsModelSerializer):
    titulo_nome = SerializerMethodField()
    norma_juridica_nome = SerializerMethodField()

    class Meta:
        model = NormasJuridicas
        fields = ["id", "norma_juridica", "norma_juridica_nome", "titulo", "titulo_nome", "descricao", "motivo_inativacao",
                  "motivo_ativacao", "data_inativacao", "data_ativacao", "ativo"]

    def __init__(self, *args, **kwargs):
        super(NormasJuridicasSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "titulo": mensagens.MSG2.format("título"),
            "descricao": mensagens.MSG2.format("descrição"),
            "norma_juridica": mensagens.MSG2.format("norma jurídica"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_titulo_nome(self, obj):
        return obj.titulo.nome

    def get_norma_juridica_nome(self, obj):
        return obj.get_norma_juridica_display()
