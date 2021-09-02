from re import T
from comum.tests.base import SiapenTestCase
from rest_framework import status
from datetime import datetime
import json
import requests

ENDERECO = [{
                "logradouro":"Rua Beraldo de Oliveira",
                "numero":"99",
                "bairro":"Mangabeira",
                "cidade":2596,
                "estado":25,
                "cep":"58.056-510",
                "observacao":"teste",
                "andar":"1",
                "sala":"101",
                "complemento":"AP"
            }]

TELEFONE=[{"numero": "9988888888", 
            "tipo": "ramal", 
            "observacao": "testes", 
            "andar":"1", 
            "sala":"101"},
            {"numero": "123", 
            "tipo": "ramal", 
            "observacao": "ok", 
            "andar":"1",
             "sala":"101"}]

class TestSetorEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
    ]
    def setUp(self) -> None:
        self.entidade = 'Setor'
        self.url = f"/api/cadastros/setor/"
        self.data = {"enderecos": ENDERECO, 
                    "telefones": TELEFONE, 
                    "nome": "SETOR A",  
                    "sigla": "SA", 
                    "ativo": True
                    }
        self.now = datetime.now()
        super(TestSetorEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

    def test_b_create(self):
        """
        Criação de objeto vazio.
        """
        data = {"setor_pai": "", "enderecos": "", "telefones": "", "nome": "",  "sigla": "", "ativo": ""}
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')
    
    def test_d_create(self):
        """
        Criação de objeto com setor pai excluido.
        """
        data = self.data
        data['setor_pai'] = "41bd73c5-ff97-44dd-b2a5-c954da886567"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_e_create(self):
        """
        Criação de objeto com nome vazio.
        """
        data = self.data
        data['nome'] = ""
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_f_create(self):
        """
        Criação de objeto sem nome.
        """
        data = self.data
        data['nome'] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_g_create(self):
        """
        Criação de objeto sem telefone.
        """
        data = self.data
        data['nome'] = "SETOR B"
        data['telefones'] = []
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

    def test_h_create(self):
        """
        Criação de objeto com telefone em formato string.
        """
        data = self.data
        data['nome'] = "SETOR C"
        data['telefones'] = ""
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

    def test_i_create(self):
        """
        Criação de objeto sem sigla.
        """
        data = self.data
        data['nome'] = "SETOR D"
        data['sigla'] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

    def test_k_create(self):
        """
        Criação de objeto com setor pai inativo.
        """
        data = self.data
        data['setor_pai'] = "4b40ac84-2476-47d1-8193-c6110540d514"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_l_create(self):
        """
        Criação de objeto com setor pai inativo.
        """
        data = self.data
        data['nome'] = "CREATE SETOR PAI INEXISTENTE"
        data['setor_pai'] = "1fcaa5b1-aadf-428b-bb69-c7c4588145dc"
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

    def test_b_list(self):
        """
        List por id.
        """
        url = f'{self.url}?search=f70266ac-74ea-4494-bd75-3fed4dd05848'
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """

        data = self.data
        data['nome'] = "SETOR EXCLUIR"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")
    
    def test_b_delete(self):
        """
        Validando o processo de remoção de registro já excluidp.
        """
        url = f"{self.url}41bd73c5-ff97-44dd-b2a5-c954da886567/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.format_print(metodo="delete")

    def test_c_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """
        data = self.data
        data['setor_pai'] = "f70266ac-74ea-4494-bd75-3fed4dd05848"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")
    
    def test_a_update(self):
        """
        Atualizando o nome do setor.
        """
        data = self.data
        data['nome'] = "SETOR BD"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'  
            resp_json['nome'] = "SETOR BD2"
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_b_update(self):
        """
        Definindo setor pai igual a setor atual.
        """
        data = self.data
        data['nome'] = "SETOR BD3"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'  
            resp_json['setor_pai'] = resp_json['id']
            resp_json['nome'] = "SETOR ATUALIZADO"
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo='Update')

    def test_c_update(self):
        """
        Atualizando o setor pai.
        """
        data = self.data
        data['setor_pai'] = "0b057129-4fcf-475b-a462-e2a71ea8dc87"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json['setor_pai'] = "f70266ac-74ea-4494-bd75-3fed4dd05848"
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo='Update')

    def test_1_update(self):
        """
        Atualizando a setor pai para valor inexistente.
        """

        data = self.data
        data['nome'] = "SETOR PAI INEXISTENTE"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json['setor_pai'] = "de87b677-b6f6-4110-b69a-46d827652f67"
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo='Update')

    def test_f_update(self):
        """
        Atualizando a lista de telefones.
        """
        data = self.data
        data['sigla'] = "TEL"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json['telefpnes'] = [{"numero": "999", "tipo": "ramal", "observacao": "ok", "andar":"1", "sala":"101"}]
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.format_print(metodo='Update')

    def test_g_update(self):
        """
        Atualizando a sigla.
        """
        data = self.data
        data['sigla'] = "ABCD"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json['sigla'] = "DABC"
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.format_print(metodo='Update')

    def test_h_update(self):
        """
        Atualizando para duplicado
        """
        data = self.data
        data['nome'] = "SETOR PARA DUPLICAR"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json['nome'] = "SETOR A"
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.format_print(metodo='Update')
    
    def test_i_update(self):
        """
        Inativando registro
        """
        data = self.data
        data['nome'] = "SETOR PARA INATIVAR"
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json['ativo'] = False
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.format_print(metodo='Update')
    
    def test_j_update(self):
        """
        Atualizando registro Inativo
        """
        data = self.data
        data['nome'] = "SETOR INATIVO"
        data['ativo'] = False
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=json.dumps(resp_json), content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo='Update')

    def test_l_list(self):
        """
        list hierarquia de setor excluido.
        """
        url = f'{self.url}treeview-setor/{"41bd73c5-ff97-44dd-b2a5-c954da886567"}'
        resp = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")


    def test_e_list(self):
        """
        list hierarquia de setor inexistente.
        """
        url = f'{self.url}treeview-setor/{"1fcaa5b1-aadf-428b-bb69-c7c4588145dc"}'
        resp = self.client.get(url)
        self.assertFalse(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_d_list(self):
        """
        list hierarquia de setor.
        """
        id = "f70266ac-74ea-4494-bd75-3fed4dd05848"
        url = f'{self.url}treeview-setor/{id}'
        resp = self.client.get(url)
        self.assertFalse(status.is_success(resp.status_code))
        self.format_print(metodo='list')
    
    def test_c_list(self):
        """
        list treeview de setor.
        """

        url = f'{self.url}setor-alocacao/'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo='list')
    
