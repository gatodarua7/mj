from rest_framework import serializers
from social.models import EstadoCivil, GrauDeInstrucao, NecessidadeEspecial, OrientacaoSexual, Profissao, Raca, Religiao
from util import mensagens


class EstadoCivilSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCivil
        fields = ['id', 'nome', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super(EstadoCivilSerializer, self).__init__(*args, **kwargs)

        self.fields['nome'].error_messages['blank'] = mensagens.MSG2.format(u'nome')


class GrauDeInstrucaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrauDeInstrucao
        fields = ['id', 'nome', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super(GrauDeInstrucaoSerializer, self).__init__(*args, **kwargs)

        self.fields['nome'].error_messages['blank'] = mensagens.MSG2.format(u'nome')


class NecessidadeEspecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = NecessidadeEspecial
        fields = ['id', 'nome', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super(NecessidadeEspecialSerializer, self).__init__(*args, **kwargs)

        self.fields['nome'].error_messages['blank'] = mensagens.MSG2.format(u'nome')


class OrientacaoSexualSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrientacaoSexual
        fields = ['id', 'nome', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super(OrientacaoSexualSerializer, self).__init__(*args, **kwargs)

        self.fields['nome'].error_messages['blank'] = mensagens.MSG2.format(u'nome')


class ProfissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profissao
        fields = ['id', 'nome', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super(ProfissaoSerializer, self).__init__(*args, **kwargs)

        self.fields['nome'].error_messages['blank'] = mensagens.MSG2.format(u'nome')


class RacaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raca
        fields = ['id', 'nome', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super(RacaSerializer, self).__init__(*args, **kwargs)

        self.fields['nome'].error_messages['blank'] = mensagens.MSG2.format(u'nome')


class ReligiaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Religiao
        fields = ['id', 'nome', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super(ReligiaoSerializer, self).__init__(*args, **kwargs)

        self.fields['nome'].error_messages['blank'] = mensagens.MSG2.format(u'nome')

