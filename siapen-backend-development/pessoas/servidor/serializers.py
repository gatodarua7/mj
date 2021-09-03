from django.db.models import Q
from rest_framework import fields
from rest_framework.fields import SerializerMethodField
from rest_flex_fields import FlexFieldsModelSerializer
from pessoas.servidor.models import Servidor
from cadastros.serializers import DocumentosSerializer
from localizacao.serializers import PaisSerializer
from cadastros.models import TipoDocumento, Foto
from localizacao.models import Estado, Cidade
from rest_framework import serializers
from validate_docbr import CPF
from util import mensagens
from mj_crypt.mj_crypt import AESCipher


class ServidorSerializer(FlexFieldsModelSerializer):
    telefones = SerializerMethodField()
    telefones_funcionais = SerializerMethodField()
    documentos = SerializerMethodField()
    enderecos = SerializerMethodField()
    cargo_nome = SerializerMethodField()
    thumbnail = SerializerMethodField()
    documentos = DocumentosSerializer(many=True, read_only=True)

    class Meta:
        model = Servidor
        ordering = ["id", "nome"]
        exclude = [
            "usuario_cadastro",
            "usuario_edicao",
            "usuario_exclusao",
            "usuario_ativacao",
            "usuario_inativacao",
        ]

    def __init__(self, *args, **kwargs):
        super(ServidorSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "cpf": mensagens.MSG2.format(u"CPF"),
            "cargos": mensagens.MSG2.format(u"cargo"),
            "data_admissao": mensagens.MSG2.format(u"data de entrada em exercício"),
            "nome": mensagens.MSG2.format(u"nome"),
            "matricula": mensagens.MSG2.format(u"matrícula"),
            "email_profissional": mensagens.MSG2.format(u"e-mail funcional"),
            "lotacao": mensagens.MSG2.format(u"lotação principal"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def to_representation(self, instance):
        """
        Representa o valor de um objeto.
        """
        representacao = super(ServidorSerializer, self).to_representation(instance)
        representacao["nacionalidade_nome"] = [
            PaisSerializer(pais).data["nome"] for pais in instance.nacionalidade.all()
        ]

        return representacao

    def get_telefones(self, obj):
        try:
            telefones = list()
            for telefone in obj.telefones.values():
                if not telefone.get("excluido"):
                    telefones.append(telefone)
            return telefones
        except Exception:
            pass

    def get_telefones_funcionais(self, obj):
        try:
            telefonelist = list()
            for telefone in obj.telefones_funcionais.values():
                if not telefone.get("excluido"):
                    telefonelist.append(telefone)
            return telefonelist
        except Exception:
            pass

    def get_documentos(self, obj):
        try:
            documentos = list()
            for doc in obj.documentos.values():
                if not doc.get("excluido"):
                    documento = doc
                    documento["tipo"] = doc.get("tipo_id")
                    documento["tipo_nome"] = TipoDocumento.objects.get(
                        Q(id=doc.get("tipo_id"))
                    ).nome
                    documentos.append(documento)
            return documentos
        except Exception:
            pass

    def get_enderecos(self, obj):
        try:
            listenderecos = list()
            for endereco in obj.enderecos.values():
                if not endereco.get("excluido"):
                    enderecodict = endereco
                    enderecodict["estado"] = endereco.get("estado_id")
                    enderecodict["estado_nome"] = Estado.objects.get(
                        Q(id=endereco.get("estado_id"))
                    ).nome
                    enderecodict["cidade"] = endereco.get("cidade_id")
                    enderecodict["cidade_nome"] = Cidade.objects.get(
                        Q(id=endereco.get("cidade_id"))
                    ).nome
                    listenderecos.append(enderecodict)
            return listenderecos
        except Exception:
            pass

    def validate(self, data):
        """
        Regras de validação de vinculo de localidade.
        """
        if data.get("cpf") and not CPF().validate(data.get("cpf")):
            raise serializers.ValidationError({"cpf": "CPF inválido."})

        if data.get("rg") and not data.get("orgao_expedidor"):
            raise serializers.ValidationError(
                {
                    "orgao_expedidor": "Selecione um orgão expedidor, para o RG informado."
                }
            )

        if data.get("pai_nao_declarado") and data.get("pai_falecido"):
            raise serializers.ValidationError(
                {
                    "pai_falecido": "O pai nao pode ser declarado falecido e não declarado."
                }
            )

        if data.get("mae_nao_declarado") and data.get("mae_falecido"):
            raise serializers.ValidationError(
                {
                    "mae_falecido": "A mãe nao pode ser declarado falecido e nao declarado."
                }
            )

        brasil_exist = None
        if data.get("nacionalidade"):
            brasil_exist = [
                pais.nome for pais in data["nacionalidade"] if "Brasil" in pais.nome
            ]

        if not brasil_exist and data.get("estado"):
            raise serializers.ValidationError(
                {"estado": "Os estados só estão disponíveis para o Brasil."}
            )

        if data.get("data_desligamento") and (
            data.get("data_desligamento") < data.get("data_admissao")
        ):
            raise serializers.ValidationError(
                {
                    "data_desligamento": "Não é possível realizar o desligamento. Data de desligamento menor que a data de exercício"
                }
            )

        if data.get("data_desligamento") and not data.get("motivo_desligamento"):
            raise serializers.ValidationError(
                {"motivo_desligamento": "Informe o motivo do desligamento."}
            )

        if data.get("ativo") is False and not data.get("motivo_inativacao"):
            raise serializers.ValidationError(
                {"motivo_inativacao": "Informe o motivo de inativação do servidor(a)."}
            )

        return data

    def get_cargo_nome(self, obj):
        return obj.cargos.cargo

    def get_thumbnail(self, obj):
        thumbnail = None
        crypt = AESCipher()

        if obj.foto_id:
            foto = Foto.objects.get(id=obj.foto_id)
            thumbnail = None
            if foto and foto.ativo:
                thumbnail = crypt.decrypt(foto.thumbnail)
        return thumbnail
