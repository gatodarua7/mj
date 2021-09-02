from comum.tests.base import SiapenTestCase
from rest_framework import status
import json


class TestCargosEndpoint(SiapenTestCase):
    def setUp(self) -> None:
        self.entidade = 'CARGOS'
        self.url = f'/api/cadastros/cargos/'
        self.data = {"cargo": "CARGO 1", "ativo": True}
        super(TestCargosEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

    def test_b_create(self):
        """
        Criação de objeto DUPLICADO.
        """
        self.client.post(self.url, data=self.data)
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.format_print(metodo='create')

    def test_c_create(self):
        """
        Criação de objeto nome vazia.
        """
        data = self.data
        data["cargo"] = ""
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo='create')

    def test_d_create(self):
        """
        Criação de objeto inativo.
        """
        data = self.data
        data['ativo'] = False
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo='create')

    def test_e_list(self):
        """
        List de objetos
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
    
    def test_f_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """

        data = self.data
        resp = self.client.post(self.url, data=data, format='json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='delete')
    
    def test_g_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"0d74acd5-4ff2-428e-b592-290391ee4701"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo='delete')
    
    def test_h_delete(self):
        """
        Apagando registro com vinculo.
        """
        url = f'{self.url}{"05ebe3b6-a127-4c3b-9bf2-8c3034adea10"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo='delete')

    def test_h_update(self):
        """
        Atualizando objeto excluído.
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format='json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo='Update')

    def test_i_update(self):
        """
        Atualizando nome do objeto
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format='json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["cargo"] = "CARGOS 2"
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='Update')

    def test_k_update(self):
        """
        Atualizando nome de objeto para já existente
        """
        data = self.data
        self.client.post(self.url, data=data, format='json')
        data["cargo"] = "CARGOS 2"
        resp = self.client.post(self.url, data=data, format='json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["cargo"] = "CARGO 1"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
            self.format_print(metodo='Update')
    
    def test_l_update(self):
        """
        Atualizando objeto com nome Vazio
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format='json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["cargo"] = ""
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo='Update')