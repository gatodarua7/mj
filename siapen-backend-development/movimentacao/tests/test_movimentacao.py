from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests


class TestPedidoInclusaoMovimentacaoEndpoint(SiapenTestCase):
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
        self.entidade = "PedidoInclusaoMovimentacao"
        self.url = f"/api/movimentacao/pedido-movimentacao/"
        self.data = {
            "pedido_inclusao": "f4ff1afb-b510-44f0-b409-5a657c98004a",
            "fase_pedido": "ba20d3be-98a1-4cef-bc84-0fd5eb938eb3",
            "motivo": "Teste",
            "usuario_cadastro": 1,
        }
        super(TestPedidoInclusaoMovimentacaoEndpoint, self).setUp()

    def test_a_create(self):
        """
        Movimentatar para ultima fase sem requisitos
        """
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_aa_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        data["fase_pedido"] = "eea4d74d-4753-45f7-a6b6-921251c8af58"

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
        data["fase_pedido"] = None
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
        data["fase_pedido"] = None
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

    def test_e_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_f_list(self):
        """
        List de objetos
        """
        url = (
            self.url
            + "?page_size=10000&ativo=true&ordering=-created_at&pedido_inclusao=0afdff24-e1d5-401b-a4f3-639fb3236c0e"
        )
        resp = self.client.get(url)
        resp_json = resp.json()
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_e_update(self):
        """
        Atualizando dados do objeto
        """

        data = self.data
        data["motivo"] = "Um parecer de atualização"
        data["fase_pedido"] = "eea4d74d-4753-45f7-a6b6-921251c8af58"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["motivo"] = "Testeando"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")
