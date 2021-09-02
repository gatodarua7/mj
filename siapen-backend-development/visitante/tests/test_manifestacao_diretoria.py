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


class TestManifestacaoDiretoriaEndpoint(SiapenTestCase):
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
        "fixtures/visitante/manifestacao_diretoria.json"
    ]

    def setUp(self) -> None:
        self.entidade = "ManifestacaoDiretoria"
        self.url = f"/api/visitante/manifestacao-diretoria/"
        self.data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]
        }
        super(TestManifestacaoDiretoriaEndpoint, self).setUp()

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
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste",
            "documentos_list":  []
        }
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo='create')

    def test_c_create(self):
        """
        Criação de objeto invalido (sem campos obrigatorios).
        """
        data = {
            "visitante": None, 
            "parecer": "",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]
        }  
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


    def test_b_list(self):
        """
        List de com acento
        """

        url = f'{self.url}?search=téste'
        data = self.data 
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
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
        url = f'{self.url}?search=teste'
        data = self.data 
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
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
        url = f'{self.url}?ativo=true'
        data = self.data 
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos inativos
        """
        url = f'{self.url}?ativo=false'
        data = self.data 
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_f_list(self):
        """
        List de objetos inativos
        """
        url = f'{self.url}?ativo=101_RECEITAS'
        data = self.data 
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")


    def test_a_update(self):
        """
        Atualizando objeto excluído.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste Edição",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]
        }  
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_b_update(self):
        """
        Atualizando dados do objeto com outro usuario
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste Edição",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}],
            "usuario_cadastro": 1
        } 
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["parecer"] = "Teste edição outro usuario" 
            resp_json["usuario_cadastro"] = 2 
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")


    def test_a_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"4f7badd4-50e1-4a75-baf9-b5435f2b9a89"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="delete")

    
