from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests


class TestNormaJuridicaEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/juridico/normas-juridicas.json",
        "fixtures/juridico/titulo-lei.json",
    ]

    def setUp(self) -> None:
        self.entidade = "NormaJuridica"
        self.url = f"/api/juridico/norma-juridica/"
        self.data = {
            "titulo": "568f98d3-a883-4b7d-8485-a138c5432264",
            "norma_juridica": "LEI_COMPLEMENTAR",
            "descricao": "Norma teste",
        }
        super(TestNormaJuridicaEndpoint, self).setUp()

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

    def test_c_create(self):
        """
        Criação de objeto nulo.
        """
        data = self.data
        data["nome"] = None
        data["norma_juridica"] = None
        data["descricao"] = None
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de norma jurídica com valor inválido
        """
        data = self.data
        data["nome"] = "teste"
        data["norma_juridica"] = "568f98d3-a883-4b7d-8485-a138c5432264"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_e_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_f_update(self):
        """
        Atualizando objeto excluído.
        """

        data = self.data
        data["nome"] = "Carta Magna"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            resp = self.client.patch(
                url, data=json.dumps(resp_json), content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_g_update(self):
        """
        Atualizando nome do objeto
        """

        data = self.data
        data["nome"] = "Atualização de nome"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Finha"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(
                url, data=json.dumps(resp_json), content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.format_print(metodo="Update")

    def test_h_update(self):
        """
        Atualizando nome do objeto inativo.
        """

        data = self.data
        data["nome"] = "Lei inativada"
        data["ativo"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(
                url, data=json.dumps(resp_json), content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_i_update(self):
        """
        Atualizando norma juridica para valor invalido.
        """

        data = self.data
        data["norma_juridica"] = "568f98d3-a883-4b7d-8485-a138c5432264"
        data["nome"] = "DECRETO_LEGISLATIVO"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["norma_juridica"] = "Decreto Leg."
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(
                url, data=json.dumps(resp_json), content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_j_delete(self):
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

    def test_k_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"015039e9-082f-48dc-8c28-ca018ff44c8c"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")
