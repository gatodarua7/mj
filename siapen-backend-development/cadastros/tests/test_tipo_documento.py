from comum.tests.base import SiapenTestCase
from rest_framework import status
from django.contrib.auth.models import User
import requests
import json
from util import mensagens


class TestTipoDocumentoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/cadastro/tipo_documento.json",
    ]

    def setUp(self) -> None:
        self.entidade = "TIPO_DOCUMENTO"
        self.data = {"nome": "CERTIDÃO TESTE", "ativo": True}
        self.url = f"/api/cadastros/tipo-documento/"
        super(TestTipoDocumentoEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

    def test_b_create(self):
        """
        Criação de objeto DUPLICADO.
        """
        data = self.data
        self.client.post(self.url, data=self.data)
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.format_print(metodo='create')

    def test_d_create(self):
        """
        Criação de objeto nome vazia.
        """
        data = self.data
        data["nome"] = ""
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_e_create(self):
        """
        Criação de objeto inativo.
        """
        data = self.data
        data["nome"] = "CERTIDAO TESTE INATIVO"
        data["ativo"] = False
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

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

        url = f'{self.url}?search=CERTIDÃO'
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
        url = f'{self.url}?search=CERTIDAO'
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
        Deletar um registro.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_b_delete(self):
        """
        Deletar um registro invalido.
        """

        url = f"{self.url}c040f4a0-05ba-45de-ab85-0c30e165ee82/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="delete")

    def test_c_delete(self):
        """
        Deletar um registro com vinculo.
        """
        url = f"{self.base_url+self.url}3c2c263e-0713-4bf1-a707-903fe601e6ae/"
        resp = requests.delete(url, proxies=self.proxies, headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="delete")

    def test_d_delete(self):
        """
        Apagando registro associado a pessoa.
        """
        url = f"{self.base_url+self.url}3c2c263e-0713-4bf1-a707-903fe601e6aepyt/"
        resp = requests.delete(url, proxies=self.proxies, headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="delete")

    def test_a_update(self):
        """
        Atualização de objeto excluido.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_b_update(self):
        """
        Atualização de objeto valido.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["nome"] = "TESTANDO" 
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="update")

    def test_c_update(self):
        """
        Atualizando nome do objeto inativo.
        """
        data = self.data
        data["ativo"] = False
        resp = requests.post(
            self.base_url+self.url,
            data=json.dumps(data),
            proxies=self.proxies,
            headers=self.headers)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "TESTE INATIVO"
            url = f'{self.base_url+self.url}{resp_json["id"]}/'
            resp = requests.put(url, data=json.dumps(data), proxies=self.proxies, headers=self.headers)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_d_update(self):
        """
        Atualização de objeto inexistente.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}7124d8d8-21b4-4d6e-aa3a-687ad2ccccc4/'
            response = self.client.patch(url, data=resp_json)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.format_print(metodo="update")

    def test_e_update(self):
        """
        Atualizando nome de objeto para já existente
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "CERTIDÃO NASCIMENTO"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
            self.format_print(metodo="update")