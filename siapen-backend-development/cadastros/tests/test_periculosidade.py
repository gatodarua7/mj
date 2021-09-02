from comum.tests.base import SiapenTestCase
from rest_framework import status


class TestPericulosidadeEndpoint(SiapenTestCase):
    def setUp(self) -> None:
        self.entidade = "GRAU_PERICULOSIDADE"
        self.url = f"/api/cadastros/periculosidade/"
        self.data = {
            "nome": "Periculoso",
            "sigla": "P",
            "observacao": "Soft",
            "ativo": True,
        }
        super(TestPericulosidadeEndpoint, self).setUp()

    def test_a_create(self):
        """
        Criação de objeto válido.
        """
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto DUPLICADO.
        """
        self.client.post(self.url, data=self.data)
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto nome vazia.
        """
        data = self.data
        data["nome"] = ""
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        Criação de objeto sigla vazia.
        """
        data = self.data
        data["sigla"] = ""
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        Criação de objeto observacao vazia.
        """
        data = self.data
        data["observacao"] = ""
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

    def test_f_create(self):
        """
        Criação de objeto inativo.
        """
        data = self.data
        data["ativo"] = False
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.format_print(metodo="create")

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
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_g_delete(self):
        """
        Apagando registro inexistente.
        """
        url = f'{self.url}{"015039e9-082f-48dc-8c28-ca018ff44c8c"}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_h_update(self):
        """
        Atualizando objeto excluído.
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            self.client.delete(url)
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_i_update(self):
        """
        Atualizando nome do objeto
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["nome"] = "Baixa Periculosidade"
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_j_update(self):
        """
        Atualizando sigla do objeto
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["sigla"] = "BP"
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_k_update(self):
        """
        Atualizando observação do objeto
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp_json["observacao"] = "Individuo de baixa complexidade."
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_l_update(self):
        """
        Atualizando nome de objeto para já existente
        """
        data = self.data
        self.client.post(self.url, data=data, format="json")
        data["nome"] = "TESTE"
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = "TESTE"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_m_update(self):
        """
        Atualizando sigla de objeto para já existente
        """
        data = self.data
        self.client.post(self.url, data=data, format="json")
        data["sigla"] = "sigla"
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["sigla"] = "sigla"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_n_update(self):
        """
        Atualizando sigla de objeto para já existente
        """
        data = self.data
        self.client.post(self.url, data=data, format="json")
        data["observacao"] = "observacao"
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["observacao"] = "observacao"
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="Update")

    def test_o_update(self):
        """
        Atualizando objeto com nome Vazio
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["nome"] = ""
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")

    def test_p_update(self):
        """
        Atualizando objeto com sigla Vazia
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="json")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            resp_json["sigla"] = ""
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=resp_json)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="Update")