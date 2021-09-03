from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests
from typing import Optional
from datetime import datetime


class TestServidorEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/cadastro/foto.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/cadastro/genero.json",
        "fixtures/cadastro/orgao_expedidor.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/religiao.json",
        "fixtures/social/raca.json",
        "fixtures/cadastro/cargo.json",
        "fixtures/cadastro/funcao.json",
        "fixtures/cadastro/setor.json",
        "fixtures/pessoas/servidor.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Servidor"
        self.url = f"/api/pessoas/servidor/"
        self.data = {
            "nome": "JOSE MARIA",
            "nome_social": "",
            "cpf": "79968464058",
            "rg": "",
            "orgao_expedidor": "",
            "genero": "96637461-43cb-4d55-893b-c09fe514ecf7",
            "raca": "",
            "estado_civil": "3c2c263e-0713-4bf1-a707-903fe601e6ae",
            "nacionalidade": [1],
            "estado": "",
            "naturalidade": "",
            "nome_mae": "MARIA",
            "nome_pai": "JOSE",
            "grau_instrucao": "a414408d-aee8-44a7-b513-f7084fde2beb",
            "necessidade_especial": ["b83cb47a-dbdb-49e4-9ef7-34fcec39443f"],
            "orientacao_sexual": "fd9341f3-4c70-43a2-9e12-1e2da2d0ae4e",
            "religiao": "1c063b46-2b96-41a9-831d-4fed804ae05e",
            "enderecos": [
                {
                    "id": "ffd0b5e5-0e26-4417-8bcd-88ad095ddb4a",
                    "logradouro": "Rua 3",
                    "bairro": "13 de Julho",
                    "numero": 147,
                    "complemento": "Condominio Tahiti",
                    "estado": 28,
                    "cidade": 2285,
                    "andar": 9,
                    "sala": "1",
                    "cep": "45234-098",
                }
            ],
            "telefones": [
                {
                    "id": "90924433-e856-4d21-abf2-e14b09cf4042",
                    "numero": 11911111111,
                    "tipo": "CELULAR",
                    "observacao": "Celular Institucional atribuído até dia 18/09/2050",
                }
            ],
            "data_nascimento": "01/01/1980",
            "mae_falecido": False,
            "mae_nao_declarado": False,
            "pai_falecido": False,
            "pai_nao_declarado": False,
            "email_pessoal": "teste@teste.com",
            "email_profissional": "teste@mj.gov.br",
            "matricula": "12345678",
            "data_admissao": "01/12/2001",
            "lotacao": "f70266ac-74ea-4494-bd75-3fed4dd05848",
            "cargos": "05ebe3b6-a127-4c3b-9bf2-8c3034adea10",
            "funcao": ["a2c5d4ab-0d63-4c67-906a-e9a59f8bc77f"],
            "documentos": [],
            "telefones_funcionais": [
                {
                    "id": "eb43b191-cfad-4011-879d-b2da2466e8ea",
                    "numero": 9869,
                    "tipo": "RESIDENCIAL",
                    "observacao": "Ramal para testes",
                    "andar": "1",
                    "sala": "101",
                }
            ],
            "ativo": True,
        }
        super(TestServidorEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """

        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto com data invalida.
        """
        data = self.data
        data["nome"] = "JOSE"
        data["cpf"] = "93945356083"
        data["data_nascimento"] = "42/13/2001"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto com campos obrigatórios nao enviados.
        """
        data = self.data
        data["cpf"] = "52365715028"
        data["cargos"] = ""
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto com pai falecido e nao declarado.
        """
        data = self.data
        data["cpf"] = "93780825058"
        data["pai_falecido"] = True
        data["pai_nao_declarado"] = True
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de objeto com mae falecida e nao declarada.
        """
        data = self.data
        data["cpf"] = "11932591001"
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_f_create(self):
        """
        Criação de objeto cpf invalido.
        """
        data = self.data
        data["cpf"] = "11111111111"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_g_create(self):
        """
        Criação de objeto de uma cidade no estado em outro.
        """

        data = self.data
        data["cpf"] = "81787043070"
        data["nacionalidade"] = [33]
        data["estado"] = 28
        data["naturalidade"] = 12
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_h_create(self):
        """
        Criação de objeto duplicado.
        """
        data = self.data
        data["cpf"] = "79968464058"
        resp = self.client.post(self.url, data=data, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_i_create(self):
        """
        Criação de objeto com funcao Vazia.
        """
        data = self.data
        data["cpf"] = "52365715028"
        data["funcao"] = []
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        List de com acento
        """

        url = f"{self.url}?search=Condominio"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f"{self.url}?search=Jose"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_d_list(self):
        """
        List de objetos ativos
        """
        url = f"{self.url}?ativo=true"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos inativos
        """
        url = f"{self.url}?ativo=false"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_f_list(self):
        """
        List de objetos
        """
        url = f"{self.url}?exclude_ids=1191484a-4ab1-4662-8c41-269fc1e66e22"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """

        data = self.data
        data["cpf"] = "27696696050"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_b_delete(self):
        """
        Apagando registro excluido inexistente.
        """

        url = f'{self.url}{"c626e537-f520-4c87-b39b-2391294bdded"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_c_delete(self):
        """
        Apagando registro ja excluído.
        """
        url = f'{self.url}{"1191484a-4ab1-4662-8c41-269fc1e66e22"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="delete")

    def test_a_update(self):
        """
        Atualizando objeto excluído.
        """

        data = self.data
        data["cpf"] = "59315067053"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_b_update(self):
        """
        Atualizando nome do objeto
        """

        data = self.data
        data["cpf"] = "98925258099"
        resp = self.client.post(self.url, data=data, content_type="application/json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "JOSEFA"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="update")

    def test_c_update(self):
        """
        Atualizando nome do objeto inativo.
        """

        data = self.data
        data["cpf"] = "34333088020"
        data["ativo"] = False
        resp = requests.post(
            self.base_url + self.url,
            data=json.dumps(data),
            proxies=self.proxies,
            headers=self.headers,
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "TESTE INATIVO"
            url = f'{self.base_url+self.url}{resp_json["id"]}/'
            resp = requests.put(
                url, data=json.dumps(data), proxies=self.proxies, headers=self.headers
            )
            self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
            self.format_print(metodo="update")

    def test_d_update(self):
        """
        Atualizando cpf do objeto para valor invalido.
        """

        data = self.data
        data["cpf"] = "74635191044"
        resp = self.client.post(
            self.base_url + self.url,
            data=json.dumps(data),
            content_type="application/json",
            proxies=self.proxies,
            headers=self.headers,
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.base_url+self.url}{resp_json["id"]}/'
            resp = requests.put(
                url, data=json.dumps(data), proxies=self.proxies, headers=self.headers
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_e_update(self):
        """
        Atualizando data de admissao para valor invalido.
        """

        data = self.data
        data["cpf"] = "12738875068"
        resp = self.client.post(
            self.base_url + self.url,
            data=json.dumps(data),
            content_type="application/json",
            proxies=self.proxies,
            headers=self.headers,
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["data_admissao"] = "2999-15-14"
            url = f'{self.base_url+self.url}{resp_json["id"]}/'
            resp = requests.put(
                url, data=json.dumps(data), proxies=self.proxies, headers=self.headers
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_f_update(self):
        """
        Atualizando o objeto para valor funcao vazia
        """

        data = self.data
        data["cpf"] = "72717667075"
        resp = self.client.post(self.url, data=data, content_type="application/json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["funcao"] = []
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")
