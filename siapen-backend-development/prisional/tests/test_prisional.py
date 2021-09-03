from comum.tests.base import SiapenTestCase
import requests
import json
from rest_framework import status


class TestPrisionalEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/estados.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/prisional/sistema.json",
        "fixtures/prisional/unidade.json",
        "fixtures/prisional/bloco.json",
        "fixtures/prisional/cela.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Prisional"
        super(TestPrisionalEndpoint, self).setUp()

    def list_bloco(self, id=None):
        """
        Efetua a listagem de dados da API.
        """
        url = (
            f"/api/prisional/bloco-alocacao/"
            if not id
            else f"/api/prisional/treeview-bloco/{id}"
        )
        response = self.client.get(url, follow=True)
        return response

    def list_cela(self, id=None):
        """
        Efetua a listagem de dados da API.
        """
        url = (
            f"/api/prisional/cela-alocacao/"
            if not id
            else f"/api/prisional/treeview-cela/{id}"
        )
        response = self.client.get(url, follow=True)
        return response

    def list_setor(self, id=None):
        """
        Efetua a listagem de dados da API.
        """
        url = (
            f"/api/prisional/setor-alocacao/"
            if not id
            else f"/api/prisional/treeview-setor/{id}"
        )
        response = self.client.get(url, follow=True)
        return response

    def test_a_list(self):
        """
        list treeview de bloco.
        """
        resp = self.list_bloco()
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        list treeview de cela.
        """
        resp = self.list_cela()
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_d_list(self):
        """
        list hierarquia de bloco.
        """
        resp = self.list_bloco("3bb870cd-4219-4799-a2f6-67e5396382e5")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="list")

    def test_e_list(self):
        """
        list hierarquia de cela.
        """
        resp = self.list_cela("8daa2753-4a87-4d40-ab8d-4ffdc2706f19")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="list")

    def test_g_list(self):
        """
        list hierarquia de bloco inexistente.
        """
        resp = self.list_bloco("5e0d66b2-7a97-4fb5-88cc-0ae41472b7aa")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="list")

    def test_h_list(self):
        """
        list hierarquia de cela inexistente.
        """
        resp = self.list_cela("736576a6-eaa6-453e-a826-fd3ee0ef5923")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="list")

    def test_j_list(self):
        """
        list hierarquia de bloco excluido.
        """
        resp = self.list_bloco("281bba94-19a4-4684-b5e1-2811f8c00b04")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="list")

    def test_k_list(self):
        """
        list hierarquia de cela excluido.
        """
        resp = self.list_cela("527f5895-c02e-410d-b9f9-280e0ef437c7")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="list")
