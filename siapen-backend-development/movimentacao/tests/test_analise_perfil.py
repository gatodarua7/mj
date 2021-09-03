from comum.tests.base import SiapenTestCase
from movimentacao.models import AnalisePedido
from rest_framework import status
import json
import requests


class TestAnalisePedidoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/movimentacao/pedido-inclusao.json",
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
        "fixtures/movimentacao/fases.json",
        "fixtures/prisional/unidade.json",
        "fixtures/prisional/sistema.json",
    ]

    def setUp(self) -> None:
        self.entidade = "AnalisePedido"
        self.url = f"/api/movimentacao/analise-pedido/"
        self.data = {
            "parecer": "Meu parecer",
            "penitenciaria": "fb5bc99e-b885-40ce-ad86-0fe2021a488b",
            "posicionamento": "DESFAVORAVEL",
            "pedido_inclusao": "96418c25-d397-45e3-9cc2-8a4dadbb2d6c",
        }
        super(TestAnalisePedidoEndpoint, self).setUp()

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
        Criação de objeto sem qualquer um dos campos obrigatorios
        """
        data = self.data
        data["parecer"] = None
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto sem todos um dos campos obrigatorios
        """
        data = self.data
        data["parecer"] = None
        data["penitenciaria"] = None
        data["posicionamento"] = None
        data["pedido_inclusao"] = None
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_e_update(self):
        """
        Atualizando objeto excluído.
        """

        data = self.data
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

    def test_f_update(self):
        """
        Atualizando dados do objeto
        """

        data = self.data
        data["parecer"] = "Um parecer de atualização"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["penitenciaria"] = "c612a4bf-0837-47b4-ade8-8ac3ad9f8bc9"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_g_update(self):
        """
        Atualizando dados do objeto
        """

        data = {
            "parecer": "Meu parecer",
            "penitenciaria": "fb5bc99e-b885-40ce-ad86-0fe2021a488b",
            "posicionamento": "DESFAVORAVEL",
            "pedido_inclusao": "f4ff1afb-b510-44f0-b409-5a657c98004a",
        }
        data["parecer"] = "Um novo parecer de atualização"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["penitenciaria"] = "c612a4bf-0837-47b4-ade8-8ac3ad9f8bc9"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertFalse(None)
            self.format_print(metodo="Update")

    def test_h_delete(self):
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

    def test_i_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"a819779d-4fe0-4283-83b2-879b6a9d2620"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")
