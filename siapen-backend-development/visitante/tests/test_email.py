from comum.tests.base import SiapenTestCase
from django.contrib.auth.models import User
from rest_framework import status
import json
import requests


class TestEmailEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/estados.json",
        "fixtures/visitante/visitante.json",
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
        "fixtures/social/religiao.json"

    ]

    def setUp(self) -> None:
        self.entidade = "EmailVisitante"
        self.url = f"/api/pessoas/email/"
        self.data = {
            "email": "teste@gmail.com",
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92",      
        }
        super(TestEmailEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
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
        Atualizando objeto excluido.
        """

        data = self.data
        data["visitante"] = "2939da1f-552d-4997-b8de-3d956359ec92"
        data["nome"] = "novoemail@outlook.com"
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
            self.format_print(metodo="Update")

    def test_b_update(self):
        """
        Atualizando dados do objeto
        """

        data = self.data
        data["visitante"] = "2939da1f-552d-4997-b8de-3d956359ec92"
        data["email"] = "outrovisitante@gmail.com"
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["email"] = "visitante1@gmail.com"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """

        data = self.data
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
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.format_print(metodo="delete")
