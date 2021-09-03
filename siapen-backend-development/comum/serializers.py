from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from comum.models import Endereco, Telefone
from util import mensagens


class EnderecoSerializer(serializers.ModelSerializer):
    estado_nome = SerializerMethodField()
    cidade_nome = SerializerMethodField()

    class Meta:
        model = Endereco
        ordering = ["id"]
        fields = [
            "id",
            "logradouro",
            "bairro",
            "numero",
            "complemento",
            "cep",
            "estado",
            "cidade",
            "andar",
            "sala",
            "observacao",
            "ativo",
            "estado_nome",
            "cidade_nome",
        ]

    def __init__(self, *args, **kwargs):
        super(EnderecoSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "cep": mensagens.MSG2.format(u"cep"),
            "logradouro": mensagens.MSG2.format(u"logradouro"),
            "bairro": mensagens.MSG2.format(u"bairro"),
            "estado": mensagens.MSG2.format(u"estado"),
            "cidade": mensagens.MSG2.format(u"cidade"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_estado_nome(self, obj):
        return obj.estado.nome

    def get_cidade_nome(self, obj):
        return obj.cidade.nome


class TelefoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefone
        ordering = ["id"]
        fields = ["id", "numero", "tipo", "observacao", "andar", "sala", "privado"]

    def __init__(self, *args, **kwargs):
        super(TelefoneSerializer, self).__init__(*args, **kwargs)

        self.fields["numero"].error_messages["blank"] = mensagens.MSG2.format(u"numero")
        self.fields["tipo"].error_messages["blank"] = mensagens.MSG2.format(u"tipo")

    def validate(self, data):
        """
        Regras de validação de telefones.
        """

        if (data.get("tipo") and data.get("tipo") != "RAMAL") and (
            data.get("andar") or data.get("sala")
        ):
            raise serializers.ValidationError(
                "Andar e sala só podem ser atribuídos a um RAMAL."
            )

        return data
