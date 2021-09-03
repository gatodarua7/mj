from django.db.models import Q
from django.forms.models import model_to_dict
from rest_framework import fields
from rest_framework.fields import SerializerMethodField
from rest_flex_fields import FlexFieldsModelSerializer
from pessoas.advogado.models import Advogado, EmailAdvogado, OAB, RgAdvogado
from localizacao.serializers import EstadoSerializer, PaisSerializer
from cadastros.models import Foto
from localizacao.models import Estado, Cidade
from rest_framework import serializers
from validate_docbr import CPF
from util import mensagens
from mj_crypt.mj_crypt import AESCipher


class OABSerializer(FlexFieldsModelSerializer):
    estado_nome = SerializerMethodField()

    class Meta:
        model = OAB
        ordering = ["id", "numero", "estado", "estado_nome"]
        fields = ["id", "numero", "estado", "estado_nome"]

        mandatory_fields = {
            "numero": mensagens.MSG2.format(u"numero"),
            "estado": mensagens.MSG2.format(u"estado"),
        }

    def get_advogado(self, obj):
        return obj.advogado

    def get_estado(self, obj):
        return obj.estado.id

    def get_estado_nome(self, obj):
        return obj.estado.nome


class RgAdvogadoSerializer(FlexFieldsModelSerializer):
    uf_rg = SerializerMethodField()
    uf_rg_nome = SerializerMethodField()
    orgao_expedidor_nome = SerializerMethodField()

    class Meta:
        model = RgAdvogado
        ordering = [
            "id",
            "numero",
            "orgao_expedidor",
            "uf_rg",
            "uf_rg_nome",
            "orgao_expedidor_nome",
        ]
        fields = [
            "id",
            "numero",
            "orgao_expedidor",
            "uf_rg",
            "uf_rg_nome",
            "orgao_expedidor_nome",
            "advogado",
        ]

    def get_uf_rg(self, obj):
        return obj.orgao_expedidor.estado.id

    def get_uf_rg_nome(self, obj):
        return obj.orgao_expedidor.estado.nome

    def get_orgao_expedidor_nome(self, obj):
        return obj.orgao_expedidor.nome


class EmailSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = EmailAdvogado
        ordering = ["id", "email"]
        fields = ["id", "email"]

    def get_advogado(self, obj):
        return obj.advogado


class AdvogadoSerializer(FlexFieldsModelSerializer):
    telefones = SerializerMethodField()
    enderecos = SerializerMethodField()
    rgs = SerializerMethodField()
    thumbnail = SerializerMethodField()
    oabs = SerializerMethodField()
    oabs_list = SerializerMethodField()
    emails = SerializerMethodField()

    class Meta:
        model = Advogado
        ordering = ["id", "nome"]
        exclude = ["usuario_cadastro", "usuario_edicao", "usuario_exclusao"]

    def __init__(self, *args, **kwargs):
        super(AdvogadoSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "cpf": mensagens.MSG2.format(u"cpf"),
            "data_nascimento": mensagens.MSG2.format(u"data nascimento"),
            "nome": mensagens.MSG2.format(u"nome"),
            "nacionalidade": mensagens.MSG2.format(u"nacionalidade"),
            "oabs": mensagens.MSG2.format(u"oabs"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def to_representation(self, instance):
        """
        Representa o valor de um objeto.
        """
        representacao = super(AdvogadoSerializer, self).to_representation(instance)
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

    def get_rgs(self, obj):
        lista_rg = list()
        for rg in RgAdvogado.objects.filter(advogado_id=obj.id, excluido=False):
            dados_rg = model_to_dict(RgAdvogado.objects.get(pk=rg.id))
            dados_rg["id"] = rg.id
            dados_rg["uf_rg"] = rg.orgao_expedidor.estado.id
            dados_rg["uf_rg_nome"] = rg.orgao_expedidor.estado.nome
            dados_rg["orgao_expedidor_nome"] = rg.orgao_expedidor.nome
            lista_rg.append(dados_rg)
        return lista_rg

    def get_oabs(self, obj):
        try:
            oabs = list()
            for oab in obj.oabs.values():
                if not oab.get("excluido"):
                    oabdict = oab
                    oabdict["numero"] = oab.get("numero")
                    oabdict["estado"] = oab.get("estado_id")
                    oabdict["estado_nome"] = Estado.objects.get(
                        Q(id=oab.get("estado_id"))
                    ).nome
                    oabs.append(oab)
            return oabs
        except Exception:
            pass

    def get_oabs_list(self, obj):
        try:
            oabs = list()
            for oab in obj.oabs.values():
                if not oab.get("excluido"):
                    oabdict = oab
                    estado = Estado.objects.get(Q(id=oab.get("estado_id"))).nome
                    oabdict["numero"] = oab.get("numero")
                    oab = oab.get("numero") + " - " + estado
                    oabs.append(oab)
            return oabs
        except Exception:
            pass

    def get_emails(self, obj):
        lista_email = list()
        for email in EmailAdvogado.objects.filter(advogado_id=obj.id, excluido=False):
            lista_email.append(email.email)
        return lista_email

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

        brasil_exist = None
        if data.get("nacionalidade"):
            brasil_exist = [
                pais.nome for pais in data["nacionalidade"] if "Brasil" in pais.nome
            ]

        if not brasil_exist and data.get("estado"):
            raise serializers.ValidationError(
                {"estado": "Os estados só estão disponíveis para o Brasil."}
            )

        if brasil_exist and not data.get("estado"):
            raise serializers.ValidationError({"estado": "Estado é obrigatório."})

        if brasil_exist and not data.get("naturalidade"):
            raise serializers.ValidationError(
                {"naturalidade": "Naturalidade é obrigatório."}
            )

        return data

    def get_thumbnail(self, obj):
        thumbnail = None
        crypt = AESCipher()

        if obj.foto_id:
            foto = Foto.objects.get(id=obj.foto_id)
            thumbnail = None
            if foto and foto.ativo:
                thumbnail = crypt.decrypt(foto.thumbnail)
        return thumbnail
