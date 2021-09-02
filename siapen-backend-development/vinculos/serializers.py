from vinculos.models import TipoVinculo
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from util import mensagens


class TipoVinculoSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = TipoVinculo
        fields = ['id', 'nome', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super(TipoVinculoSerializer, self).__init__(*args, **kwargs)

        self.fields['nome'].error_messages['blank'] = mensagens.MSG2.format(u'nome')