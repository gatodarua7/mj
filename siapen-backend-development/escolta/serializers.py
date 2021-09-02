from datetime import date, datetime
import re
from core.models import BaseModel
from django.forms.models import model_to_dict
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField
from rest_flex_fields import FlexFieldsModelSerializer
from escolta.models import (Escoltas, VoosEscolta)
from rest_framework import serializers
from util import mensagens
from util.busca import formata_data_escolta_aerea, formata_data_escolta_terrestre, get_nome_semana, concatena_data_hora, cast_string_in_datetime
from util.image import get_thumbnail
from uuid import UUID



class EscoltasSerializer(FlexFieldsModelSerializer):
    pedidos_inclusao = SerializerMethodField()
    servidores_escolta_aerea = SerializerMethodField()
    servidores_escolta_terrestre = SerializerMethodField()
    escolta_aerea = SerializerMethodField()
    escolta_terrestre = SerializerMethodField()
    voos = SerializerMethodField()
    usuario_cadastro_nome = SerializerMethodField()
    dia_semana_fim_terrestre = SerializerMethodField()
    dia_semana_fim_aereo = SerializerMethodField()
    dia_semana_inicio_terrestre = SerializerMethodField()
    dia_semana_inicio_aereo = SerializerMethodField()
    inicio_terrestre = SerializerMethodField()
    fim_terrestre = SerializerMethodField()
    inicio_aereo = SerializerMethodField()
    fim_aereo = SerializerMethodField()
    status_aerea = SerializerMethodField()
    status_terrestre = SerializerMethodField()
    unidade_nome = SerializerMethodField()

    class Meta:
        model = Escoltas
        exclude = ("usuario_cadastro",)

    def __init__(self, *args, **kwargs):
        super(EscoltasSerializer, self).__init__(*args, **kwargs)

        mandatory_fields = {
            "numero_sei": mensagens.MSG2.format("Nº SEI"),
            "numero_documento_sei": mensagens.MSG2.format("Nº documento SEI"),
            "responsavel": mensagens.MSG2.format("responsável"),
            "pedidos_inclusao": mensagens.MSG2.format("pedidos inclusão"),
            "ordem_missao": mensagens.MSG2.format("Ordem de missão penitenciária")
        }

        for key, value in mandatory_fields.items():
            self.fields[key].error_messages["required"] = value
            self.fields[key].error_messages["blank"] = value
            self.fields[key].error_messages["null"] = value


    def validate(self, data):
        erro = dict()
        if not self.check_periodo_escolta(data, 'aerea') and not self.check_periodo_escolta(data):
            raise serializers.ValidationError({'non_field_errors': mensagens.MSG_ESCOLTA})
        if self.check_periodo_escolta(data, 'aerea'):
            erro.update(self.check_fields_periodo_escolta(data, 'aerea'))
            if not erro.get('data_fim_aerea') and not erro.get('hora_fim_aerea'):
                erro.update(self.check_data_fim_escolta(data, 'aerea'))
        if self.check_periodo_escolta(data):
            erro.update(self.check_fields_periodo_escolta(data))
            if not erro.get('data_fim_terrestre') and not erro.get('hora_fim_terrestre'):
                erro.update(self.check_data_fim_escolta(data))
        if ((self.check_periodo_escolta(data, 'aerea') and 
            self.check_periodo_escolta(data)) and 
            (not self.check_periodo_escolta(erro, 'aerea') and 
            not self.check_periodo_escolta(erro))):
            erro.update(self.check_data_fim_escolta_terrestre(data))
        if data.get('responsavel') == 'DEPEN' and self.check_periodo_escolta(data, 'aerea'):
            erro.update(self.check_fields_escolta_depen(data))
        if erro:
            raise serializers.ValidationError(erro)
        return data
    
    def check_fields_escolta_depen(self, data):
        erro = dict()
        if not data.get('tipo_aeronave'):
            erro['tipo_aeronave'] = mensagens.MSG2.format("aeronave")
        if data.get('tipo_aeronave') == 'INSTITUCIONAL' and not data.get('instituicao'):
            erro['instituicao'] = mensagens.MSG2.format("instituição")
        return erro
    
    def check_periodo_escolta(self, data, tipo_escolta='terrestre'):
        """ Verifica a o preencimento dos campos de escolta aérea/terrestre"""
        return (data.get(f'data_inicio_{tipo_escolta}') or 
                data.get(f'data_fim_{tipo_escolta}') or 
                data.get(f'hora_inicio_{tipo_escolta}') or 
                data.get(f'hora_fim_{tipo_escolta}'))

    def check_fields_periodo_escolta(self, data, tipo_escolta='terrestre'):
        erro = dict()
        if not data.get(f'data_inicio_{tipo_escolta}'):
            erro[f'data_inicio_{tipo_escolta}'] = mensagens.MSG2.format("data de início")     
        if not data.get(f'data_fim_{tipo_escolta}'):
            erro[f'data_fim_{tipo_escolta}'] = mensagens.MSG2.format("data fim")       
        if not data.get(f'hora_inicio_{tipo_escolta}'):
            erro[f'hora_inicio_{tipo_escolta}'] = mensagens.MSG2.format("hora de início")   
        if not data.get(f'hora_fim_{tipo_escolta}'):
            erro[f'hora_fim_{tipo_escolta}'] = mensagens.MSG2.format("hora fim")   
        return erro

    def check_data_fim_escolta(self, data, tipo_escolta='terrestre'):
        erro = dict()
        if data.get(f'data_inicio_{tipo_escolta}') and data.get(f'data_fim_{tipo_escolta}'):
            if data.get(f'data_inicio_{tipo_escolta}') > data.get(f'data_fim_{tipo_escolta}'):
                erro[f'data_fim_{tipo_escolta}'] = "Data fim não pode ser menor que a data de início." 
            elif ((data.get(f'data_inicio_{tipo_escolta}') == data.get(f'data_fim_{tipo_escolta}')) and 
                    data.get(f'hora_inicio_{tipo_escolta}') >= data.get(f'hora_fim_{tipo_escolta}')):
                erro[f'hora_fim_{tipo_escolta}'] = "Hora fim deve ser maior que a hora de início."    
        return erro
    
    def check_data_fim_escolta_terrestre(self, data):
        erro = dict()
        if data.get(f'data_fim_aerea') > data.get(f'data_fim_terrestre'):
            erro[f'data_fim_terrestre'] = "Data fim terrestre não pode ser menor que a data fim aérea." 
        elif ((data.get(f'data_fim_aerea') == data.get(f'data_fim_terrestre')) and 
                data.get(f'hora_fim_aerea') >= data.get(f'hora_fim_terrestre')):
            erro[f'hora_fim_terrestre'] = "Hora fim terrestre deve ser maior que a hora fim aérea."    
        return erro

    def get_pedidos_inclusao(self, obj):
        pedidos_inclusao = list()
        for query in obj.pedidos_inclusao.all():
            dict_pedido = {
                "tipo_inclusao": query.tipo_inclusao,
                "id": query.pk,
                "nome": query.nome,
                "cpf": query.cpf,
                "unidade_nome": query.unidade.nome if query.unidade else "",
                "estado_solicitante_nome": query.estado_solicitante.nome if query.estado_solicitante else "",
                "foto": get_thumbnail(query.foto_id)
            }
            pedidos_inclusao.append(dict_pedido)
        return pedidos_inclusao
    
    def get_servidores_escolta_aerea(self, obj):
        servidores = list()
        if obj.servidores_escolta_aerea:
            servidores.extend(self.get_servidor(obj.servidores_escolta_aerea.all()))
        return servidores
    
    def get_escolta_aerea(self, obj):
        data_escolta = ""
        if obj.data_inicio_aerea:
           data_escolta = formata_data_escolta_aerea(obj)
        return data_escolta

    def get_servidores_escolta_terrestre(self, obj):
        servidores = list()
        if obj.servidores_escolta_terrestre:
           servidores.extend(self.get_servidor(obj.servidores_escolta_terrestre.all()))
        return servidores
    
    def get_escolta_terrestre(self, obj):
        data_escolta = ""
        if obj.data_inicio_terrestre:
            data_escolta = formata_data_escolta_terrestre(obj)
        return data_escolta
    
    def get_voos(self, obj):
        voos = list()
        for query in VoosEscolta.objects.filter(escolta_id=obj.pk):
            dict_voo = {
                "numero_voo": query.voo
            }
            voos.append(dict_voo)
        return voos
    
    def get_servidor(self, servidor_list):
        servidores = list()
        for query in servidor_list:
            dict_pedido = {
                "id": query.pk,
                "nome": query.nome,
                "cpf": query.cpf,
                "cargo_nome": query.cargos.cargo if query.cargos else "",
                "matricula": query.matricula,
                "thumbnail": get_thumbnail(query.foto_id)
            }
            servidores.append(dict_pedido)
        return servidores

    def get_inicio_aereo(self, obj):
        return concatena_data_hora(obj.data_inicio_aerea, obj.hora_inicio_aerea) if obj.data_inicio_aerea else None

    def get_fim_aereo(self, obj):
        return concatena_data_hora(obj.data_fim_aerea, obj.hora_fim_aerea) if obj.data_fim_aerea else None
    
    def get_inicio_terrestre(self, obj):
        return concatena_data_hora(obj.data_inicio_terrestre, obj.hora_inicio_terrestre) if obj.data_inicio_terrestre else None
    
    def get_fim_terrestre(self, obj):
        return concatena_data_hora(obj.data_fim_terrestre, obj.hora_fim_terrestre) if obj.data_fim_terrestre else None

    def get_dia_semana_inicio_aereo(self, obj):
        return get_nome_semana(obj.data_inicio_aerea) if obj.data_inicio_aerea else None

    def get_dia_semana_fim_aereo(self, obj):
        return get_nome_semana(obj.data_fim_aerea) if obj.data_fim_aerea else None
    
    def get_dia_semana_inicio_terrestre(self, obj):
        return get_nome_semana(obj.data_inicio_terrestre) if obj.data_inicio_terrestre else None
    
    def get_dia_semana_fim_terrestre(self, obj):
        return get_nome_semana(obj.data_fim_terrestre) if obj.data_fim_terrestre else None

    def get_usuario_cadastro_nome(self, obj):
        return obj.usuario_cadastro.username
    
    def get_status_aerea(self, obj):
        fase = None
        if obj.data_inicio_aerea:
            fase = self.check_status_escolta_aerea(obj)
        if fase and fase != obj.fase_escolta_aerea:
            Escoltas.objects.filter(id=obj.pk).update(fase_escolta_aerea=fase)
        return fase

    def get_status_terrestre(self, obj):
        fase = None
        if obj.data_inicio_terrestre:
            fase = self.check_status_escolta_terrestre(obj)
        if fase and fase != obj.fase_escolta_terrestre:
            Escoltas.objects.filter(id=obj.pk).update(fase_escolta_terrestre=fase)
        return fase

    def check_status_escolta_aerea(self, obj):
        now = datetime.now()
        status = 'AGENDADA'
        data_hora_inicio = concatena_data_hora(obj.data_inicio_aerea, obj.hora_inicio_aerea)
        data_hora_fim = concatena_data_hora(obj.data_fim_aerea, obj.hora_fim_aerea)
        if now > cast_string_in_datetime(data_hora_fim):
            status = 'FINALIZADA'
        elif now > cast_string_in_datetime(data_hora_inicio) and now < cast_string_in_datetime(data_hora_fim):
            status = 'INICIADA_AEREA'
        if status == 'AGENDADA' and obj.fase_escolta_terrestre == 'FINALIZADA':
            status = 'EM_TRANSITO'
        return status

    def check_status_escolta_terrestre(self, obj):
        now = datetime.now()
        status = 'AGENDADA'
        data_hora_inicio = concatena_data_hora(obj.data_inicio_terrestre, obj.hora_inicio_terrestre)
        data_hora_fim = concatena_data_hora(obj.data_fim_terrestre, obj.hora_fim_terrestre)
        if now > cast_string_in_datetime(data_hora_fim):
            status = 'FINALIZADA'
        elif now > cast_string_in_datetime(data_hora_inicio) and now < cast_string_in_datetime(data_hora_fim):
            status = 'INICIADA_TERRESTRE'
        if status == 'AGENDADA' and obj.fase_escolta_aerea == 'FINALIZADA':
            status = 'EM_TRANSITO'
        return status

    
    def get_unidade_nome(self, obj):
        unidade_nome = [pedido.unidade.nome for pedido in obj.pedidos_inclusao.all() if pedido.unidade]
        return sorted(set(unidade_nome)) if unidade_nome else unidade_nome