from comum.tests.base import SiapenTestCase
import requests
import json
from rest_framework import status
from typing import Optional


class TestFaccaoCargoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/estados.json",
        "fixtures/orcrim/faccao.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Facção_Cargo"
        self.url = f"/api/orcrim/faccao-cargo/"
        self.data = {
            "faccao": "967a3657-09fe-4e1b-83c8-f6d8cbd53a84",
            "nome": "CARGO 1",
            "observacao": "TESTE",
            "ativo": True,
        }
        super(TestFaccaoCargoEndpoint, self).setUp()

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
        Criação de objeto facção None.
        """
        data = self.data
        data["faccao"] = None
        data["nome"] = "CARGO 1"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto nome None.
        """
        data = self.data
        data["faccao"] = None
        data["nome"] = None
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto nome vazio.
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = ""
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de objeto nome None.
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = None
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        Lista os registros de facções.
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

    def test_g_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """
        url = f'{self.url}{"967a3657-09fe-4e1b-83c8-f6d8cbd53a84"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_h_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"0e648d25-5cda-4284-bce0-4e6227615dec"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_i_update(self):
        """
        Atualizando  Facção CARGO
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "CARGO 3"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            data = self.data
            data["id"] = resp_json["id"]
            data["faccao"] = "4e354096-0b68-4039-90d5-09267cbf1302"
            resp = self.client.patch(url, data=data)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_j_update(self):
        """
        Atualizando Facção CARGO excluído.
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "CARGO 4"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            data = self.data
            data["id"] = resp_json["id"]
            data["faccao"] = 4
            data["nome"] = "TESTE 4"
            resp = self.client.delete(url)
            data["nome"] = "TESTE 6"
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
            self.format_print(metodo="Update")

    def test_k_update(self):
        """
        Atualizando Facção CARGO para nome duplicado
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "CARGO 5"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["nome"] = "CARGO 5"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo="Update")

    def test_l_update(self):
        """
        Atualizando Facção CARGO inativa
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "CARGO 7"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["nome"] = "CARGO atu"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo="Update")

    def test_m_update(self):
        """
        Atualizando Facção CARGO para ativa
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "CARGO 8"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["nome"] = "CARGO atu 8"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo="Update")
