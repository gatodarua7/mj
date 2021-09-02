from comum.tests.base import SiapenTestCase
from django.contrib.auth.models import User
from rest_framework import status
import json
import requests


class TestRgAdvogadoEndpoint(SiapenTestCase):
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
        "fixtures/social/religiao.json"

    ]
    def setUp(self) -> None:
        self.entidade = "RgAdvogado"
        self.url = f"/api/pessoas/rg-advogado/"
        self.data = {
            "numero": "3610441",
            "orgao_expedidor": "96637461-43cb-4d55-893b-c09fe514ebf7",
            "advogado": "29a09f2d-e1dd-43fa-9b3f-6f722c20b8c9"

        }
        super(TestRgAdvogadoEndpoint, self).setUp()

   
    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = requests.post(self.base_url+self.url, data=json.dumps(data), proxies=self.proxies, headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto inválido.
        """
        data = self.data
        data["numero"] = ""
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

    def test_a_update(self):
        """
        Atualizando objeto excluído.
        """

        data = self.data
        data["advogado"] = "29a09f2d-e1dd-43fa-9b3f-6f722c20b8c9"
        data["numero"] = "11111"
        data["orgao_expedidor"] = "96637461-43cb-4d55-893b-c09fe514ebf7"
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
        data["advogado"] = "29a09f2d-e1dd-43fa-9b3f-6f722c20b8c9"
        data["numero"] = "11111"
        data["orgao_expedidor"] = "96637461-43cb-4d55-893b-c09fe514ebf7"
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["numero"] = "222222"
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """

        data = self.data
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
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
