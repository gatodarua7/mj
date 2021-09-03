from comum.tests.base import SiapenTestCase
from rest_framework import status
from localizacao.models import Estado
from django.contrib.auth.models import User
from util import mensagens


class TestEstadoEndpoint(SiapenTestCase):
    fixtures = ["fixtures/localizacao/paises.json"]

    def setUp(self) -> None:
        self.entidade = "Estados"
        self.data = {"pais": 1, "nome": "TESTE_ESTADO", "sigla": "TT"}
        self.url = f"/api/localizacao/estados/"
        super(TestEstadoEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto invalido.
        """
        data = self.data
        data["sigla"] = ""
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        criar objeto valido.
        """
        data = self.data
        data["sigla"] = "TT"
        resp = self.client.post(self.url, data=self.data)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto extrapolando campos.
        """
        data = self.data
        data["sigla"] = "TTTTTTTTTTT"
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        Criação de objeto vazio.
        """
        resp = self.client.get(self.url)
        resp_json = resp.json()
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        List
        """
        resp = self.client.post(self.url, data=self.data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
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

        url = f"{self.url}99999999/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_a_update(self):
        """
        Atualização de objeto invalido.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["sigla"] = ""
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=data)
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
            resp_json["sigla"] = "TTT"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="update")

    def test_c_update(self):
        """
        Atualização de objeto Extrapolando campos.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["sigla"] = "GGGGG"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
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
            resp_json["sigla"] = "GG"
            url = f"{self.url}999999999/"
            response = self.client.patch(url, data=resp_json)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.format_print(metodo="update")
