from re import T
from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests
from typing import Optional
from datetime import datetime


class TestPessoaEndpoint(SiapenTestCase):
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
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/religiao.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Pessoa"
        self.url = f"/api/cadastros/pessoas/"
        self.data = {
            "nome": "Carlos Alexandre",
            "data_nascimento": "01/01/2000",
            "genero": "96637461-43cb-4d55-893b-c09fe514ecf7",
            "nacionalidade": 33,
            "naturalidade": 283,
            "estado": 29,
            "enderecos": [],
            "telefones": [],
            "foto": "",
            "cpf": "94875968019",
            "necessidade_especial": ["b83cb47a-dbdb-49e4-9ef7-34fcec39443f"],
        }
        super(TestPessoaEndpoint, self).setUp()

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
        data["nome"] = "Marcos Ramos"
        data["data_nascimento"] = "01/13/2001"
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
        data["nome"] = None
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = False
        data["mae_nao_declarado"] = False
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto com mae falecida.
        """
        data = self.data
        data["nome"] = "Leopoldo"
        data["mae_falecido"] = True
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de objeto inativo.
        """
        data = self.data
        data["nome"] = "Maria"
        data["ativo"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_f_create(self):
        """
        Criação de objeto com mae nao declarada.
        """
        data = self.data
        data["nome"] = "Mariah"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = []
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = []
        data["telefones"] = []
        data["ativo"] = True
        data["mae_falecido"] = False
        data["mae_nao_declarado"] = False
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_g_create(self):
        """
        Criação de pai falecido.
        """
        data = self.data
        data["nome"] = "Pedro"
        data["pai_falecido"] = True
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_h_create(self):
        """
        Criação de pai nao declarado.
        """
        data = self.data
        data["nome"] = "Joao"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = []
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = []
        data["telefones"] = []
        data["ativo"] = True
        data["mae_falecido"] = False
        data["mae_nao_declarado"] = False
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = True
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_i_create(self):
        """
        Criação de objeto com pai falecido e nao declarado.
        """
        data = self.data
        data["nome"] = "Jose"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = False
        data["mae_nao_declarado"] = False
        data["pai_falecido"] = True
        data["pai_nao_declarado"] = True
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_j_create(self):
        """
        Criação de objeto com mae falecida e nao declarada.
        """
        data = self.data
        data["nome"] = "Carol"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_k_create(self):
        """
        Criação de objeto cpf invalido.
        """
        data = self.data
        data["nome"] = "Carolyne"
        data["cpf"] = "66726786620"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_ka_create(self):
        """
        Criação de objeto cpf invalido.
        """
        data = self.data
        data["nome"] = "Caroline"
        data["cpf"] = "66726786622"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_l_create(self):
        """
        Criação de objeto com cpf invalido
        """
        data = self.data
        data["nome"] = "Clara"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = "048103729476"
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_m_create(self):
        """
        Criação de objeto com genero inextistente
        """
        data = self.data
        data["nome"] = "Ulisses"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = "42eaa97f-be62-4574-a71c-2b0dc5ad52e5"
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_n_create(self):
        """
        Criação de objeto com raca inexistente.
        """
        data = self.data
        data["nome"] = "Maria"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = "ce3edf88-c786-4c0f-ae1a-ac9ad6f5f0e7"
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_o_create(self):
        """
        Criação de objeto estado civil inexistente.
        """
        data = self.data
        data["nome"] = "Jailton"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = "80c4e4dc-5407-41a3-b74f-97dce02befb8"
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_p_create(self):
        """
        Criação de objeto com nacionalidade invalida.
        """
        data = self.data
        data["nome"] = "Silvana"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = 7904534
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_q_create(self):
        """
        Criação de objeto estado invalido.
        """
        data = self.data
        data["nome"] = "Pedrinho"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = 99999999
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_r_create(self):
        """
        Criação de objeto naturalidade invalida.
        """
        data = self.data
        data["nome"] = "Iris"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = 9272
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_s_create(self):
        """
        Criação de objeto grau_instrucao invalido.
        """
        data = self.data
        data["nome"] = "Isis"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = "37a26085-8566-4142-b3cb-14db2abca6a8"
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_t_create(self):
        """
        Criação de objeto Profissao.
        """
        data = self.data
        data["nome"] = "Stefany"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = "3a17fce8-451d-4338-b68b-794b22c73b94"
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_u_create(self):
        """
        Criação de objeto necessidade_especial.
        """
        data = self.data
        data["nome"] = "Joao Pedro"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = "7bb1e169-4031-43e4-baf3-76e9945ae342"
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_v_create(self):
        """
        Criação de objeto orientacao_sexual invalida.
        """
        data = self.data
        data["nome"] = "Lucas"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = "ee77a163-bfc7-4fca-a34b-da90ef2c552e"
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_x_create(self):
        """
        Criação de objeto religiao invalida.
        """
        data = self.data
        data["nome"] = "Luis"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = "f8903630-e917-4507-b784-727c30f84d9f"
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_y_create(self):
        """
        Criação de objeto enderecos invalidos.
        """
        data = self.data
        data["nome"] = "Manuela"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = 456456
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_w_create(self):
        """
        Criação de objeto telefones.
        """
        data = self.data
        data["nome"] = "Manuel"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = None
        data["estado"] = None
        data["naturalidade"] = None
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = 34534534
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_z_create(self):
        """
        Criação de objeto de uma cidade no estado em outro.
        """
        data = self.data
        data["nome"] = "Erondina"
        data["nome_social"] = None
        data["data_nascimento"] = None
        data["cpf"] = None
        data["rg"] = None
        data["orgao_expedidor"] = None
        data["genero"] = None
        data["raca"] = None
        data["estado_civil"] = None
        data["nacionalidade"] = 33
        data["estado"] = 28
        data["naturalidade"] = 756
        data["nome_mae"] = None
        data["nome_pai"] = None
        data["grau_instrucao"] = None
        data["profissao"] = None
        data["necessidade_especial"] = None
        data["orientacao_sexual"] = None
        data["religiao"] = None
        data["enderecos"] = None
        data["telefones"] = None
        data["ativo"] = True
        data["mae_falecido"] = True
        data["mae_nao_declarado"] = True
        data["pai_falecido"] = False
        data["pai_nao_declarado"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_f_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """
        data = self.data
        data["nome"] = "Nelma"
        resp = self.client.post(
            self.url, data=json.dumps(self.data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_b_delete(self):
        """
        Apagando registro excluido inexistente.
        """
        url = f"{self.url}32807f7f-8684-47b5-a7db-728c54d82012/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_c_delete(self):
        """
        Apagando registro ja excluído.
        """
        url = f"{self.url}cc6113d2-a267-4bf1-9101-1004199c3a5a/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_a_update(self):
        """
        Atualizando objeto excluído.
        """

        data = self.data
        data["nome"] = "Yasmin"
        data["data_nascimento"] = None
        resp = self.client.post(
            self.url, data=json.dumps(self.data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_b_update(self):
        """
        Atualizando nome do objeto
        """
        data = self.data
        data["nome"] = "Glaucia"
        resp = self.client.post(
            self.url, data=json.dumps(self.data), content_type="application/json"
        )

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["nome"] = "Teresinha"
            resp = self.client.patch(
                url, data=json.dumps(resp_json), content_type="application/json"
            )
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_c_update(self):
        """
        Atualizando descricao do objeto inativo.
        """
        data = self.data
        data["nome"] = "Geyce"
        data["ativo"] = False
        resp = self.client.post(
            self.url, data=json.dumps(self.data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["nome"] = "Caroline"
            resp_json["ativo"] = False
            resp = self.client.patch(
                url, data=json.dumps(resp_json), content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_d_update(self):
        """
        Atualizando cpf do objeto para valor invalido.
        """
        data = self.data
        data["nome"] = "Greyce"
        data["cpf"] = "25134280305"
        resp = self.client.post(
            self.url, data=json.dumps(self.data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["cpf"] = "11111111111"
            resp = self.client.patch(
                url, data=json.dumps(resp_json), content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_e_update(self):
        """
        Atualizando data de nascimento para valor invalido.
        """
        data = self.data
        data["nome"] = "Gleicene"
        data["data_nascimento"] = "2999-05-01"
        resp = self.client.post(
            self.url, data=json.dumps(self.data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["data_nascimento"] = "2999-15-14"
            resp = self.client.patch(
                url, data=json.dumps(resp_json), content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")
