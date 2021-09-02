from comum.tests.base import SiapenTestCase
from rest_framework import status
import json
import requests


class TestPedidoInclusaoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/cadastro/foto.json",
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
        "fixtures/localizacao/estados.json",
        "fixtures/comum/endereco.json",
        "fixtures/comum/telefone.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/cadastro/genero.json",
        "fixtures/cadastro/regime_prisional.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/religiao.json",
        "fixtures/movimentacao/fases.json",
        "fixtures/movimentacao/pedido-inclusao.json",
    ]

    def setUp(self) -> None:
        self.entidade = "PedidoInclusao"
        self.url = f"/api/movimentacao/pedido-inclusao/"
        self.data = {
            "nome": "JOSEFA ARAGÂO",
            "nome_social": "",
            "genero": "24b81a5b-b377-4fd9-b05e-5db5b90b9461",
            "estado": None,
            "naturalidade": None,
            "cpf": "35916019009",
            "foto": None,
            "nome_mae": "MARIA",
            "nome_pai": "JOSE",
            "mae_falecido": False,
            "mae_nao_declarado": False,
            "pai_falecido": False,
            "pai_nao_declarado": False,
            "data_nascimento": "05/02/1986",
            "preso_extraditando": False,
            "regime_prisional": "96637461-43cb-4d55-893b-c09fe514ecf8",
            "interesse": "SEGURANCA_PUBLICA",
            "tipo_inclusao": "DEFINITIVO",
            "numero_sei": "23454.908908/2020-12",
            "data_pedido_sei": "05/02/2021",
            "data_movimentacao": "2021-05-25T01:17:21.853Z",
            "fase_pedido": "210fc034-845d-42ce-9a5e-621d3716e1fe",
            "motivo_exclusao": None,
            "estado_solicitante": 13,
            "nacionalidade": [
                1
            ],
            "necessidade_especial": [
                "b83cb47a-dbdb-49e4-9ef7-34fcec39443f"
            ]
        }
        super(TestPedidoInclusaoEndpoint, self).setUp()

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
        Criação de objeto Interno Ativo
        """
        data = self.data
        data['cpf'] = '61094644064'
        resp = self.client.post(self.url, data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto vazio.
        """
        data = self.data
        data["data_nascimento"] = None
        data["vulgo"] = None
        data["preso_extraditando"] = None
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de pedido de inclusao sem interessado.
        """
        data = self.data
        data["interesse"] = ""
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de pedido de inclusao sem fase.
        """
        data = self.data
        data["tipo_inclusao"] = ""
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_f_create(self):
        """
        Criação de pedido de inclusao com menor de idade.
        """
        pedido = self.data
        pedido["data_nascimento"] = "10/10/2020"
        resp = self.client.post(self.url, data=json.dumps(pedido), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_g_create(self):
        """
        Criação de pedido de inclusao sem numero SEI.
        """
        data = self.data
        data["numero_sei"] = ""
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
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
        """List de objetos em escolta"""
    
        url = self.url + "?page=1&ordering=&page_size=10&fase=escolta&search="
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_c_list(self):
        """List de objetos em cgin"""
    
        url = self.url + "?page=1&ordering=&page_size=10&fase=cgin&search="
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_d_list(self):
        """Dashboard de ToTal por fase"""
    
        url = self.url + "total-fases/"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_e_list(self):
        """Dashboard de ToTal parecer CGIN"""
    
        url = self.url + "total-parecer-cgin/"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_f_list(self):
        """Dashboard de ToTal unidade CGIN"""
    
        url = self.url + "total-unidades-cgin/"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_g_list(self):
        """Dashboard de ToTal fase por mes"""
    
        url = self.url + "total-fases-mes/"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_h_list(self):
        """Dashboard de ToTal por estado Solicitante"""
    
        url = self.url + "total-estado-solicitante/"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_i_list(self):
        """
        List de com acento
        """

        url = f'{self.url}?search=ARAGÂO'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_j_list(self):
        """
        List de objetos sem acento
        """
        url = f'{self.url}?search=ARAGAO'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_k_list(self):
        """
        List de objetos ativos
        """
        url = f'{self.url}?ativo=true'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_l_list(self):
        """
        List de objetos inativos
        """
        url = f'{self.url}?ativo=false'
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_m_list(self):
        """List de objetos em escolta"""
    
        url = self.url + "pessoas/?page=1&ordering=nome&page_size=10&cpf=06789566413&nome=jose&nome_mae=maria"
        resp = self.client.get(url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")
    
    def test_j_update(self):
        """
        Atualizando objeto excluído.
        """

        data = self.data
        data["cpf"] = "84012256041"
        resp = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_k_update(self):
        """
        Atualizando dados do objeto
        """

        data = self.data
        data["nome"] = "Atualização de nome"
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "Dona Finha."
            resp_json["cpf"] = "33385149053"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_l_update(self):
        """
        Atualizando para data de nascimento invalida.
        """

        data = self.data
        data["data_nascimento"] = "05/07/2000"
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["data_nascimento"] = "09/09/2020"
            resp_json["cpf"] = "36888104060"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_n_update(self):
        """
        Atualizando para numero SEI invalido.
        """

        data = self.data
        data["numero_sei"] = "78765.827364/2020.02"
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["numero_sei"] = "78765827364AGRV02"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")
    
    def test_oo_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """

        data = self.data
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json = resp_json['motivo_exclusao'] = 'teste'
            resp = self.update(id="c38ea467-4aca-4c25-bdec-ace5aab8015f", data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="delete")

    def test_o_delete(self):
        """
        Validando o processo de remoção de registro válido.
        """

        data = self.data
        resp = self.client.post(self.url, data=data, content_type='application/json')
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json['motivo_exclusao'] = 'teste'
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")


    def test_p_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"015039e9-082f-48dc-8c28-ca018ff44c8c"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")
