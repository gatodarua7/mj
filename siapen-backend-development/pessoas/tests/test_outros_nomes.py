from comum.tests.base import SiapenTestCase
from django.contrib.auth.models import User
from rest_framework import status
import json
import requests


class TestOutroNomeInternoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/pessoas/interno.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/raca.json",
        "fixtures/social/religiao.json",
        "fixtures/social/profissao.json",
        "fixtures/cadastro/genero.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
    ]

    def setUp(self) -> None:
        self.entidade = "OutroNome"
        self.url = f"/api/pessoas/outro-nome/"
        self.data = {
            "interno": "1191484a-4ab1-4662-8c41-269fc1e66e23",
            "nome": "Outro nome 1",
        }
        super(TestOutroNomeInternoEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto inválido.
        """
        data = self.data
        data["interno"] = None
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto inválido.
        """
        data = self.data
        data["nome"] = ""
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_list(self):
        """
        List de objetos
        """

        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_d_update(self):
        """
        Atualizando objeto excluído.
        """

        data = self.data
        data["interno"] = "1191484a-4ab1-4662-8c41-269fc1e66e23"
        data["nome"] = "Outro nome 2"
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
            self.format_print(metodo="Update")

    def test_e_update(self):
        """
        Atualizando dados do objeto
        """

        data = self.data
        data["interno"] = "1191484a-4ab1-4662-8c41-269fc1e66e23"
        data["nome"] = "Atualização de Outro nome"
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["nome"] = "Outro nome 3"
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_f_delete(self):
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

    def test_g_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"4f7badd4-50e1-4a75-baf9-b5435f2b9a89"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.format_print(metodo="delete")
