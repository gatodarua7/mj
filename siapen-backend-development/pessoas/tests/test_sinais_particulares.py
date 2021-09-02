from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests



class TestSinaisParticularesEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/cadastro/foto.json",
        "fixtures/pessoas/interno.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/raca.json",
        "fixtures/social/religiao.json",
        "fixtures/social/profissao.json",
        "fixtures/cadastro/genero.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json"
    ]

    def setUp(self) -> None:
        self.entidade = "Sinais_Particulares"
        self.url = f"/api/pessoas/sinais/"
        self.data = {'interno': '1191484a-4ab1-4662-8c41-269fc1e66e23',
                    'foto': "efcd3306-0c77-4f93-945c-9672ff72e256",
                    'area': 'frt_01',
                    'position_x': 2,
                    'position_y': 1,
                    'tipo': 'TATUAGEM',
                    'descricao': 'Tatuagem Teste',
                    "motivo_ativacao": "",
                    "motivo_inativacao": ""
        }
        super(TestSinaisParticularesEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        data = self.data
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto com sem interno.
        """
        data = self.data
        data["interno"] = ""
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto com interno inexistente.
        """
        data = self.data
        data["interno"] = "1aa7de60-9666-4af6-a4da-1e0c64e75f08"
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto sem interno.
        """
        data = self.data
        data["interno"] = ""
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de objeto sem descricao.
        """
        data = self.data
        data.pop('descricao')
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")
    
    def test_f_create(self):
        """
        Criação de objeto sem tipo.
        """
        data = self.data
        data.pop('tipo')
        resp = self.client.post(self.url, data=data)
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
        Atualizando objeto excluído.
        """
        data = self.data
        data["area"] = "rtf_2"
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json['motivo_exclusao'] = 'Foto errada.'
            resp = self.client.delete(url)
            resp_json['updated_at'] = ""
            resp_json['delete_at'] = ""
            resp_json['usuario_edicao'] = ""
            resp_json['usuario_exclusao'] = ""
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_b_update(self):
        """
        Atualizando descricao do objeto
        """
        data = self.data
        data["interno"] = "a414408d-aee8-44a7-b513-f7084fde2beb"
        data["descricao"] = "Primeira descricao teste"
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["descricao"] = "Descricao testes"
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_a_delete(self):
        '''
        Validando o processo de remoção de registro válido.
        '''
        
        data = self.data
        data['descricao'] = 'c'
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json['motivo_exclusao'] = 'Foto XPTO.'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo='delete')

    def test_b_delete(self):
        '''
        Apagando registro excluido inexistente.
        '''
        data = self.data
        data['descricao'] = 'c'
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{"c626e537-f520-4c87-b39b-2391294bdded"}/'
            resp_json['motivo_exclusao'] = 'Foto'
            resp_json['delete_at'] = "2021-07-08 "
            resp = self.client.delete(url)
            resp = self.client.patch(url)
            self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
            self.format_print(metodo='delete')

    def test_c_delete(self):
        '''
        Apagando registro ja excluído.
        '''
        data = self.data
        data['descricao'] = 'Teste'
        resp = self.client.post(self.url, data=data)
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json['motivo_exclusao'] = 'teste'
            resp = self.client.delete(url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.format_print(metodo='delete')