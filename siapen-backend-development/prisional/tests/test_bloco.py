from comum.tests.base import SiapenTestCase
import requests
import json
from rest_framework import status


class TestBlocoEndpoint(SiapenTestCase):
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
        self.entidade = "Bloco"
        self.url = f"/api/prisional/bloco/"
        self.data = {
            "unidade": "c612a4bf-0837-47b4-ade8-8ac3ad9f8bc9",
            "nome": "BLOCO A1",
            "bloco_pai": None,
            "ativo": True,
        }
        super(TestBlocoEndpoint, self).setUp()

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
        Criação de objeto vazio.
        """
        data = {
            "unidade": None, 
            "nome": None, 
            "bloco_pai": None,
            "ativo": None
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

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
        url = f'{self.url}?search=BLOCÓ'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f'{self.url}?search=BLOCO'
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
            "unidade": "c612a4bf-0837-47b4-ade8-8ac3ad9f8bc9", 
            "nome": "BLOCO D", 
            "bloco_pai": None,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_b_delete(self):
        """
        Validando o processo de remoção de registro inválido.
        """
        data = {
            "unidade": "f612a4bf-0837-47b4-ade8-8ac3ad9f8bc4", 
            "nome": "BLOCO db", 
            "bloco_pai": None,
            "ativo": True
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
            "unidade": "c612a4bf-0837-47b4-ade8-8ac3ad9f8bc9", 
            "nome": "BLOCO AU", 
            "bloco_pai": None,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["unidade"] = "c612a4bf-0837-47b4-ade8-8ac3ad9f8bc9"
            resp_json["nome"] = "BLOCO AU ATUALIZADO"
            resp_json["bloco_pai"] = None
            resp_json["ativo"] = True
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_b_update(self):
        """
        Atualizando a ativo.
        """
        data = {
            "unidade": "c612a4bf-0837-47b4-ade8-8ac3ad9f8bc9", 
            "nome": "BLOCO BCU", 
            "bloco_pai": None,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["unidade"] = "c612a4bf-0837-47b4-ade8-8ac3ad9f8bc9"
            resp_json["nome"] = "BLOCO BU ATUALIZADO"
            resp_json["bloco_pai"] = None
            resp_json["ativo"] = False
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")
