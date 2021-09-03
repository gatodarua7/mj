from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests


class TestFasesEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/cadastro/foto.json",
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
        "fixtures/movimentacao/pedido-inclusao.json",
    ]

    def setUp(self) -> None:
        self.entidade = "FasePedido"
        self.url = f"/api/movimentacao/fases-pedido/"
        self.emergencial = {
            "usuario_cadastro": 1,
            "nome": "INICIADO",
            "cor": "#77BAFAFF",
            "ordem": 1,
            "grupo": "EMERGENCIAL",
            "descricao": "Pedido de inclusão iniciado",
            "fase_inicial": True,
            "ultima_fase": False,
            "cgin": False,
        }
        self.definitivo = {
            "usuario_cadastro": 1,
            "nome": "INICIADO",
            "cor": "#77BAFAFF",
            "ordem": 1,
            "grupo": "DEFINITIVO",
            "descricao": "Pedido de inclusão iniciado",
            "fase_inicial": False,
            "fase": "CGIN",
        }
        super(TestFasesEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["nome"] = "Teste"
        fase_definitivo["fase"] = "ULTIMA_FASE"
        fase_definitivo["ultima_fase"] = "DEFERIDO"
        fase_definitivo["fase_inicial"] = False
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        fase_definitivo["ordem"] = len(res["results"]) + 1
        res["results"].append(fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto duplicado.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["fase_inicial"] = False
        fase_definitivo["fase"] = "ULTIMA_FASE"
        fase_definitivo["ultima_fase"] = "INDEFERIDO"
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        fase_definitivo["ordem"] = len(res["results"]) + 1
        res["results"].append(fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto em posição final sem ser ultima fase.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["nome"] = "Teste2"
        fase_definitivo["fase_inicial"] = False
        fase_definitivo["fase"] = "CGIN"
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        res["results"].append(fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto ultima fase e fase inicial.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["nome"] = "Teste3"
        fase_definitivo["fase_inicial"] = True
        fase_definitivo["fase"] = "ULTIMA_FASE"
        fase_definitivo["ultima_fase"] = "INDEFERIDO"
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        fase_definitivo["ordem"] = len(res["results"]) + 1
        res["results"].append(fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto CGIN apos uma ultima.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["nome"] = "Teste3"
        fase_definitivo["fase_inicial"] = True
        fase_definitivo["fase"] = "CGIN"
        fase_definitivo["ultima_fase"] = False
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        fase_definitivo["ordem"] = len(res["results"]) + 1
        res["results"].append(fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de objeto ulyima fase como intermediario.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["nome"] = "Teste4"
        fase_definitivo["fase_inicial"] = False
        fase_definitivo["fase"] = "ULTIMA_FASE"
        fase_definitivo["ultima_fase"] = "DEFERIDO"
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        fase_definitivo["ordem"] = len(res["results"]) + 1
        res["results"].insert(1, fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_g_create(self):
        """
        Criação de objeto  CGIN e Primeira Fase.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["nome"] = "TesteY"
        fase_definitivo["fase_inicial"] = True
        fase_definitivo["fase"] = "CGIN"
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        fase_definitivo["ordem"] = len(res["results"]) + 1
        res["results"].insert(3, fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_h_update(self):
        """
        Atualizando objeto duplicando fase.
        """
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        res["results"][2]["nome"] = "INICIADO"
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.format_print(metodo="update")

    def test_i_update(self):
        """
        Atualizando nome de Item
        """
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        res["results"][1]["nome"] = "LOFT"
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="update")

    def test_j_update(self):
        """
        Criação de objeto Fase inicial como ultima fase.
        """
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        res["results"][0]["fase"] = "ULTIMA_FASE"
        res["results"][0]["ultima_fase"] = "DEFERIDO"
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="update")

    def test_k_update(self):
        """
        Criação de objeto ultimafase e fase inicial.
        """
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        res["results"][-1]["fase_inicial"] = True
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="update")

    def test_l_update(self):
        """
        objeto ultimo item para nao ultima fase.
        """
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        res["results"][-1]["fase"] = "CGIN"
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="update")

    def test_m_create(self):
        """
        Criação de objeto válido não ultima fase.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["nome"] = "TesteX"
        fase_definitivo["fase_inicial"] = False
        fase_definitivo["fase"] = "ARQUIVAR"
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        fase_definitivo["ordem"] = len(res["results"]) + 1
        res["results"].insert(1, fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_n_delete(self):
        """
        Delete de objeto sem vinculo.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["nome"] = "Teste"
        fase_definitivo["fase"] = "ULTIMA_FASE"
        fase_definitivo["ultima_fase"] = "DEFERIDO"
        fase_definitivo["fase_inicial"] = False
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        fase_definitivo["ordem"] = len(res["results"]) + 1
        res["results"].append(fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            response = resp.json()
            id_fase = response[-1]["id"]
            url = f"{self.url}{id_fase}/"
            resp = self.client.delete(url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.format_print(metodo="delete")

    def test_o_delete(self):
        """
        Delete de objeto vinculado.
        """

        id_fase = "28c0c735-cd59-4229-8164-2019d47412c4"
        url = f"{self.url}{id_fase}/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        Get end point de grupos.
        """
        url = self.url + "grupos/"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="create")

    def test_b_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        List de com DEFINITIVO
        """

        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_c_list(self):
        """
        List Emergencial
        """
        url = f"{self.url}?grupo=EMERGENCIAL"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_d_list(self):
        """
        List de objetos inicial
        """
        url = f"{self.url}?movimentacao=inicial"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos final
        """
        url = f"{self.url}?movimentacao=final"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_q_create(self):
        """
        Criação de objeto inválido.
        """
        fase_definitivo = self.definitivo
        fase_definitivo["nome"] = "TesteEE"
        fase_definitivo["fase"] = "ULTIMA_FASE"
        fase_definitivo["fase_inicial"] = False
        url = f"{self.url}?grupo=DEFINITIVO"
        resp = self.client.get(url)
        res = resp.json()
        fase_definitivo["ordem"] = len(res["results"]) + 1
        res["results"].append(fase_definitivo)
        resp = self.client.post(
            self.url, data=json.dumps(res["results"]), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")
