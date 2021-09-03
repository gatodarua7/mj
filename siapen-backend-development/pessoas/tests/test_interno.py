from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests
from typing import Optional
from datetime import datetime


class TestInternoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/cadastro/foto.json",
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/cadastro/genero.json",
        "fixtures/cadastro/orgao_expedidor.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/profissao.json",
        "fixtures/social/religiao.json",
        "fixtures/social/raca.json",
        "fixtures/pessoas/interno.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Interno"
        self.url = f"/api/pessoas/interno/"
        self.data = {
            "nome": "Carlos Leopoldo",
            "nome_social": "Leopoldo",
            "foto": None,
            "cpf": "15797187019",
            "orgao_expedidor": None,
            "genero": "96637461-43cb-4d55-893b-c09fe514ecf7",
            "raca": None,
            "estado_civil": "3c2c263e-0713-4bf1-a707-903fe601e6ae",
            "nacionalidade": [1],
            "estado": None,
            "naturalidade": None,
            "nome_mae": "MARIA",
            "nome_pai": "JOSE",
            "grau_instrucao": "a414408d-aee8-44a7-b513-f7084fde2beb",
            "profissao": None,
            "necessidade_especial": ["b83cb47a-dbdb-49e4-9ef7-34fcec39443f"],
            "orientacao_sexual": "fd9341f3-4c70-43a2-9e12-1e2da2d0ae4e",
            "religiao": "1c063b46-2b96-41a9-831d-4fed804ae05e",
            "data_nascimento": "01/01/2000",
            "mae_falecido": False,
            "mae_nao_declarado": False,
            "pai_falecido": False,
            "pai_nao_declarado": False,
            "documentos": [],
            "caracteristicas_cutis": "BRANCA",
            "caracteristicas_cor_cabelo": "PRETO",
            "caracteristicas_tipo_cabelo": "LISO",
            "caracteristicas_tipo_rosto": "ACHATADO",
            "caracteristicas_tipo_testa": "ALTA",
            "caracteristicas_tipo_olhos": "FUNDOS",
            "caracteristicas_cor_olhos": "PRETOS",
            "caracteristicas_nariz": "ACHATADO",
            "caracteristicas_labios": "FINOS",
            "caracteristicas_compleicao": "GORDA",
            "caracteristicas_sobrancelhas": "APARADAS",
            "caracteristicas_orelhas": "GRANDES",
        }
        super(TestInternoEndpoint, self).setUp()

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
        Criação de objeto com data invalida.
        """
        data = self.data
        data["nome"] = "JOSE"
        data["cpf"] = "93945356083"
        data["data_nascimento"] = "42/13/2001"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto com campos obrigatórios nao enviados.
        """
        data = self.data
        data["cpf"] = ""
        data["data_nascimento"] = ""
        data["nome"] = ""
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto com pai falecido e nao declarado.
        """
        data = self.data
        data["cpf"] = "93780825058"
        data["pai_falecido"] = True
        data["pai_nao_declarado"] = True
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de objeto com mae falecida e nao declarada.
        """
        data = self.data
        data["cpf"] = "11932591001"
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_f_create(self):
        """
        Criação de objeto cpf invalido.
        """
        data = self.data
        data["cpf"] = "11111111111"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_g_create(self):
        """
        Criação de objeto de uma cidade no estado em outro.
        """

        data = self.data
        data["cpf"] = "81787043070"
        data["nacionalidade"] = [33]
        data["estado"] = 28
        data["naturalidade"] = 12
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_h_create(self):
        """
        Criação de objeto duplicado.
        """
        data = self.data
        data["cpf"] = "15797187019"
        resp = self.client.post(self.url, data=data, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        List de com acento
        """

        url = f"{self.url}?search=Condominio"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f"{self.url}?search=Jose"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_d_list(self):
        """
        List de objetos ativos
        """
        url = f"{self.url}?ativo=true"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos inativos
        """
        url = f"{self.url}?ativo=false"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_a_update(self):
        """
        Atualizando objeto excluído.
        """

        data = self.data
        data["cpf"] = "76081278050"
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

    def test_b_update(self):
        """
        Atualizando nome do objeto
        """

        data = self.data
        data["cpf"] = "98646233030"
        resp = self.client.post(self.url, data=data, content_type="application/json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Finha"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_c_update(self):
        """
        Atualizando cpf do objeto para valor invalido.
        """

        data = self.data
        data["cpf"] = "62508348007"
        resp = self.client.post(self.url, data=data, content_type="application/json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["cpf"] = "11111111111"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_d_update(self):
        """
        Atualizando data de nascimento para menor de 18 anos
        """

        data = self.data
        data["cpf"] = "45183106088"
        resp = self.client.post(self.url, data=data, content_type="application/json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["data_nascimento"] = "21-09-2020"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")
