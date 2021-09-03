from django.db.models import Q
from rest_framework.fields import SerializerMethodField
from pessoas.interno.models import OutroNome, Vulgo
from cadastros.models import (
    ComportamentoInterno,
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
    Setor
)
from localizacao.models import Estado, Cidade
from rest_framework import serializers
from util import mensagens, documento
from mj_crypt.mj_crypt import AESCipher
import os
import base64
from mimetypes import guess_type


class FotoSerializer(serializers.ModelSerializer):
    thumbnail = SerializerMethodField()
    foto = SerializerMethodField()
    cwd = os.getcwd()

    class Meta:
        model = Foto
        ordering = ["id"]
        fields = ["id", "foto_temp", "foto", "thumbnail", "ativo"]

    def __init__(self, *args, **kwargs):

        super(FotoSerializer, self).__init__(*args, **kwargs)

    def get_thumbnail(self, obj):
        crypt = AESCipher()
        thumbnail = crypt.decrypt(obj.thumbnail)

        return thumbnail

    def get_foto(self, obj):
        crypt = AESCipher()
        foto = crypt.decrypt(obj.foto)

        return foto


class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ["id", "descricao", "ativo"]

    def __init__(self, *args, **kwargs):
        super(GeneroSerializer, self).__init__(*args, **kwargs)

        self.fields["descricao"].error_messages["blank"] = mensagens.MSG2.format(
            "descrição"
        )


class FuncaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcao
        fields = ["id", "descricao", "ativo"]

    def __init__(self, *args, **kwargs):
        super(FuncaoSerializer, self).__init__(*args, **kwargs)

        self.fields["descricao"].error_messages["blank"] = mensagens.MSG2.format(
            "descrição"
        )


class PessoaSerializer(serializers.ModelSerializer):
    telefones = SerializerMethodField()
    enderecos = SerializerMethodField()
    foto = serializers.SlugRelatedField(
        queryset=Foto.objects.all(), slug_field="id", required=False, allow_null=True
    )

    class Meta:
        model = Pessoa
        ordering = ["nome", "cpf", "ativo"]
        fields = [
            "id",
            "nome",
            "nome_social",
            "data_nascimento",
            "cpf",
            "rg",
            "orgao_expedidor",
            "genero",
            "raca",
            "estado_civil",
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
            "ativo",
            "mae_falecido",
            "mae_nao_declarado",
            "pai_falecido",
            "pai_nao_declarado",
            "foto",
        ]

    def get_telefones(self, obj):
        try:
            telefonelist = list()
            for telefone in obj.telefones.values():
                if not telefone.get("excluido"):
                    telefonedict = dict()
                    telefonedict["id"] = telefone.get("id")
                    telefonedict["numero"] = telefone.get("numero")
                    telefonedict["tipo"] = telefone.get("tipo")
                    telefonedict["andar"] = telefone.get("andar")
                    telefonedict["sala"] = telefone.get("sala")
                    telefonedict["privado"] = telefone.get("privado")
                    telefonedict["usuario_cadastro"] = telefone.get(
                        "usuario_cadastro_id"
                    )
                    telefonedict["observacao"] = telefone.get("observacao")
                    telefonelist.append(telefonedict)
            return telefonelist
        except Exception:
            pass

    def get_enderecos(self, obj):
        try:
            listenderecos = list()
            for endereco in obj.enderecos.values():
                if not endereco.get("excluido"):
                    enderecodict = dict()
                    enderecodict["id"] = endereco.get("id")
                    enderecodict["logradouro"] = endereco.get("logradouro")
                    enderecodict["andar"] = endereco.get("andar")
                    enderecodict["sala"] = endereco.get("sala")
                    enderecodict["cep"] = endereco.get("cep")
                    enderecodict["numero"] = endereco.get("numero")
                    enderecodict["bairro"] = endereco.get("bairro")
                    enderecodict["estado"] = endereco.get("estado_id")
                    enderecodict["estado_nome"] = Estado.objects.get(
                        Q(id=endereco.get("estado_id"))
                    ).nome
                    enderecodict["cidade"] = endereco.get("cidade_id")
                    enderecodict["cidade_nome"] = Cidade.objects.get(
                        Q(id=endereco.get("cidade_id"))
                    ).nome
                    enderecodict["complemento"] = endereco.get("complemento")
                    enderecodict["observacao"] = endereco.get("observacao")
                    enderecodict["usuario_cadastro"] = endereco.get(
                        "usuario_cadastro_id"
                    )
                    listenderecos.append(enderecodict)
            return listenderecos
        except Exception:
            pass

    def validate(self, data):
        """
        Regras de validação de vinculo de localidade.
        """

        if data.get("pai_nao_declarado") and data.get("pai_falecido"):
            raise serializers.ValidationError(
                "O pai nao pode ser declarado falecido e nao declarado."
            )

        if data.get("mae_nao_declarado") and data.get("mae_falecido"):
            raise serializers.ValidationError(
                "A mãe nao pode ser declarado falecido e nao declarado."
            )

        if (data.get("nacionalidade") and data.get("nacionalidade").nome != "Brasil") and data.get("estado"):
                raise serializers.ValidationError(
                    "Os estados só estão disponíveis para o Brasil."
                )

        return data


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        ordering = ["nome"]
        fields = ["id", "nome", "ativo"]


class CargosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargos
        fields = ["id", "cargo", "ativo"]


class OrgaoExpedidorSerializer(serializers.ModelSerializer):
    estado_sigla = SerializerMethodField()

    class Meta:
        model = OrgaoExpedidor
        fields = [
            "id",
            "nome",
            "sigla",
            "estado",
            "estado_sigla",
            "ativo",
        ]

    def __init__(self, *args, **kwargs):
        super(OrgaoExpedidorSerializer, self).__init__(*args, **kwargs)
        mandatory_fields = {
            "sigla": mensagens.MSG2.format(u"sigla"),
            "nome": mensagens.MSG2.format(u"nome do órgão expedidor"),
            "estado": mensagens.MSG2.format(u"UF"),
        }
        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_estado_sigla(self, obj):
        return obj.estado.sigla


class RegimePrisionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegimePrisional
        fields = ["id", "nome", "ativo"]


class PericulosidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periculosidade
        fields = ["id", "nome", "sigla", "observacao", "ativo"]


class DocumentosPostSerializer(serializers.ModelSerializer):
    tipo_nome = SerializerMethodField()

    class Meta:
        model = Documentos
        ordering = ["id"]
        fields = [
            "id",
            "arquivo_temp",
            "tipo",
            "num_cod",
            "observacao",
            "tipo_nome",
            "data_validade",
        ]

    def __init__(self, *args, **kwargs):
        super(DocumentosPostSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "tipo": mensagens.MSG2.format("tipo"),
            "num_cod": mensagens.MSG2.format("Número/Código"),
            "arquivo_temp": mensagens.MSG2.format("Arquivo"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value
            self.fields[key].error_messages["invalid"] = value

    def get_tipo_nome(self, obj):
        return obj.tipo.nome


class DocumentosSerializer(serializers.ModelSerializer):
    tipo_nome = SerializerMethodField()
    preview = SerializerMethodField()

    class Meta:
        model = Documentos
        ordering = ["id"]
        fields = [
            "id",
            "tipo",
            "num_cod",
            "observacao",
            "tipo_nome",
            "preview",
            "data_validade",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super(DocumentosSerializer, self).__init__(*args, **kwargs)

    def get_tipo_nome(self, obj):
        return obj.tipo.nome

    def get_preview(self, obj):
        return documento.documento(obj.pk)


class SetorSerializer(serializers.ModelSerializer):
    setor_pai_nome = SerializerMethodField()
    telefones = SerializerMethodField()
    enderecos = SerializerMethodField()
    cep_logradouro = SerializerMethodField()

    class Meta:
        model = Setor
        fields = [
            "id",
            "setor_pai",
            "setor_pai_nome",
            "nome",
            "sigla",
            "enderecos",
            "telefones",
            "ativo",
            "cep_logradouro",
        ]

    def __init__(self, *args, **kwargs):
        super(SetorSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "nome": mensagens.MSG2.format("Nome"),
            "sigla": mensagens.MSG2.format("Sigla"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_setor_pai_nome(self, obj):
        try:
            return obj.setor_pai.nome
        except Exception:
            pass

    def get_cep_logradouro(self, obj):
        try:
            endereco = f"{obj.enderecos.cep} {obj.enderecos.logradouro}"
            return endereco[:20]
        except Exception:
            pass

    def get_telefones(self, obj):
        try:
            telefonelist = list()
            for telefone in obj.telefones.values():
                if not telefone.get("excluido"):
                    telefonedict = dict()
                    telefonedict["id"] = telefone.get("id")
                    telefonedict["numero"] = telefone.get("numero")
                    telefonedict["tipo"] = telefone.get("tipo")
                    telefonedict["andar"] = telefone.get("andar")
                    telefonedict["sala"] = telefone.get("sala")
                    telefonedict["usuario_cadastro"] = telefone.get(
                        "usuario_cadastro_id"
                    )
                    telefonedict["observacao"] = telefone.get("observacao")
                    telefonelist.append(telefonedict)
            return telefonelist
        except Exception:
            pass

    def get_enderecos(self, obj):
        try:
            listenderecos = list()
            if obj.enderecos and not obj.enderecos.excluido:
                enderecodict = dict()
                enderecodict["id"] = obj.enderecos.id
                enderecodict["logradouro"] = obj.enderecos.logradouro
                enderecodict["andar"] = obj.enderecos.andar
                enderecodict["sala"] = obj.enderecos.sala
                enderecodict["cep"] = obj.enderecos.cep
                enderecodict["numero"] = obj.enderecos.numero
                enderecodict["bairro"] = obj.enderecos.bairro
                enderecodict["estado"] = obj.enderecos.estado.id
                enderecodict["cidade"] = obj.enderecos.cidade.id
                enderecodict["complemento"] = obj.enderecos.complemento
                enderecodict["observacao"] = obj.enderecos.observacao
                enderecodict["usuario_cadastro"] = obj.enderecos.usuario_cadastro.id
                listenderecos.append(enderecodict)
            return listenderecos
        except Exception:
            pass


class ComportamentoInternoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComportamentoInterno
        fields = ["id", "nome", "ativo"]

    def __init__(self, *args, **kwargs):
        super(ComportamentoInternoSerializer, self).__init__(*args, **kwargs)

        self.fields["nome"].error_messages["blank"] = mensagens.MSG2.format("nome")
