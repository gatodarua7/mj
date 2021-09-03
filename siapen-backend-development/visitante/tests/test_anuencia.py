from comum.tests.base import SiapenTestCase
from django.contrib.auth.models import User
from rest_framework import status
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from visitante.models import DocumentosVisitante
from django.core.files.uploadedfile import InMemoryUploadedFile
import json
import requests


class TestAnuenciaEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/paises.json",
        "fixtures/cadastro/foto.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/raca.json",
        "fixtures/social/religiao.json",
        "fixtures/social/profissao.json",
        "fixtures/cadastro/genero.json",
        "fixtures/visitante/visitante.json",
        "fixtures/pessoas/interno.json",
        "fixtures/visitante/documentos_visitante.json",
        "fixtures/vinculos/tipo_vinculo.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Anuencia"
        self.url = f"/api/visitante/anuencia/"
        self.data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92",
            "interno": "1191484a-4ab1-4662-8c41-269fc1e66e23",
            "data_declaracao": "21/02/2021",
            "observacao": "teste",
            "tipo_vinculo": "816579b4-0c3b-4c2f-a6d5-97e1dbc36444",
            "documento": "07f4e25a-95c2-4c62-9c44-017f1be0696a",
        }
        super(TestAnuenciaEndpoint, self).setUp()

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
        Criação de objeto sem campos obrigatorios.
        """
        data = {
            "data_declaracao": "21/02/2021",
            "observacao": "teste",
            "tipo_vinculo": "816579b4-0c3b-4c2f-a6d5-97e1dbc36444",
            "documento": "07f4e25a-95c2-4c62-9c44-017f1be0696a",
        }
        self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto invalido sem documentos.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92",
            "interno": "1191484a-4ab1-4662-8c41-269fc1e66e23",
            "observacao": "teste",
            "tipo_vinculo": "816579b4-0c3b-4c2f-a6d5-97e1dbc36444",
        }
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto invalido sem data declaracao
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92",
            "interno": "1191484a-4ab1-4662-8c41-269fc1e66e23",
            "observacao": "teste",
            "tipo_vinculo": "816579b4-0c3b-4c2f-a6d5-97e1dbc36444",
            "documento": "07f4e25a-95c2-4c62-9c44-017f1be0696a",
        }
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
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
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f"{self.url}?search=Condomínio"
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_d_list(self):
        """
        List de objetos ativos
        """
        url = f"{self.url}?ativo=true"
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos por visitante
        """
        url = f"{self.url}?id_visitante=2939da1f-552d-4997-b8de-3d956359ec92"
        data = self.data
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_a_update(self):
        """
        Atualizando objeto sem dados obrigatorios.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92",
            "interno": "1191484a-4ab1-4662-8c41-269fc1e66e23",
            "data_declaracao": "21/02/2021",
            "observacao": "teste",
            "tipo_vinculo": "816579b4-0c3b-4c2f-a6d5-97e1dbc36444",
            "documento": "07f4e25a-95c2-4c62-9c44-017f1be0696a",
        }
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["visitante"] = None
            resp_json["interno"] = None
            resp = self.client.patch(
                url, data=json.dumps(resp_json), content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_b_update(self):
        """
        Atualizando dados do objeto sem interno
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92",
            "data_declaracao": "21/02/2021",
            "observacao": "teste",
            "tipo_vinculo": "816579b4-0c3b-4c2f-a6d5-97e1dbc36444",
            "documento": "07f4e25a-95c2-4c62-9c44-017f1be0696a",
        }
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["observacao"] = "Update"
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_a_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"4f7badd4-50e1-4a75-baf9-b5435f2b9a89"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.format_print(metodo="delete")
