from comum.tests.base import SiapenTestCase
from django.contrib.auth.models import User
from rest_framework import status
import json
import requests


class TestOutroNomeEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/movimentacao/pedido-inclusao.json",
        "fixtures/movimentacao/fases.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/cadastro/genero.json",
        "fixtures/cadastro/regime_prisional.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/religiao.json",
    ]

    def setUp(self) -> None:
        self.entidade = "PedidoInclusaoOutroNome"
        self.url = f"/api/movimentacao/outro-nome/"
        self.data = {
            "pedido_inclusao": "0afdff24-e1d5-401b-a4f3-639fb3236c0e",
            "nome": "Outro nome 1",
        }
        super(TestOutroNomeEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto inválido.
        """
        data = self.data
        data["pedido_inclusao"] = None
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto inválido.
        """
        data = self.data
        data["nome"] = ""
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
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
        data["pedido_inclusao"] = "0afdff24-e1d5-401b-a4f3-639fb3236c0e"
        data["nome"] = "Outro nome 2"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
            self.format_print(metodo="Update")

    def test_e_update(self):
        """
        Atualizando dados do objeto
        """

        data = self.data
        data["pedido_inclusao"] = "0afdff24-e1d5-401b-a4f3-639fb3236c0e"
        data["nome"] = "Atualização de Outro nome"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Outro nome 3"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
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
        url = f'{self.url}{"015039e9-082f-48dc-8c28-ca018ff44c8c"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")
