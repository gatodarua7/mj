from rest_framework.fields import SerializerMethodField
from localizacao.models import Pais, Estado, Cidade
from rest_framework import serializers


class PaisSerializer(serializers.ModelSerializer):
    nome_pesquisa = SerializerMethodField()

    class Meta:
        model = Pais
        ordering = ["nome"]
        fields = ["nome", "id", "nome_pesquisa", "sigla"]

    def get_nome_pesquisa(self, obj):
        from unidecode import unidecode

        return unidecode(obj.nome)


class EstadoSerializer(serializers.ModelSerializer):

    nome_pesquisa = SerializerMethodField()

    class Meta:
        model = Estado
        ordering = ["sigla"]
        fields = ["pais", "id", "nome", "nome_pesquisa", "sigla"]

    def get_nome_pesquisa(self, obj):
        from unidecode import unidecode

        return unidecode(obj.nome)


class CidadeSerializer(serializers.ModelSerializer):
    nome_uf = SerializerMethodField()
    nome_pesquisa = SerializerMethodField()

    class Meta:
        model = Cidade
        ordering = ["nome", "estado"]
        fields = ["estado", "id", "nome", "nome_uf", "nome_pesquisa"]

    def get_nome_uf(self, obj):
        return obj.nome + " - " + obj.estado.sigla

    def get_nome_pesquisa(self, obj):
        from unidecode import unidecode

        return unidecode(obj.nome + " - " + obj.estado.sigla)
