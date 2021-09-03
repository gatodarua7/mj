from comum.tests.base import SiapenTestCase
import requests
import json
from rest_framework import status
from typing import Optional


class TestFaccaoGrupoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/estados.json",
        "fixtures/orcrim/faccao.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Facção_Grupo"
        self.url = f"/api/orcrim/faccao-grupo/"
        self.data = {
            "faccao": "967a3657-09fe-4e1b-83c8-f6d8cbd53a84",
            "nome": "CV DO AM",
            "observacao": "TESTE",
            "ativo": True,
        }
        super(TestFaccaoGrupoEndpoint, self).setUp()

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
        data["nome"] = "TESTE"
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
        url = f'{self.url}{"dff28324-2bbe-4e06-bf9d-3aca90d4f56f"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_i_update(self):
        """
        Atualizando  Facção Grupo
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "TESTE 3"
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
            data["nome"] = "TESTE 3"
            resp = self.client.patch(url, data=data)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_j_update(self):
        """
        Atualizando Facção Grupo excluído.
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "TESTE 4"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            id = resp_json["id"]
            url = f'{self.url}{"967a3657-09fe-4e1b-83c8-f6d8cbd53a84"}/'
            resp = self.client.delete(url)
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo="Update")

    def test_k_update(self):
        """
        Atualizando Facção Grupo para nome existente
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "TESTE 5"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["nome"] = "CV DO AM"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo="Update")

    def test_l_update(self):
        """
        Atualizando Facção Grupo inativa
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "TESTE 7"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["nome"] = "TESTE5 atu"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo="Update")

    def test_m_update(self):
        """
        Atualizando Facção Grupo para ativa
        """
        data = self.data
        data["faccao"] = "967a3657-09fe-4e1b-83c8-f6d8cbd53a84"
        data["nome"] = "TESTE 8"
        data["observacao"] = "TESTE"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["nome"] = "TESTE5 atu 8"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo="Update")
