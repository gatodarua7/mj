from re import T
from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests


class TestAdvogadoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/usuarios/usuario.json",
        "fixtures/cadastro/foto.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/cadastro/genero.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/religiao.json",
        "fixtures/pessoas/advogado.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Advogado"
        self.url = f"/api/pessoas/advogado/"
        self.data = {
            "nome": "Carlos Leopoldo",
            "data_nascimento": "01/01/2000",
            "genero": "96637461-43cb-4d55-893b-c09fe514ecf7",
            "nacionalidade": [33],
            "naturalidade": 283,
            "estado": 29,
            "enderecos": [],
            "telefones": [],
            "foto": "",
            "cpf": "94875968019",
            "necessidade_especial": ["b83cb47a-dbdb-49e4-9ef7-34fcec39443f"],
            "oabs": "",
            "ativo": True,
        }
        super(TestAdvogadoEndpoint, self).setUp()

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
        Criação de objeto com mesmo CPF.
        """
        data = self.data
        data["nome"] = "JOSE"
        data["cpf"] = "94875968019"
        resp = self.client.post(self.url, data=data, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto com campos obrigatórios nao enviados.
        """
        data = self.data
        data["cpf"] = ""
        data["data_nascimento"] = ""
        data["nome"] = ""
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto cpf invalido.
        """
        data = self.data
        data["cpf"] = "11111111111"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de objeto de uma cidade no estado em outro.
        """

        data = self.data
        data["cpf"] = "99822245068"
        data["nacionalidade"] = [33]
        data["estado"] = 28
        data["naturalidade"] = 12
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
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_c_list(self):
        """
        List de objetos sem acento
        """
        url = f"{self.url}?search=Jose"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_d_list(self):
        """
        List de objetos ativos
        """
        url = f"{self.url}?ativo=true"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_e_list(self):
        """
        List de objetos inativos
        """
        url = f"{self.url}?ativo=false"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_a_update(self):
        """
        Atualizando objeto excluído.
        """
        data = self.data
        data["cpf"] = "14790844099"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            url = f'{self.base_url+self.url}{resp_json["id"]}/'
            resp = requests.put(
                url, data=json.dumps(data), proxies=self.proxies, headers=self.headers
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_b_update(self):
        """
        Atualizando nome do objeto
        """
        data = self.data
        data["cpf"] = "98925258099"
        resp = self.client.post(self.url, data=data, content_type="application/json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "JOSEFA"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="update")

    def test_c_update(self):
        """
        Atualizando nome do objeto inativo.
        """

        data = self.data
        data["cpf"] = "05212487013"
        data["ativo"] = False
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_d_update(self):
        """
        Atualizando cpf do objeto para valor invalido.
        """

        data = self.data
        data["cpf"] = "48020807004"
        resp = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json"
        )
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["cpf"] = "11111111111"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_a_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """

        data = self.data
        data["cpf"] = "59517890010"
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
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.format_print(metodo="delete")
