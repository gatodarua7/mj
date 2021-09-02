from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests


class TestUnidadeCustodiaEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/estados.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/prisional/sistema.json",
        "fixtures/prisional/unidade.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Unidade de Custódia"
        self.url = f"/api/prisional/unidade/"
        self.data = {
            "nome": "UNIDADE DE CUSTÓDIA DE BRASÍLIA",
            "sigla": "UCBSB",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 3956,
            "estado": 28,
            "ativo": True
        }
        super(TestUnidadeCustodiaEndpoint, self).setUp()

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
        Criando objeto sem sistema prisional.
        """

        data = {
            "nome": "UNIDADE DE CUSTÓDIA 3",
            "sigla": "UCBSB3",
            "sistema":"8f18cb04-439a-40ab-af1f-137481e353db",
            "cidade": 3956,
            "estado":28,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criando objeto com apenas o nome diferente ao teste 1.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA 4",
            "sigla": "UCBSB",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 3956,
            "estado":28,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criando objeto de uma cidade de outro estado.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA DE BRASÍLIA",
            "sigla": "UCBSBAR",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 756,
            "estado": 15,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        Listando os registros de unidades de custódia.
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        List de com acento
        """
        url = f'{self.url}?search=CUSTÒDIA'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f'{self.url}?search=CUSTODIA'
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
            "nome": "UNIDADE DE CUSTÓDIA DO DF",
            "sigla": "UCDF",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 3956,
            "estado": 28,
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
        Apagando registro inexistente.
        """
        url = f'{self.url}"25a84ddd-ac32-43e8-8b3e-ccb00d60cf41"/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="delete")

    def test_a_update(self):
        """
        Atualizando o nome da unidade de custódia.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA",
            "sigla": "XYZ",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 123,
            "estado": 14,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "UNIDADE DE CUSTÓDIA ATUALIZADA" 
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_b_update(self):
        """
        Atualizando o sigla da unidade de custódia.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA",
            "sigla": "XYZ",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 123,
            "estado": 14,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["sigla"] = "XPTO" 
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_c_update(self):
        """
        Atualizando o sistema penal.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA",
            "sigla": "XYZ",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 123,
            "estado": 14,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["sistema"] = "87bdc2e5-4dbb-4405-9f5b-1a8f83830a0c" 
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_d_update(self):
        """
        Atualizando cidade.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA",
            "sigla": "XYZ",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 123,
            "estado": 14,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["cidade"] = 124
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_e_update(self):
        """
        Atualizando estado.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA",
            "sigla": "XYZ",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 123,
            "estado": 14,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["estado"] = 15
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_f_update(self):
        """
        Atualizando status ativo.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA",
            "sigla": "XYZ",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 123,
            "estado": 14,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["estado"] = 15
            resp_json["ativo"] = False
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_g_update(self):
        """
        Atualizando data.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA",
            "sigla": "XYZ",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 123,
            "estado": 14,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_h_update(self):
        """
        Atualizando usuário que gerou a ação.
        """
        data = {
            "nome": "UNIDADE DE CUSTÓDIA",
            "sigla": "XYZ",
            "sistema":"21796b1d-082d-43f3-804f-57c58d803087",
            "cidade": 123,
            "estado": 14,
            "ativo": True
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["usuario_edicao"] = 2
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')
