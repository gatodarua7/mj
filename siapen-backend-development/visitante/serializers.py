from re import T
from django.db.models import Q
from django.forms.models import model_to_dict
from rest_framework import fields
from rest_framework.fields import SerializerMethodField
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from visitante.models import (
    Visitante,
    EmailVisitante,
    RgVisitante,
    Anuencia,
    Manifestacao,
    DocumentosVisitante,
    VisitanteMovimentacao,
    VisitanteRecurso,
    ManifestacaoDiretoria,
)
from pessoas.interno.models import Interno, InternoVulgosThroughModel
from pessoas.interno.serializers import InternoSerializer
from vinculos.serializers import TipoVinculoSerializer
from localizacao.serializers import PaisSerializer
from cadastros.models import Foto, TipoDocumento
from localizacao.models import Estado, Cidade
from rest_framework import serializers
from validate_docbr import CPF
from util import mensagens, user
from util.documento import documento as decrypt_file
from mj_crypt.mj_crypt import AESCipher
import json
from datetime import datetime, date
from util.datas import get_proximo_dia_util, sum_years_date, cast_datetime_date


class RgVisitanteSerializer(FlexFieldsModelSerializer):
    uf_rg = SerializerMethodField()
    uf_rg_nome = SerializerMethodField()
    orgao_expedidor_nome = SerializerMethodField()

    class Meta:
        model = RgVisitante
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
            "visitante",
        ]

    def __init__(self, *args, **kwargs):
        super(RgVisitanteSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "numero": mensagens.MSG2.format("RG"),
            "orgao_expedidor": mensagens.MSG2.format("Órgão Expedidor"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_uf_rg(self, obj):
        return obj.orgao_expedidor.estado.id

    def get_uf_rg_nome(self, obj):
        return obj.orgao_expedidor.estado.nome

    def get_orgao_expedidor_nome(self, obj):
        return obj.orgao_expedidor.nome


class EmailVisitanteSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = EmailVisitante
        ordering = ["id", "email"]
        fields = ["id", "email"]

    def get_visitante(self, obj):
        return obj.visitante


class DocumentosVisitantePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentosVisitante
        ordering = ["id"]
        fields = ["id", "arquivo_temp"]

    def __init__(self, *args, **kwargs):
        super(DocumentosVisitantePostSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {"arquivo_temp": mensagens.MSG2.format("Arquivo")}

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value
            if key == "arquivo_temp" and not self.fields[key]:
                self.fields[key].error_messages["invalid"] = value


class DocumentosVisitanteSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = DocumentosVisitante
        ordering = ["id"]
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(DocumentosVisitanteSerializer, self).__init__(*args, **kwargs)


class VisitanteRecursoSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = VisitanteRecurso
        fields = "__all__"

        expandable_fields = {
            "documentos": (DocumentosVisitanteSerializer, {"many": True})
        }

    def __init__(self, *args, **kwargs):
        super(VisitanteRecursoSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {"data_recurso": mensagens.MSG2.format(u"data do recurso")}

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value


class ManifestacaoSerializer(FlexFieldsModelSerializer):
    usuario = SerializerMethodField()

    class Meta:
        model = Manifestacao
        fields = ["id", "parecer", "documentos", "visitante", "created_at", "usuario"]

        expandable_fields = {
            "documentos": (DocumentosVisitanteSerializer, {"many": True})
        }

    def __init__(self, *args, **kwargs):
        super(ManifestacaoSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "parecer": mensagens.MSG2.format(u"parecer"),
            "visitante": mensagens.MSG2.format(u"visitante"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_usuario(self, obj):
        return obj.usuario_cadastro.username


class VisitanteSerializer(FlexFieldsModelSerializer):
    telefones = SerializerMethodField()
    enderecos = SerializerMethodField()
    rgs = SerializerMethodField()
    thumbnail = SerializerMethodField()
    emails = SerializerMethodField()
    documentos = SerializerMethodField()
    analise_inteligencia = SerializerMethodField()
    analise_diretoria = SerializerMethodField()
    situacao = SerializerMethodField()
    permite_recurso = SerializerMethodField()
    usuario_permissao = SerializerMethodField()
    recurso_diretoria = SerializerMethodField()

    class Meta:
        model = Visitante
        ordering = ["id", "nome"]
        exclude = ["usuario_cadastro", "usuario_edicao", "usuario_exclusao"]

        expandable_fields = {"recurso": VisitanteRecursoSerializer}

    def __init__(self, *args, **kwargs):
        super(VisitanteSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "foto": mensagens.MSG2.format(u"foto"),
            "nome": mensagens.MSG2.format(u"nome"),
            "data_nascimento": mensagens.MSG2.format(u"data nascimento"),
            "numero_sei": mensagens.MSG2.format(u"Número SEI"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def to_representation(self, instance):
        """
        Representa o valor de um objeto.
        """
        representacao = super(VisitanteSerializer, self).to_representation(instance)
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
        for rg in RgVisitante.objects.filter(visitante_id=obj.id, excluido=False):
            dados_rg = model_to_dict(RgVisitante.objects.get(pk=rg.id))
            dados_rg["id"] = rg.id
            dados_rg["uf_rg"] = rg.orgao_expedidor.estado.id
            dados_rg["uf_rg_nome"] = rg.orgao_expedidor.estado.nome
            dados_rg["orgao_expedidor_nome"] = rg.orgao_expedidor.nome
            lista_rg.append(dados_rg)
        return lista_rg

    def get_emails(self, obj):
        lista_email = list()
        for email in EmailVisitante.objects.filter(visitante_id=obj.id, excluido=False):
            lista_email.append(email.email)
        return lista_email

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
                    documento["preview"] = decrypt_file(doc.get("id"))
                    documento.pop("arquivo")
                    documento.pop("arquivo_temp")
                    documentos.append(documento)
            return documentos
        except Exception:
            pass

    def get_analise_inteligencia(self, obj):
        return Manifestacao.objects.filter(visitante_id=obj.id, excluido=False).exists()

    def get_analise_diretoria(self, obj):

        try:
            manifestacao = ManifestacaoDiretoria.objects.filter(
                visitante_id=obj.id
            ).latest("created_at")
            if manifestacao:
                if obj.data_movimentacao < manifestacao.created_at:
                    return manifestacao.pk
                else:
                    return None
        except Exception:
            None

    def get_usuario_permissao(self, obj):
        try:
            manifestacao = ManifestacaoDiretoria.objects.filter(
                visitante_id=obj.id
            ).latest("created_at")
            if manifestacao:
                request = self.context.get("request")
                if (manifestacao.usuario_cadastro == request.user) or (
                    manifestacao.usuario_edicao == request.user
                ):
                    return True
                else:
                    return False
        except Exception:
            None

    def get_recurso_diretoria(self, obj):
        return ManifestacaoDiretoria.objects.filter(visitante_id=obj.id).exists()

    def validate(self, data):
        """
        Regras de validação de vinculo de localidade.
        """
        requisicao = self.context["request"].data

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
            raise serializers.ValidationError(
                {"estado": "O campo Estado é de preenchimento obrigatório."}
            )

        if brasil_exist and not data.get("naturalidade"):
            raise serializers.ValidationError(
                {"naturalidade": "O campo Naturalidade é de preenchimento obrigatório."}
            )

        if (data.get("idade") and self.check_maioridade(data)) and brasil_exist:
            if not data.get("estado"):
                raise serializers.ValidationError(
                    {"non_field_errors": mensagens.MSG2.format(u"rg")}
                )

            if not data.get("cpf"):
                raise serializers.ValidationError(
                    {"cpf": mensagens.MSG2.format(u"cpf")}
                )

            if not requisicao.get("rgs"):
                raise serializers.ValidationError(
                    {"non_field_errors": mensagens.MSG2.format(u"rg")}
                )

        return data

    def check_maioridade(self, data):
        idade = data.get("idade")
        if idade < 18:
            return False
        return True

    def get_thumbnail(self, obj):
        thumbnail = None
        crypt = AESCipher()

        if obj.foto_id:
            foto = Foto.objects.get(id=obj.foto_id)
            thumbnail = None
            if foto and foto.ativo:
                thumbnail = crypt.decrypt(foto.thumbnail)
        return thumbnail

    def get_situacao(self, obj):
        if obj.data_validade and datetime.today().date() > obj.data_validade:
            Visitante.objects.filter(id=obj.pk).update(situacao=False)
            return False
        return obj.situacao

    def get_permite_recurso(self, obj):
        if obj.fase == "INDEFERIDO" and obj.solicitante_informado:
            movimentacao = VisitanteMovimentacao.objects.get(
                visitante_id=obj.pk, fase="SOLICITANTE_INFORMADO"
            )
            if movimentacao:
                dia = 5 if movimentacao.data_contato.isoweekday() in [6, 7] else 4
                return datetime.today().date() <= get_proximo_dia_util(
                    data=movimentacao.data_contato, dia=dia
                )
        return False


class AnuenciaSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Anuencia
        ordering = ["id"]
        exclude = ["usuario_cadastro", "usuario_edicao", "usuario_exclusao"]

        expandable_fields = {
            "interno": InternoSerializer,
            "tipo_vinculo": TipoVinculoSerializer,
            "visitante": VisitanteSerializer,
            "documento": DocumentosVisitanteSerializer,
        }

    def __init__(self, *args, **kwargs):
        super(AnuenciaSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "data_declaracao": mensagens.MSG2.format(u"Data declaracao"),
            "tipo_vinculo": mensagens.MSG2.format(u"Tipo vinculo"),
            "documento": mensagens.MSG2.format(u"Declaração"),
            "interno": mensagens.MSG2.format(u"Interno"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value


class VisitanteMovimentacaoSerializer(FlexFieldsModelSerializer):
    usuario = SerializerMethodField()

    class Meta:
        model = VisitanteMovimentacao
        fields = "__all__"

    def get_usuario(self, obj):
        return obj.usuario_cadastro.username

    def validate(self, data):
        erro = dict()
        erro.update(self.check_data_comunicado(data))
        if erro:
            raise serializers.ValidationError(erro)
        return data

    def check_data_comunicado(self, data):
        erro = dict()
        if data.get("fase") == "SOLICITANTE_INFORMADO" and not data.get("data_contato"):
            erro = {"data_contato": mensagens.MSG2.format(u"data do contato")}
        return erro


class ManifestacaoDiretoriaSerializer(FlexFieldsModelSerializer):
    usuario = SerializerMethodField()

    class Meta:
        model = ManifestacaoDiretoria
        fields = ["id", "parecer", "documentos", "visitante", "created_at", "usuario"]

        expandable_fields = {
            "documentos": (DocumentosVisitanteSerializer, {"many": True})
        }

    def __init__(self, *args, **kwargs):
        super(ManifestacaoDiretoriaSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "parecer": mensagens.MSG2.format(u"parecer"),
            "visitante": mensagens.MSG2.format(u"visitante"),
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value

    def get_usuario(self, obj):
        return obj.usuario_cadastro.username
