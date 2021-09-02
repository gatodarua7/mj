from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests
from typing import Optional


class TestFaccaoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/estados.json",
        "fixtures/orcrim/faccao.json",
    ]

    def setUp(self) -> None:
        self.entidade = 'Facção'
        self.url = f'/api/orcrim/faccao/'
        self.data = {
            "nome":"PRIMEIRA FAÇAO", 
            "sigla": "PFS", 
            "pais":[2], 
            "estado":[],
            "ativo": True, 
            "observacao":""
        }
        super(TestFaccaoEndpoint, self).setUp()

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
        Criação de objeto sem nome.
        """
        data = self.data
        data["nome"] = ""
        data["sigla"]= "PFS2"
        data["pais"] = [33]
        data["estado"] = [28]
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_c_create(self):
        """
        Criação de objeto sem sigla.
        """
        data = self.data
        data["nome"] = "Segunda Facção"
        data["sigla"]= ""
        data["pais"] = [33]
        data["estado"] = [28]
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_d_create(self):
        """
        Criação de objeto fora do país e sem estado.
        """
        data = self.data
        data["nome"] = "Terceira Facção - Internacional"
        data["sigla"]= "TFI"
        data["pais"] = [32]
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_e_create(self):
        """
        Criação de objeto fora do país e com estado.
        """
        data = self.data
        data["nome"] = "Quarta Facção - Internacional"
        data["sigla"]= "QFI"
        data["pais"] = [32]
        data["estado"] = [28]
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_f_create(self):
        """
        Criação de objeto sem país e com estado.
        """
        data = self.data
        data["nome"] = "Quinta Facção - Internacional"
        data["sigla"]= "QUFI"
        data["pais"] = None
        data["estado"] = [28]
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_g_create(self):
        """
        Criação de objeto sem país e sem estado.
        """
        data = self.data
        data["nome"] = "Sexta Facção - Internacional"
        data["sigla"]= "SFI"
        data["pais"] = None
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_h_create(self):
        """
        Criação de objeto sem país e inativo.
        """
        data = self.data
        data["nome"] = "Sétima Facção - Internacional"
        data["sigla"]= "SEFI"
        data["pais"] = None
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_i_create(self):
        """
        Criação de objeto sem país e excluído.
        """
        data = self.data
        data["nome"] = "Oitava Facção - Internacional"
        data["sigla"]= "OFI"
        data["pais"] = None
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_j_create(self):
        """
        Criação de objeto sem data de inclusão.
        """
        data = self.data
        data["nome"] = "Nona Facção - Internacional"
        data["sigla"]= "NFI"
        data["pais"] = [13]
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_k_create(self):
        """
        Criação de objeto com data de inclusão inválida.
        """
        data = self.data
        data["nome"] = "Decima Facção - Internacional"
        data["sigla"]= "DFI"
        data["pais"] = [13]
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_l_create(self):
        """
        Criação de objeto sem data de exclusão.
        """
        data = self.data
        data["nome"] = "Décima Primeira Facção - Internacional"
        data["sigla"]= "DPFI"
        data["pais"] = [13]
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_m_create(self):
        """
        Criação de objeto com data de exclusão inválida.
        """
        data = self.data
        data["nome"] = "Decima Segunda Facção - Internacional"
        data["sigla"]= "DSFI"
        data["pais"] = [13]
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_n_create(self):
        """
        Criação de objeto com data de exclusão anterior a data de inclusão.
        """
        data = self.data
        data["nome"] = "Decima Terceira Facção - Internacional"
        data["sigla"]= "DTFI"
        data["pais"] = [13]
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_o_create(self):
        """
        Criação de objeto com usuário inválido.
        """
        data = self.data
        data["nome"] = "Decima Quarta Facção - Internacional"
        data["sigla"]= "DQFI"
        data["pais"] = [13]
        data["estado"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_p_create(self):
        """
        Criação de nome duplicado.
        """
        data = self.data
        data["nome"] = "Primeira Facção"
        data["sigla"]= "PFSXX"
        data["pais"] = [33]
        data["estado"] = [12]
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

    def test_q_create(self):
        """
        Criação de sigla duplicado.
        """
        data = self.data
        data["nome"] = "Primeira Facção duplicado"
        data["sigla"]= "PFS"
        data["pais"] = [33]
        data["estado"] = [12]
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')
    
    def test_r_create(self):
        """
        Criação de registro com mesmo nome e sigla 
        """
        data = self.data
        data["nome"] = "FACÇÃO EXCLUIR"
        data["sigla"]= "PFS"
        data["pais"] = [33]
        data["estado"] = [11]
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.client.post(self.url, data=data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

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

        url = f'{self.url}?search=Condominio'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f'{self.url}?search=Jose'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_d_list(self):
        """
        List de objetos ativos
        """
        url = f'{self.url}?ativo=true'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos inativos
        """
        url = f'{self.url}?ativo=false'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro existente.
        """
        data = self.data
        data["nome"] = "Primeira Facção duplicado para deletar"
        data["sigla"]= "PFS"
        data["pais"] = [33]
        data["estado"] = [11]
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_b_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"25a84ddd-ac32-43e8-8b3e-ccb00d60cf41"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")


    def test_a_update(self):
        """
        Atualizando registro de nome.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 1"
        data["sigla"]= "PFS"
        data["pais"] = [33]
        data["estado"] = [28]
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Facção para atualizar 2" 
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_b_update(self):
        """
        Atualizando registro de sigla.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 3"
        data["sigla"]= "PFS"
        data["pais"] = [33]
        data["estado"] = [28]
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Facção para atualizar 4" 
            data["sigla"]= "PFS2"
            data["estado"] = [11]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_c_update(self):
        """
        Atualizando registro de estado.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 5"
        data["sigla"]= "PFS"
        data["pais"] = [33]
        data["estado"] = [15]
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Facção para atualizar 5" 
            data["sigla"]= "PFS"
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_d_update(self):
        """
        Atualizando registro de pais.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 6"
        data["sigla"]= "PFS"
        data["pais"] = [15]
        data["estado"] = None
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Facção para atualizar 6" 
            data["sigla"]= "PFS"
            data["estado"] = [19]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_e_update(self):
        """
        Atualizando registro de pais.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 7"
        data["sigla"]= "PFS"
        data["pais"] = [15]
        data["estado"] = None
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Facção para atualizar 8" 
            data["sigla"]= "PFS"
            data["pais"] = [33]
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')        

    def test_f_update(self):
        """
        Atualizando registro de pais inválido com estado.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 9"
        data["sigla"]= "PFS"
        data["pais"] = [33]
        data["estado"] = [28]
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Facção para atualizar 10" 
            data["sigla"]= "PFS"
            data["pais"] = [18]
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo='Update')

    def test_g_update(self):
        """
        Atualizando registro de pais inválido com estado.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 10"
        data["sigla"]= "PFS"
        data["pais"] = [33]
        data["estado"] = [28]
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data = self.data
            data["nome"] = "Facção para atualizar 11"
            data["sigla"]= "PFS"
            data["pais"] = None
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo='Update')           

    def test_h_update(self):
        """
        Atualizando registro de pais inválido com estado.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 8"
        data["sigla"]= "PFS"
        data["pais"] = [33]
        data["estado"] = [28]
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data = self.data
            data["nome"] = "Facção para atualizar 9"
            data["sigla"]= "PFS"
            data["pais"] = None
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo='Update')  

    def test_i_update(self):
        """
        Atualizando data inválida.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 9"
        data["sigla"]= "PFS"
        data["pais"] = [15]
        data["estado"] = None
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data = self.data
            data["nome"] = "Facção para atualizar 10"
            data["sigla"]= "PFS"
            data["pais"] = [33]
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo='Update')

    def test_j_update(self):
        """
        Atualizando usuário de cadastro.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 12"
        data["sigla"]= "PFS"
        data["pais"] = [15]
        data["estado"] = None
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data = self.data
            data["nome"] = "Facção para atualizar 13"
            data["sigla"]= "PFS"
            data["pais"] = [33]
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo='Update')   

    def test_k_update(self):
        """
        Atualizando cadastro inativo.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 13"
        data["sigla"]= "PFS"
        data["pais"] = [15]
        data["estado"] = None
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data = self.data
            data["nome"] = "Facção para atualizar 14"
            data["sigla"]= "PFS"
            data["pais"] = [33]
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo='Update')   


    def test_l_update(self):
        """
        Atualizando cadastro excluído para ativo.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 12"
        data["sigla"]= "PFS"
        data["pais"] = [15]
        data["estado"] = None
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data = self.data
            data["nome"] = "Facção atualizada 12"
            data["sigla"]= "PFS"
            data["pais"] = [33]
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo='Update') 

    def test_m_update(self):
        """
        Atualizando cadastro excluído.
        """
        data = self.data
        data["nome"] = "Facção para atualizar 13"
        data["sigla"]= "PFS"
        data["pais"] = [15]
        data["estado"] = None
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data = self.data
            data["nome"] = "Facção atualizada 13"
            data["sigla"]= "PFS"
            data["pais"] = [33]
            data["estado"] = [28]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_client_error(resp.status_code))
            self.format_print(metodo='Update') 