from comum.tests.base import SiapenTestCase
from django.contrib.auth.models import User
from rest_framework import status
import json
import requests


class TestVisitanteEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/paises.json",
        "fixtures/cadastro/foto.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/raca.json",
        "fixtures/social/religiao.json",
        "fixtures/social/profissao.json",
        "fixtures/cadastro/genero.json",
        "fixtures/visitante/visitante.json",
        "fixtures/visitante/documentos_visitante.json",
        "fixtures/vinculos/tipo_vinculo.json",
        "fixtures/visitante/manifestacao_diretoria.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Visitante"
        self.url = f"/api/visitante/visitante/"
        self.data = {
            "nome": "João da Silva",
            "cpf": "23973947074",
            "foto": "15764e55-46a8-49ee-aa3e-56152dcb0c65",
            "data_nascimento": "21/02/1990",
            "idade": 30,
            "numero_sei": "11111.111111/1111-11",
            "telefones": [],
            "enderecos": [],
            "nacionalidade": [1],
            "situacao": False,
            "necessidade_especial": ["cc4c334e-7ab4-47fd-8a57-73c21dcda178"],
            "anuencias": [],
            "fase": "INICIADO",
        }
        super(TestVisitanteEndpoint, self).setUp()

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
        Criação de objeto duplicado.
        """
        data = self.data
        self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto invalido (sem campos obrigatorios).
        """
        data = {"idade": 30, "telefones": [], "enderecos": [], "nacionalidade": [3]}
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto invalido (brasileiro e maior de idade sem RG).
        """
        data = {
            "nome": "João da Silva",
            "data_nascimento": "21/02/1990",
            "numero_sei": "11111.111111/1111-11",
            "idade": 30,
            "telefones": [],
            "enderecos": [],
            "nacionalidade": [33],
            "naturalidade": 283,
            "estado": 29,
        }
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de objeto invalido (brasileiro sem cidade).
        """
        data = {
            "nome": "João da Silva",
            "data_nascimento": "21/02/1990",
            "numero_sei": "11111.111111/1111-11",
            "idade": 30,
            "telefones": [],
            "enderecos": [],
            "nacionalidade": [33],
            "naturalidade": [27],
        }
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_f_create(self):
        """
        Criação de objeto invalido (menor de idade e estrangeiro).
        """
        data = {
            "nome": "João da Silva",
            "data_nascimento": "21/02/2019",
            "numero_sei": "11111.111111/1111-11",
            "idade": 2,
            "telefones": [],
            "enderecos": [],
            "nacionalidade": [1],
        }
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_g_create(self):
        """
        Criação de objeto co telefone.
        """
        data = {
            "nome": "José Santo",
            "cpf": "50807471020",
            "data_nascimento": "21/02/1990",
            "numero_sei": "12345.111111/1111-11",
            "idade": 31,
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
            "nacionalidade": [33],
        }
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
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
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f"{self.url}?search=Condomínio"
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_d_list(self):
        """
        List de objetos ativos
        """
        url = f"{self.url}?ativo=true"
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos inativos
        """
        url = f"{self.url}?ativo=false"
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_a_update(self):
        """
        Atualizando objeto excluído.
        """
        data = {
            "nome": "João da Silva",
            "data_nascimento": "21/02/2019",
            "cpf": "15567918011",
            "numero_sei": "11111.111111/1111-11",
            "idade": 2,
            "telefones": [],
            "enderecos": [],
            "nacionalidade": [1],
            "anuencias": [],
            "fase": "INICIADO",
        }
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_b_update(self):
        """
        Atualizando dados do objeto
        """
        data = {
            "nome": "João da Silva",
            "data_nascimento": "21/02/2019",
            "cpf": "93327635005",
            "numero_sei": "11111.111111/1111-11",
            "idade": 2,
            "telefones": [],
            "enderecos": [],
            "nacionalidade": [1],
            "anuencias": [],
            "fase": "INICIADO",
        }
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["nome"] = "TESTANDO"
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="update")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """
        data = {
            "nome": "João da Silva",
            "data_nascimento": "21/02/2019",
            "cpf": "94412979091",
            "numero_sei": "11111.111111/1111-11",
            "idade": 2,
            "telefones": [],
            "enderecos": [],
            "nacionalidade": [1],
            "anuencias": [],
            "fase": "INICIADO",
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
