from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests



class TestContatosEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/estados.json",
        "fixtures/pessoas/advogado.json",
        "fixtures/cadastro/foto.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/cadastro/genero.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/religiao.json",
        "fixtures/vinculos/tipo_vinculo.json"

    ]
    def setUp(self) -> None:
        self.entidade = "Contatos"
        self.url = f"/api/pessoas/contatos-interno/"
        self.data = {"nome": "Luiz", 
                    "interno": "1191484a-4ab1-4662-8c41-269fc1e66e23",
                    "tipo_vinculo": "816579b4-0c3b-4c2f-a6d5-97e1dbc36444",
                    "enderecos": [{"id":"ffd0b5e5-0e26-4417-8bcd-88ad095ddb4a",
                                   "logradouro": "Rua 3",
                                    "bairro": "13 de Julho",
                                    "numero": 147,
                                    "complemento": "Condominio Tahiti",
                                    "estado": 28,
                                    "cidade": 2285,
                                    "andar": 9,
                                    "sala": "1",
                                    "cep":"45234-098"}], 
                    "telefones": [{"id":"90924433-e856-4d21-abf2-e14b09cf4042",
                                    "numero": 11911111111,
                                    "tipo": "CELULAR",
                                    "observacao": "Celular Institucional atribuído até dia 18/09/2050"}],
                    "ativo": True
        }
        super(TestContatosEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = requests.post(
             self.base_url+self.url, data=json.dumps(data), proxies=self.proxies, headers=self.headers)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto com sem vinculo.
        """
        data = self.data
        data["nome"] = "JOSE"
        data["tipo_vinculo"] = ""
        resp = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto com vinculo inexistente.
        """
        data = self.data
        data["nome"] = "Joao"
        data["tipo_vinculo"] = "1aa7de60-9666-4af6-a4da-1e0c64e75f08"
        resp = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto sem interno (nao tem validação).
        """
        data = self.data
        data["nome"] = "Joao"
        data["interno"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_a_update(self):
        """
        Atualizando objeto excluído.
        """

        data = self.data
        data["nome"] = "Maria"
        resp = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_b_update(self):
        """
        Atualizando nome do objeto
        """

        data = self.data
        data["nome"] = "Josefa"
        resp = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Finha"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """
        
        data = self.data
        data["nome"] = "Bruno"
        resp = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
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

        data = self.data
        data["nome"] = "Rita"
        resp = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            resp = self.client.delete(url)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="delete")