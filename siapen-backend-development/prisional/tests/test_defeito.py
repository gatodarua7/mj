from comum.tests.base import SiapenTestCase
import requests
import json
from rest_framework import status


class TestDefeitoCelaEndpoint(SiapenTestCase):
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
        self.entidade = "Defeito 1"
        self.url = f"/api/prisional/defeito/"
        self.data = {
            "descricao": "SISTEMA PENAL DE SERGIPANO",
            "ativo": True,
        }
        super(TestDefeitoCelaEndpoint, self).setUp()

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
        data = self.data
        data["descricao"] = ""
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
        url = f'{self.url}?search=DEFEITÓ'
        resp = self.client.post(self.url, data=self.data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")
    
    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f'{self.url}?search=defeito'
        resp = self.client.post(self.url, data=self.data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_d_list(self):
        """
        List de objetos ativos
        """
        url = f'{self.url}?ativo=true'
        resp = self.client.post(self.url, data=self.data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos inativos
        """
        url = f'{self.url}?ativo=false'
        resp = self.client.post(self.url, data=self.data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """
        data = {
            "descricao": "Defeito 30",
            "ativo": True,
        }
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f"{self.base_url}/api/prisional/defeito/{resp_json['id']}/"
            resp = requests.delete(url, proxies=self.proxies, headers=self.headers)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.format_print(metodo="delete")


    def test_a_update(self):
        """
        Atualizando a descrição.
        """
        data = {
            "descricao": "Defeito 50",
            "ativo": True,
        }
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["descricao"] = "Defeito 60"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_b_update(self):
        """
        Atualizando a ativo.
        """
        data = {
            "descricao": "Defeito 70",
            "ativo": True,
        }
        resp = self.client.post(self.url, data=data)

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["descricao"] = "Defeito 70"
            resp_json["ativo"] = False
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="create")
