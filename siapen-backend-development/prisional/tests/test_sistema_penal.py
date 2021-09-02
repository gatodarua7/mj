from comum.tests.base import SiapenTestCase
from prisional.models import SistemaPenal
from rest_framework import status
from django.urls import reverse
import json
import requests


class TestSistemaPenalEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/estados.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/prisional/sistema.json",
        "fixtures/prisional/unidade.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Sistema Penal"
        self.url = f"/api/prisional/sistema-penal/"
        self.data = {
            "nome": "SISTEMA PENAL DE SERGIPANO",
            "sigla": "SPSE",
            "pais": 33,
            "estado": 28,
            "ativo": True,
        }
        super(TestSistemaPenalEndpoint, self).setUp()

    def test_a_create(self):
        """
        Cria objeto conforme esperado pela aplicação.
        """
        data = self.data
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Cria objeto de outro país com os dados esperados.
        """
        data = {
            "nome": "SISTEMA PENAL DO CANADA",
            "sigla": "SPCANA",
            "pais": 42,
            "estado": None,
            "ativo": False,
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Cria objeto com informação do estado informado como inteiro, se referindo a um estado que não existe.
        """
        data = {
            "nome": "SISTEMA PENAL DE ANGOLA",
            "sigla": "SPAN",
            "pais": 7,
            "estado": 0,
            "ativo": True,
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Cria objeto com informação do estado informado como string vazia, passando o valor de uma forma errada.
        """
        data = {
            "nome": "SISTEMA PENAL DO CAZAQUISTÃO",
            "sigla": "SPCAS",
            "pais": 44,
            "estado": "",
            "ativo": True,
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Cria objeto com informação do estado informado como inteiro, se referindo a um estado brasileiro existente.
        """
        data = {
            "nome": "SISTEMA PENAL ALEMÃO",
            "sigla": "SPAL",
            "pais": 5,
            "estado": 28,
            "ativo": False,
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_f_create(self):
        """
        Cria objeto com duplicidade de siglas, onde deveria ser identificador único.
        """
        data = {
            "nome": "SISTEMA PENAL ALAGOANO",
            "sigla": "SPSE",
            "pais": 33,
            "estado": 28,
            "ativo": True,
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        Listando os registros de sistema penal.
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        List de com acento
        """
        url = f'{self.url}?search=INICÌAL'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f'{self.url}?search=INICIAL'
        resp = self.client.post(self.url, data=self.data)
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
        Validando o processo de remoção de registro com estado existente.
        """
        data = {
            "nome": "SISTEMA PENAL PARA DELETAR",
            "sigla": "SPPD",
            "pais": 33,
            "estado": 28,
            "ativo": True,
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
        Apagando registro com estado inexistente.
        """
        data = {
            "nome": "SISTEMA PENAL PARA DELETAR",
            "sigla": "SPPD",
            "pais": 33,
            "estado": 18,
            "ativo": True,
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
        Atualizando registro de nome.
        """
        data = {
            "nome": "SISTEMA PENAL JABAQUARAAA",
            "sigla": "SPJQ",
            "pais": 33,
            "estado": 27,
            "ativo": True,
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "SISTEMA PENAL JABAQUARA ATUALIZADO"
            resp_json["sigla"] = "SPPD"
            resp_json["pais"] = 33
            resp_json["estado"] = 28
            resp_json["ativo"] = True
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_b_update(self):
        """
        Atualizando sigla de um sistema prisional.
        """
        data = {
            "nome": "SISTEMA PENAL JABAQUARAAAAAA",
            "sigla": "SPJQ",
            "pais": 33,
            "estado": 27,
            "ativo": True,
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["sigla"] = "SPJ"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')


    def test_c_update(self):
        """
        Atualizando país de um sistema prisional.
        """
        data = {
            "nome": "SISTEMA PENAL JABAQA",
            "sigla": "SPJQ",
            "pais": 33,
            "estado": 27,
            "ativo": True,
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "SISTEMA PENAL JBQ"
            resp_json["sigla"] = "SPPD"
            resp_json["pais"] = 28
            resp_json["estado"] = ""
            resp_json["ativo"] = True
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_d_update(self):
        """
        Atualizando o status de um sistema prisional.
        """
        data = {
            "nome": "SISTEMA PENAL JABAQA",
            "sigla": "SPJQ",
            "pais": 33,
            "estado": 27,
            "ativo": True,
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "SISTEMA JABAQA ATUALIZADO"
            resp_json["sigla"] = "SPPD"
            resp_json["pais"] = 28
            resp_json["estado"] = ""
            resp_json["ativo"] = False
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')
