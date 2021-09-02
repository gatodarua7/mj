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


class TestRecursoEndpoint(SiapenTestCase):
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
        "fixtures/visitante/documentos_visitante.json",
        "fixtures/vinculos/tipo_vinculo.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Recurso"
        self.url = f"/api/visitante/recurso/"
        self.data = {
            "observacao": "Teste",
            "data_recurso": "2020-01-01",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}],
            "usuario_cadastro": 1
        }
        super(TestRecursoEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data 
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto sem documento.
        """

        data = self.data
        data["documentos_list"] = []
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_c_create(self):
        """
        Criação de objeto invalido (sem campos obrigatorios).
        """
        data = self.data
        data["data_recurso"] = None 
        resp = self.client.post(self.url,data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")


    def test_a_update(self):
        """
        Atualizando objeto.
        """
        data = self.data
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            data["id"] = resp_json["id"]
            data["data_recurso"] = "2020-11-01"
            data["documentos_list"] = [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]
            resp = self.client.patch(url, data=json.dumps(data), content_type='application/json')
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="update")

    def test_a_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"4f7badd4-50e1-4a75-baf9-b5435f2b9a89"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    
