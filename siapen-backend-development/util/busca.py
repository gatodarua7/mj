from unidecode import unidecode
from datetime import datetime, timezone, timedelta
import re

# Função para normalizar os campos de busca
def trata_campo(campo):
    return unidecode(str(campo).upper().strip().replace("'", "")) if campo else ""


def formata_data(data):
    if data:
        data = data.split("-")
        ano = data[0]
        mes = data[1]
        dia = data[2]
        data = "{}/{}/{}".format(dia, mes, ano)
    return data

def formata_hora(data):
    return data.strftime('%H:%M')

def formata_data_usa(data):
    if data:
        data = data.split("/")
        dia = data[0]
        mes = data[1]
        ano = data[2]
        data = "{}-{}-{}".format(ano, mes, dia)
    return data

def formata_data_hora(data):
    fuso_horario = timezone(timedelta(hours=-3))
    data_hora = data.astimezone(fuso_horario)
    return data_hora.strftime("%d/%m/%Y %H:%M:%S")

def get_nome_semana(data):
    dias_semana = {'Sunday': 'Domingo',
                    'Monday': 'Segunda-feira',
                    'Tuesday': 'Terça-feira',
                    'Wednesday': 'Quarta-feira',
                    'Thursday': 'Quinta-feira',
                    'Friday': 'Sexta-feira',
                    'Saturday': 'Sábado'}
    return dias_semana[data.strftime('%A')]

def concatena_data_hora(data, hora):
    return f"{data.strftime('%Y-%m-%d')} {hora.strftime('%H:%M')}"

def cast_string_in_datetime(data):
    return datetime.strptime(data, '%Y-%m-%d %H:%M')

def formata_data_escolta_aerea(data):
    inicio = f"{data.data_inicio_aerea.strftime('%d/%m/%Y')} {data.hora_inicio_aerea.strftime('%H:%M')}"
    fim = f"{data.data_fim_aerea.strftime('%d/%m/%Y')} {data.hora_fim_aerea.strftime('%H:%M')}"
    escolta = f'Início: {inicio} - Fim: {fim}'
    return escolta

def formata_data_escolta_terrestre(data):
    inicio = f"{data.data_inicio_terrestre.strftime('%d/%m/%Y')} {data.hora_inicio_terrestre.strftime('%H:%M')}"
    fim = f"{data.data_fim_terrestre.strftime('%d/%m/%Y')} {data.hora_fim_terrestre.strftime('%H:%M')}"
    escolta = f'Início: {inicio} - Fim: {fim}'
    return escolta

def converte_string_data_hora(data, hora='00:00'):
    """Concatena data e hora STR para datetime"""
    return datetime.fromisoformat(f"{formata_data_usa(data)} {hora_inicio}")

def check_duplicidade(campo):
    """
    Método responsável por normalizar os campos de busca
    """
    return str(campo).upper().strip() if campo else ""


def trata_campo_ativo(ativo=None):
    if ativo is not None:
        if ativo == "true":
            ativo = True
        elif ativo == "false":
            ativo = False
    return ativo


def trata_telefone(busca):
    import re

    busca = re.sub(u"[^a-zA-Z0-9: ]", "", busca.encode().decode("utf-8"))
    busca = busca.replace(" ", "")
    return busca

def trata_email(email):
    if(re.match(u"[\w\.-]+@[\w\.-]+(\.[\w]+)+", email)):
        return True
    else:
        return False

def get_ids(list_dicts):
    list_ids = list()
    if list_dicts:
        for requisicao in list_dicts:
            list_ids.append(requisicao["id"])
    return list_ids

def has_key(key, requisicao):
    return key in requisicao
