from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests


class TestEscoltaEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/movimentacao/pedido-inclusao.json",
        "fixtures/movimentacao/fases.json",
        "fixtures/cadastro/genero.json",
        "fixtures/cadastro/regime_prisional.json",
        "fixtures/cadastro/orgao_expedidor.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/religiao.json",
        "fixtures/pessoas/servidor.json",
        "fixtures/cadastro/cargo.json",
        "fixtures/cadastro/funcao.json",
        "fixtures/cadastro/setor.json",
        "fixtures/social/raca.json"
    ]

    def setUp(self) -> None:
        self.entidade = "Escolta"
        self.url = f"/api/escoltas/escoltas/"
        self.data = {
            "data_fim_aerea": "24/07/2021",
            "data_fim_terrestre": "24/07/2021",
            "data_inicio_aerea": "24/07/2021",
            "data_inicio_terrestre": "24/07/2021",
            "descricao_aerea": "TESTE",
            "dia_semana_fim_aereo": "Quarta-feira",
            "dia_semana_fim_terrestre": "Quarta-feira",
            "dia_semana_inicio_aereo": "Quarta-feira",
            "dia_semana_inicio_terrestre": "Quarta-feira",
            "escolta_aerea": "Início: 24/07/2021 21:10 - Fim: 24/07/2021 23:00",
            "escolta_terrestre": "Início: 24/07/2021 23:00 - Fim: 24/07/2021 23:59",
            "fase_escolta_aerea": "FINALIZADA",
            "fase_escolta_terrestre": "FINALIZADA",
            "fim_terrestre": "24/07/2021 23:59",
            "hora_fim_aerea": "23:00:00",
            "hora_fim_terrestre": "23:59:00",
            "hora_inicio_aerea": "21:10:00",
            "hora_inicio_terrestre": "23:01:00",
            "inicio_aereo": "24/07/2021 21:10",
            "inicio_terrestre": "24/07/2021 23:00",
            "instituicao": "PC",
            "nome_missao": "Operação",
            "numero_documento_sei": "10",
            "numero_escolta": "077/2021",
            "numero_sei": "54444.444444/4444-44",
            "ordem_missao": "TESTE",
            "pedidos_inclusao": [{"tipo_inclusao": "EMERGENCIAL", "id": "0afdff24-e1d5-401b-a4f3-639fb3236c0e", "nome": "JOSE MARIA DOS SANTOS", "aguardando_escolta": True}],
            "responsavel": "DEPEN",
            "servidores_escolta_aerea": [{"id": "1191484a-4ab1-4662-8c41-269fc1e66e22", "nome": "JOSE MARIA", "cpf": "33245741022"}],
            "servidores_escolta_terrestre": [],
            "status_aerea": "FINALIZADA",
            "status_terrestre": "FINALIZADA",
            "tipo_aeronave": "INSTITUCIONAL",
            "tipo_escolta": "INCLUSAO",
            "unidade_nome": ["UNIDADE DE CUSTÓDIA DE BRASÍLIA"],
            "voos": []
            }
        super(TestEscoltaEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto sem pedidos inclusao
        """
        data = self.data
        data["pedidos_inclusao"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")


    def test_c_create(self):
        """
        Criação de objeto com pedido inclusao invalido
        """
        data = self.data
        data["pedidos_inclusao"] = "f4ff1afb-b510-44f0-b409-5a657c98004a"
        data["aguardando_escolta"] = False
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")


    def test_d_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_e_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """

        data = {
            "data_fim_aerea": "24/07/2021",
            "data_fim_terrestre": "24/07/2021",
            "data_inicio_aerea": "24/07/2021",
            "data_inicio_terrestre": "24/07/2021",
            "descricao_aerea": "TESTE",
            "dia_semana_fim_aereo": "Quarta-feira",
            "dia_semana_fim_terrestre": "Quarta-feira",
            "dia_semana_inicio_aereo": "Quarta-feira",
            "dia_semana_inicio_terrestre": "Quarta-feira",
            "escolta_aerea": "Início: 24/07/2021 21:10 - Fim: 24/07/2021 23:00",
            "escolta_terrestre": "Início: 24/07/2021 23:00 - Fim: 24/07/2021 23:59",
            "fase_escolta_aerea": "FINALIZADA",
            "fase_escolta_terrestre": "FINALIZADA",
            "fim_terrestre": "24/07/2021 23:59",
            "hora_fim_aerea": "23:00:00",
            "hora_fim_terrestre": "23:59:00",
            "hora_inicio_aerea": "21:10:00",
            "hora_inicio_terrestre": "23:01:00",
            "inicio_aereo": "24/07/2021 21:10",
            "inicio_terrestre": "24/07/2021 23:00",
            "instituicao": "PC",
            "nome_missao": "Operação",
            "numero_documento_sei": "10",
            "numero_escolta": "077/2021",
            "numero_sei": "54444.444444/4444-44",
            "ordem_missao": "TESTE",
            "pedidos_inclusao": [{"tipo_inclusao": "EMERGENCIAL", "id": "0afdff24-e1d5-401b-a4f3-639fb3236c0e", "nome": "JOSE MARIA DOS SANTOS", "aguardando_escolta": True}],
            "responsavel": "DEPEN",
            "servidores_escolta_aerea": [{"id": "1191484a-4ab1-4662-8c41-269fc1e66e22", "nome": "JOSE MARIA", "cpf": "33245741022"}],
            "servidores_escolta_terrestre": [],
            "status_aerea": "FINALIZADA",
            "status_terrestre": "FINALIZADA",
            "tipo_aeronave": "INSTITUCIONAL",
            "tipo_escolta": "INCLUSAO",
            "unidade_nome": ["UNIDADE DE CUSTÓDIA DE BRASÍLIA"],
            "voos": []
        }
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_b_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"4f7badd4-50e1-4a75-baf9-b5435f2b9a89"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")
