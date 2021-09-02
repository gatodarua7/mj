from comum.tests.base import SiapenTestCase
import requests
import json
from rest_framework import status


class TestCelaEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/estados.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/prisional/sistema.json",
        "fixtures/prisional/unidade.json",
        "fixtures/prisional/bloco.json",
        "fixtures/prisional/cela.json",
    ]


    def setUp(self) -> None:
        self.entidade = 'Cela'
        self.url = f'/api/prisional/cela/'
        self.data = {
            "bloco": "8daa2753-4a87-4d40-ab8d-4ffdc2706f19", 
            "nome": "Cela A", 
            "capacidade": 50,
            "ativo": True, 
            "observacao": ""
        }
        self.cela_excluida = None
        super(TestCelaEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

    def test_b_create(self):
        """
        Criação de objeto vazio.
        """
        data = {
            "bloco": None, 
            "nome": None, 
            "capacidade": None,
            "ativo": None, 
            "observacao": None
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_a_list(self):
        """
        Criação de objeto vazio.
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        List de com acento
        """
        url = f'{self.url}?search=CELÁ'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f'{self.url}?search=cela'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_d_list(self):
        """
        List de objetos ativos
        """
        url = f'{self.url}?ativo=true'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos inativos
        """
        url = f'{self.url}?ativo=false'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")


    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """
        data = {
            "bloco": "8daa2753-4a87-4d40-ab8d-4ffdc2706f19", 
            "nome": "Cela B", 
            "capacidade": 10,
            "ativo": True, 
            "observacao": "Nenhuma"
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_a_update(self):
        """
        Atualizando campos.
        """
        data = {
            "bloco": "8daa2753-4a87-4d40-ab8d-4ffdc2706f19", 
            "nome": "Cela D", 
            "capacidade": 100,
            "ativo": True, 
            "observacao": "Nenhuma"
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["bloco"] = "8daa2753-4a87-4d40-ab8d-4ffdc2706f19"
            resp_json["nome"] = "Cela D Atualizada"
            resp_json["capacidade"] = 10
            resp_json["ativo"] = True
            resp_json["observacao"] = "Nada"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_b_update(self):
        """
        Inativando Cela.
        """
        data = {
            "bloco": "8daa2753-4a87-4d40-ab8d-4ffdc2706f19", 
            "nome": "Cela E", 
            "capacidade": 10,
            "ativo": True, 
            "observacao": "Nenhuma"
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["bloco"] = "8daa2753-4a87-4d40-ab8d-4ffdc2706f19"
            resp_json["nome"] = "Cela E"
            resp_json["capacidade"] = 10
            resp_json["ativo"] = True
            resp_json["observacao"] = "Nada"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")
    
    def test_c_update(self):
        """
        Atualizando Cela Inativa.
        """
        data = {
            "bloco": "8daa2753-4a87-4d40-ab8d-4ffdc2706f19", 
            "nome": "Cela G", 
            "capacidade": 10,
            "ativo": False, 
            "observacao": "Nenhuma"
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["bloco"] = "8daa2753-4a87-4d40-ab8d-4ffdc2706f19"
            resp_json["nome"] = "Cela GE"
            resp_json["capacidade"] = 10
            resp_json["ativo"] = False
            resp_json["observacao"] = "Nenhuma"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")
