from django.db.models.query import QuerySet
from movimentacao.models import PedidoInclusao, VulgosThroughModel
from comum.tests.base import SiapenTestCase
from pessoas.interno.models import Vulgo
from rest_framework import status
import json
import requests


class TestVulgoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/movimentacao/pedido-inclusao.json",
        "fixtures/movimentacao/fases.json",
        "fixtures/cadastro/genero.json",
        "fixtures/cadastro/regime_prisional.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/estados.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
    ]

    def setUp(self) -> None:
        self.entidade = "VulgosThroughModel"
        self.obj_id = Vulgo.objects.create(nome="Teste 1").pk
        self.novo_vulgo = Vulgo.objects.create(nome="Teste 2").pk

        self.data = {
            "pedido_inclusao": "0afdff24-e1d5-401b-a4f3-639fb3236c0e",
            "nome": self.obj_id
        }
        self.pedido = PedidoInclusao.objects.get(nome="JOSE MARIA DOS SANTOS")
        super(TestVulgoEndpoint, self).setUp()

    def test_a_create(self):
        vulgo = Vulgo.objects.get(id=self.obj_id)
        self.assertTrue(isinstance(vulgo, Vulgo)) 

    def test_c_list(self):
        """
        List de objetos
        """
        vulgos = VulgosThroughModel.objects.filter(pedido_inclusao=self.pedido.id)
        self.assertIsInstance(vulgos, QuerySet)
        self.format_print(metodo="list")

    def test_d_update(self):
        """
        Aualiza objeto
        """
        vulgo2 = Vulgo.objects.get(id=self.novo_vulgo)
        vulgo = VulgosThroughModel.objects.filter(pedido_inclusao=self.pedido.id)
        vulgo.vulgo = vulgo2

        self.assertIsInstance(vulgo, QuerySet)
        self.format_print(metodo="update")

    def test_d_update(self):
        """
        Aualiza objeto
        """
        vulgo2 = Vulgo.objects.get(id=self.novo_vulgo)
        vulgo = VulgosThroughModel.objects.filter(pedido_inclusao=self.pedido.id)
        vulgo.vulgo = vulgo2

        self.assertIsInstance(vulgo, QuerySet)
        self.format_print(metodo="update")

    def test_e_delete(self):
        """
        Deleta objeto
        """
        vulgo = VulgosThroughModel.objects.filter(pedido_inclusao=self.pedido.id).delete()
        self.assertEqual(len(vulgo) == 0, False)
        self.format_print(metodo="delete")

    def test_f_delete(self):
        """
        Deleta objeto
        """
        vulgo = VulgosThroughModel.objects.filter(pedido_inclusao=self.pedido.id).delete()
        self.assertTrue(vulgo)
        self.format_print(metodo="delete")


    
