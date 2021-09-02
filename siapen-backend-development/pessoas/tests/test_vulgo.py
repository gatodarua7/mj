from django.db.models.query import QuerySet
from comum.tests.base import SiapenTestCase
from pessoas.interno.models import Interno, InternoVulgosThroughModel, Vulgo
from rest_framework import status
import json
import requests


class TestVulgoInternoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/pessoas/interno.json",
        "fixtures/cadastro/genero.json",
        "fixtures/cadastro/regime_prisional.json",
        "fixtures/social/necessidade_especial.json",
        "fixtures/social/estado_civil.json",
        "fixtures/social/grau_instrucao.json",
        "fixtures/social/orientacao_sexual.json",
        "fixtures/social/raca.json",
        "fixtures/social/religiao.json",
        "fixtures/social/profissao.json",
        "fixtures/usuarios/usuario.json",
        "fixtures/localizacao/estados.json",
        "fixtures/localizacao/paises.json",
        "fixtures/localizacao/municipios.json",
    ]

    def setUp(self) -> None:
        self.entidade = "InternoVulgosThroughModel"
        self.obj_id = Vulgo.objects.create(nome="Teste 1").pk
        self.novo_vulgo = Vulgo.objects.create(nome="Teste 2").pk

        self.data = {
            "interno": "1191484a-4ab1-4662-8c41-269fc1e66e23",
            "nome": self.obj_id
        }
        self.interno = Interno.objects.get(nome="JOSE MARIA")
        super(TestVulgoInternoEndpoint, self).setUp()

    def test_a_create(self):
        vulgo = Vulgo.objects.get(id=self.obj_id)
        self.assertTrue(isinstance(vulgo, Vulgo)) 

    def test_c_list(self):
        """
        List de objetos
        """
        vulgos = InternoVulgosThroughModel.objects.filter(interno=self.interno.id)
        self.assertIsInstance(vulgos, QuerySet)
        self.format_print(metodo="list")

    def test_d_update(self):
        """
        Aualiza objeto
        """
        vulgo2 = Vulgo.objects.get(id=self.novo_vulgo)
        vulgo = InternoVulgosThroughModel.objects.filter(interno=self.interno.id)
        vulgo.vulgo = vulgo2

        self.assertIsInstance(vulgo, QuerySet)
        self.format_print(metodo="update")

    def test_d_update(self):
        """
        Aualiza objeto
        """
        vulgo2 = Vulgo.objects.get(id=self.novo_vulgo)
        vulgo = InternoVulgosThroughModel.objects.filter(interno=self.interno.id)
        vulgo.vulgo = vulgo2

        self.assertIsInstance(vulgo, QuerySet)
        self.format_print(metodo="update")

    def test_e_delete(self):
        """
        Deleta objeto
        """
        vulgo = InternoVulgosThroughModel.objects.filter(interno=self.interno.id).delete()
        self.assertEqual(len(vulgo) == 0, False)
        self.format_print(metodo="delete")

    def test_f_delete(self):
        """
        Deleta objeto
        """
        vulgo = InternoVulgosThroughModel.objects.filter(interno=self.interno.id).delete()
        self.assertTrue(vulgo)
        self.format_print(metodo="delete")


    
