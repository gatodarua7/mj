from comum.tests.base import SiapenTestCase
from django.contrib.auth.models import User
from ..models import Manifestacao
from rest_framework import status
import json
import requests


class TestVisitanteMovimentacaoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/estados.json",
        "fixtures/visitante/visitante.json",
        "fixtures/visitante/visitante.json",
        "fixtures/cadastro/foto.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/cadastro/genero.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/religiao.json"
    ]

    def setUp(self) -> None:
        self.entidade = "VisitanteMovimentacao"
        self.url = f"/api/visitante/movimentacao/"
        self.data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92",      
            "fase" : "SOLICITANTE_INFORMADO",
            "motivo": "teste",
            "data_contato": "11/08/2021",
            "usuario_cadastro": 1
        }
        super(TestVisitanteMovimentacaoEndpoint, self).setUp()


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
        Movimenta para a fase ANALISE_INTELIGENCIA sem ter manifestacao cadastrada.
        """
        data = self.data
        data["fase"] = "ANALISE_INTELIGENCIA"
        self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')


    def test_c_create(self):
        """
        Criação de fase ANALISE_INTELIGENCIA com manifestação cadastrada.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]   
        }
        entidade = "Manifestacao"
        url = f"/api/visitante/manifestacao/"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            data = self.data
            data["fase"] = "ANALISE_INTELIGENCIA"
            resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            self.format_print(metodo='create')

    def test_d_create(self):
        """
        Movimenta da ANALISE_INTELIGENCIA para ANALISE_DIRETORIA.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]   
        }
        entidade = "Manifestacao"
        url = f"/api/visitante/manifestacao/"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            data = self.data
            data["fase"] = "ANALISE_INTELIGENCIA"
            resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                url = f'{self.url}{resp_json["id"]}/'
                resp_json["fase"] = "ANALISE_DIRETORIA" 
                resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
                self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
                self.format_print(metodo='create')

    def test_e_create(self):
        """
        Movimenta da ANALISE_INTELIGENCIA para ASSISTENCIA_SOCIAL.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]   
        }
        entidade = "Manifestacao"
        url = f"/api/visitante/manifestacao/"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            data = self.data
            data["fase"] = "ANALISE_INTELIGENCIA"
            resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                url = f'{self.url}{resp_json["id"]}/'
                resp_json["fase"] = "ASSISTENCIA_SOCIAL" 
                resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
                self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
                self.format_print(metodo='create')

    def test_f_create(self):
        """
        Movimenta da ANALISE_INTELIGENCIA para DEFERIDO.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]   
        }
        entidade = "Manifestacao"
        url = f"/api/visitante/manifestacao/"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            data = self.data
            data["fase"] = "ANALISE_INTELIGENCIA"
            resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                url = f'{self.url}{resp_json["id"]}/'
                resp_json["fase"] = "DEFERIDO" 
                resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
                self.format_print(metodo='create')

    def test_g_create(self):
        """
        Movimenta da ANALISE_INTELIGENCIA para INDEFERIDO.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]   
        }
        entidade = "Manifestacao"
        url = f"/api/visitante/manifestacao/"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            data = self.data
            data["fase"] = "ANALISE_INTELIGENCIA"
            resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                url = f'{self.url}{resp_json["id"]}/'
                resp_json["fase"] = "INDEFERIDO" 
                resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
                self.format_print(metodo='create')

    def test_h_create(self):
        """
        Movimenta da ASSISTENCIA_SOCIAL para DEFERIDO.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]   
        }
        entidade = "Manifestacao"
        url = f"/api/visitante/manifestacao/"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            data = self.data
            data["fase"] = "ASSISTENCIA_SOCIAL"
            resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                url = f'{self.url}{resp_json["id"]}/'
                resp_json["fase"] = "DEFERIDO" 
                resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
                self.format_print(metodo='create')

    def test_i_create(self):
        """
        Movimenta da ASSISTENCIA_SOCIAL para INDEFERIDO.
        """
        data = {
            "visitante": "2939da1f-552d-4997-b8de-3d956359ec92", 
            "parecer": "Teste",
            "documentos_list":  [{"id":"07f4e25a-95c2-4c62-9c44-017f1be0696a"}]   
        }
        entidade = "Manifestacao"
        url = f"/api/visitante/manifestacao/"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            data = self.data
            data["fase"] = "ASSISTENCIA_SOCIAL"
            resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                url = f'{self.url}{resp_json["id"]}/'
                resp_json["fase"] = "INDEFERIDO" 
                resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
                self.format_print(metodo='create')

    def test_j_create(self):
        """
        Movimenta para a fase RECURSO.
        """
        data = {
            "nome": "João da Silva", 
            "cpf": "23973947074",
            "foto": "15764e55-46a8-49ee-aa3e-56152dcb0c65",
            "data_nascimento": "21/02/1990",
            "idade": 30,
            "numero_sei": "11111.111111/1111-11",
            "telefones": [],
            "enderecos": [],
            "nacionalidade": [1],
            "situacao": False,
            "necessidade_especial": ["cc4c334e-7ab4-47fd-8a57-73c21dcda178"],  
            "anuencias": [],
            "fase": "INDEFERIDO" 
        }
        entidade = "Visitante"
        url = f"/api/visitante/visitante/"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            data = self.data
            data["fase"] = "SOLICITANTE_INFORMADO"
            resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                url = f'{self.url}{resp_json["id"]}/'
                resp_json["fase"] = "RECURSO" 
                resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
                self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
                self.format_print(metodo='create')


    def test_k_create(self):
        """
        Movimenta para a fase RECURSO sem o visitante estar na fase SOLICITANTE_INFORMADO.
        """
        data = {
            "nome": "João da Silva", 
            "cpf": "23973947074",
            "foto": "15764e55-46a8-49ee-aa3e-56152dcb0c65",
            "data_nascimento": "21/02/1990",
            "idade": 30,
            "numero_sei": "11111.111111/1111-11",
            "telefones": [],
            "enderecos": [],
            "nacionalidade": [1],
            "situacao": False,
            "necessidade_especial": ["cc4c334e-7ab4-47fd-8a57-73c21dcda178"],  
            "anuencias": [],
            "fase": "INICIADO" 
        }
        entidade = "Visitante"
        url = f"/api/visitante/visitante/"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            data = self.data
            data["fase"] = "SOLICITANTE_INFORMADO"
            resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                url = f'{self.url}{resp_json["id"]}/'
                resp_json["fase"] = "RECURSO" 
                resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
                self.format_print(metodo='create')

    def test_a_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")


    def test_a_update(self):
        """
        Atualizando de SOLICITANTE_INFORMADO para DEFERIDO.
        """
        data = self.data
        data["fase"] = ["SOLICITANTE_INFORMADO"]
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["fase"] = "DEFERIDO"
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            self.format_print(metodo="update")


    def test_a_delete(self):
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

    def test_b_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"4f7badd4-50e1-4a75-baf9-b5435f2b9a89"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")
    
