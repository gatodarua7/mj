from django.db.models import Q
from django.forms.models import model_to_dict
from rest_framework import fields
from rest_framework.fields import SerializerMethodField
from rest_flex_fields import FlexFieldsModelSerializer
from cadastros.models import TipoDocumento, Foto
from comum.models import Endereco, Telefone
from pessoas.interno.models import (
    Interno,
    Vulgo,
    OutroNome,
    Contatos,
    Rg,
    SinaisParticulares,
)
from localizacao.serializers import PaisSerializer
from localizacao.models import Estado, Cidade
from rest_framework import serializers
from validate_docbr import CPF
from util import mensagens
from mj_crypt.mj_crypt import AESCipher


class RgSerializer(FlexFieldsModelSerializer):
    uf_rg = SerializerMethodField()
    uf_rg_nome = SerializerMethodField()
    orgao_expedidor_nome = SerializerMethodField()

    class Meta:
        model = Rg
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
            "interno"
        ]

    def get_uf_rg(self, obj):
        return obj.orgao_expedidor.estado.id

    def get_uf_rg_nome(self, obj):
        return obj.orgao_expedidor.estado.nome

    def get_orgao_expedidor_nome(self, obj):
        return obj.orgao_expedidor.nome


class VulgoSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Vulgo
        ordering = ["id", "nome"]
        fields = ["id", "nome"]

    def get_interno(self, obj):
        return obj.interno


class OutroNomeSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = OutroNome
        ordering = ["id", "nome", "interno"]
        fields = ["id", "nome", "interno"]

    def get_interno(self, obj):
        return obj.interno


