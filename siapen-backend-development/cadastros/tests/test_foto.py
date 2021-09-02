from comum.tests.base import SiapenTestCase
from rest_framework import status
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from cadastros.models import Foto
from django.contrib.auth.models import User
from imagehelpers.image import get_mimetype
from util import mensagens


class TestFotoEndpoint(SiapenTestCase):
    def setUp(self) -> None:
        self.entidade = "Foto"
        self.image = self.get_image()
        self.data = {"foto_temp": self.image, "ativo": True}
        self.url = f"/api/cadastros/foto/"
        super(TestFotoEndpoint, self).setUp()

    def get_image(self, file="imagem.jpg", size=(720, 480)):

        tipo = file.split(".")[-1]
        if tipo == "jpg":
            tipo = "jpeg"
        img = Image.new("RGB", size, color="red")
        img.save(file)
        buffer = BytesIO()
        img.save(buffer, tipo.upper())
        image_file = InMemoryUploadedFile(
            buffer, None, file, f"image/{tipo}", img.size, None
        )
        image_file.seek(0)
        return image_file

    def test_a_create(self):
        """
        Criação de objeto invalido.
        """
        data = self.data
        data["foto_temp"] = self.get_image(file="gif_teste.gif")
        resp = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de objeto baixa.
        """
        data = self.data
        data["foto_temp"] = self.get_image(file="baixa.jpg", size=(60, 30))
        resp = self.client.post(self.url, data=data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            self.assertEqual(resp_json["detail"], mensagens.IMG_BAIXA_RESOLUCAO)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        criar objeto valido.
        """
        resp = self.client.post(self.url, data=self.data, format="multipart")
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        Criação de objeto vazio.
        """
        resp = self.client.get(self.url)
        resp_json = resp.json()
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        List
        """
        resp = self.client.post(self.url, data=self.data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.get(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="list")

    def test_a_delete(self):
        """
        Deletar um registro.
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.delete(url)
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="delete")

    def test_b_delete(self):
        """
        Deletar um registro invalido.
        """

        url = f"{self.url}c040f4a0-05ba-45de-ab85-0c30e165ee82/"
        resp = self.client.delete(url)
        resp_json = resp.json()
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_a_update(self):
        """
        Atualização de objeto invalido.
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["foto_temp"] = self.get_image(file="gif_teste.gif")
            data["id"] = resp_json["id"]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=data, format="multipart")
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_b_update(self):
        """
        Atualização para registro em baixa qualidade.
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["foto_temp"] = self.get_image(file="baixa.jpg", size=(60, 30))
            data["id"] = resp_json["id"]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=data, format="multipart")
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                self.assertEqual(resp_json["detail"], mensagens.IMG_BAIXA_RESOLUCAO)
        self.format_print(metodo="update")

    def test_c_update(self):
        """
        Inativar registro
        """
        data = self.data
        resp = self.client.post(self.url, data=data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            obj = {"id": resp_json["id"], "ativo": False}
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=obj, format="multipart")
            self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="update")