class InternoSerializer(FlexFieldsModelSerializer):
    outros_nomes = OutroNomeSerializer(
        source="nome_set", many=True, read_only=True)
    vulgo = VulgoSerializer(source="vulgo_set", many=True, read_only=True)
    rgs = SerializerMethodField()
    thumbnail = SerializerMethodField()
    contatos = SerializerMethodField()
    documentos = SerializerMethodField()
    sinais = SerializerMethodField()

    class Meta:
        model = Interno
        ordering = ["nome", "vulgo"]
        exclude = ("usuario_cadastro",)

    def get_rgs(self, obj):
        lista_rg = list()
        for rg in Rg.objects.filter(interno_id=obj.id, excluido=False):
            dados_rg = model_to_dict(Rg.objects.get(pk=rg.id))
            dados_rg["id"] = rg.id
            dados_rg["uf_rg"] = rg.orgao_expedidor.estado.id
            dados_rg["uf_rg_nome"] = rg.orgao_expedidor.estado.nome
            dados_rg["orgao_expedidor_nome"] = rg.orgao_expedidor.nome
            lista_rg.append(dados_rg)
        return lista_rg

    def get_thumbnail(self, obj):
        thumbnail = None
        crypt = AESCipher()

        if obj.foto_id:
            foto = Foto.objects.get(id=obj.foto_id)
            thumbnail = None
            if foto and foto.ativo:
                thumbnail = crypt.decrypt(foto.thumbnail)
        return thumbnail

    def __init__(self, *args, **kwargs):
        super(InternoSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "cpf": mensagens.MSG2.format(u"CPF"),
            "data_nascimento": mensagens.MSG2.format(u"data de nascimento"),
            "nome": mensagens.MSG2.format(u"nome"),
            "caracteristicas_cutis": mensagens.MSG2.format("cútis"),
            "caracteristicas_cor_cabelo": mensagens.MSG2.format("cor de cabelo"),
            "caracteristicas_tipo_cabelo": mensagens.MSG2.format("tipo de cabelo"),
            "caracteristicas_tipo_rosto": mensagens.MSG2.format("tipo de rosto"),
            "caracteristicas_tipo_testa": mensagens.MSG2.format("tipo de testa"),
            "caracteristicas_tipo_olhos": mensagens.MSG2.format("tipo de olhos"),
            "caracteristicas_cor_olhos": mensagens.MSG2.format("cor de olhos"),
            "caracteristicas_nariz": mensagens.MSG2.format("nariz"),
            "caracteristicas_labios": mensagens.MSG2.format("labios"),
            "caracteristicas_compleicao": mensagens.MSG2.format("compleição"),
            "caracteristicas_sobrancelhas": mensagens.MSG2.format("sobrancelha"),
            "caracteristicas_orelhas": mensagens.MSG2.format("orelhas"),
            "mae_nao_declarado": mensagens.MSG2.format("Mãe não declarado"),
            "mae_falecido": mensagens.MSG2.format("Mãe falecido"),
            "pai_falecido": mensagens.MSG2.format("Pai falecido"),
            "pai_nao_declarado": mensagens.MSG2.format("Pai não declarado")
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def to_representation(self, instance):
        """
        Representa o valor de um objeto.
        """
        representacao = super(
            InternoSerializer, self).to_representation(instance)
        representacao["nacionalidade_nome"] = [
            PaisSerializer(pais).data["nome"] for pais in instance.nacionalidade.all()
        ]

        representacao["vulgo"] = [
            VulgoSerializer(v).data["nome"]
            for v in instance.vulgo.all()
        ]

        representacao["outros_nomes"] = [
            OutroNomeSerializer(on).data["nome"]
            for on in OutroNome.objects.filter(interno_id=instance.id, ativo=True)
        ]

        if representacao["vulgo"]:
            parametros = self.context['request'].query_params
            if (parametros and parametros.get('ordering')) and parametros.get('ordering') == '-vulgo':
                representacao["vulgo"].sort(reverse=True)

        return representacao

    def validate(self, data):
        """
        Regras de validação de vinculo de localidade.
        """
        if data.get("cpf") and not CPF().validate(data.get("cpf")):
            raise serializers.ValidationError({"cpf": "CPF inválido."})

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
        else:
            raise serializers.ValidationError({"nacionalidade":  mensagens.MSG2.format("nacionalidade")})

        if not brasil_exist and data.get("estado"):
            raise serializers.ValidationError(
                {"estado": "Os estados só estão disponíveis para o Brasil."}
            )

        return data

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
                    documento.pop("arquivo")
                    documento.pop("arquivo_temp")
                    documentos.append(documento)
            return documentos
        except Exception:
            pass

    def get_contatos(self, obj):
        try:
            contatos = list()
            for contato in Contatos.objects.filter(interno_id=obj.id, excluido=False):
                contato_dict = model_to_dict(
                    Contatos.objects.get(pk=contato.id))
                contato_dict["total_telefones"] = contato.telefones.count()
                contato_dict["total_enderecos"] = contato.enderecos.count()
                contato_dict["tipo_vinculo_nome"] = contato.tipo_vinculo.nome
                contato_dict["id"] = contato.id
                if contato_dict["enderecos"]:
                    endereco_list = []
                    for endereco in contato_dict["enderecos"]:
                        endereco_dict = dict()
                        endereco_dict = model_to_dict(
                            Endereco.objects.get(pk=endereco.id))
                        endereco_dict["id"] = endereco.id
                        endereco_dict['cidade_nome'] = endereco.cidade.nome
                        endereco_dict['estado_nome'] = endereco.estado.nome
                        endereco_list.append(endereco_dict)
                    contato_dict["enderecos"] = endereco_list
                if contato_dict["telefones"]:
                    telefone_list = []
                    for telefone in contato_dict["telefones"]:
                        telefone_dict = dict()
                        telefone_dict = model_to_dict(
                            Telefone.objects.get(pk=telefone.id))
                        telefone_dict["id"] = telefone.id
                        telefone_list.append(telefone_dict)
                    contato_dict["telefones"] = telefone_list
                contatos.append(contato_dict)
            return contatos
        except Exception:
            pass

    def get_sinais(self, obj):
        try:
            sinais = list()
            for sinal in SinaisParticulares.objects.filter(
                interno_id=obj.id, excluido=False
            ):
                sinal_dict = model_to_dict(
                    SinaisParticulares.objects.get(pk=sinal.id))
                sinal_dict["id"] = sinal.id
                sinais.append(sinal_dict)
            return sinais
        except Exception:
            pass


class ContatosSerializer(serializers.ModelSerializer):
    telefones = SerializerMethodField()
    enderecos = SerializerMethodField()
    tipo_vinculo_nome = SerializerMethodField()
    total_telefones = SerializerMethodField()
    total_enderecos = SerializerMethodField()

    class Meta:
        model = Contatos
        ordering = ["nome"]
        fields = [
            "id",
            "interno",
            "nome",
            "tipo_vinculo",
            "enderecos",
            "total_enderecos",
            "telefones",
            "ativo",
            "total_telefones",
            "tipo_vinculo_nome",
        ]

    def __init__(self, *args, **kwargs):
        super(ContatosSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "nome": mensagens.MSG2.format(u"nome"),
            "tipo_vinculo": mensagens.MSG2.format(u"vínculo")
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

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

    def get_telefones(self, obj):
        try:
            telefones = list()
            for telefone in obj.telefones.values():
                if not telefone.get("excluido"):
                    telefones.append(telefone)
            return telefones
        except Exception:
            pass

    def get_total_telefones(self, obj):
        return obj.telefones.count()

    def get_total_enderecos(self, obj):
        return obj.enderecos.count()

    def get_tipo_vinculo_nome(self, obj):
        return obj.tipo_vinculo.nome


class SinaisParticularesSerializer(serializers.ModelSerializer):
    thumbnail = SerializerMethodField()
    imagem = SerializerMethodField()

    class Meta:
        model = SinaisParticulares
        ordering = ["id"]
        exclude = ("usuario_cadastro",)

    def __init__(self, *args, **kwargs):
        super(SinaisParticularesSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "foto": mensagens.MSG2.format(u"foto"),
            "descricao": mensagens.MSG2.format(u"descrição"),
            "tipo": mensagens.MSG2.format(u"tipo")

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
            if obj.foto:
                queryset = Foto.objects.get(id=obj.foto.id)
                imagem = crypt.decrypt(queryset.foto)
            return imagem
        except Exception:
            pass
