from comum.tests.base import SiapenTestCase
from rest_framework import status
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from cadastros.models import Documentos, TipoDocumento
from django.core.files.uploadedfile import InMemoryUploadedFile
from util import mensagens
import os


class TestDocumentoEndpoint(SiapenTestCase):
    fixtures = [
        "fixtures/cadastro/tipo_documento.json",
        "fixtures/usuarios/usuario.json",
    ]

    def setUp(self) -> None:
        self.entidade = "Documentos"
        self.image = self.get_image()
        self.documento = self.get_documento()
        self.image_data = {
            "arquivo_temp": self.image,
            "tipo": 1,
            "num_cod": "0ak",
            "observacao": "Nada a observar",
            "ativo": True,
            "usuario_cadastro_id": 1,
        }
        self.documento_data = {
            "arquivo_temp": self.documento,
            "tipo": 5,
            "num_cod": "0ak",
            "observacao": "Nada a observar",
            "ativo": True,
        }
        self.url = f"/api/cadastros/documento/"
        super(TestDocumentoEndpoint, self).setUp()

    def get_image(self, file="imagem.jpg", size=(720, 480)):
        tipo = file.split(".")[-1]
        if tipo == "jpg":
            tipo = "jpeg"
        img = Image.new("RGB", size, color="red")
        img.save(file)
        buffer = BytesIO()
        img.save(buffer, tipo.upper())
        image_file = InMemoryUploadedFile(
            buffer, None, file, f"documento/{tipo}", img.size, None
        )
        image_file.seek(0)
        return image_file

    def get_documento(self, file="sample.pdf"):
        with open(file, "rb") as infile:
            _file = SimpleUploadedFile(file, infile.read())
            tp_doc = TipoDocumento.objects.get(id=1)
            attachment = Documentos.objects.create(
                tipo=tp_doc,
                num_cod="teste",
                observacao="observacao",
                arquivo_temp=_file,
                usuario_cadastro_id=1,
            )
        return attachment

    def test_a_create(self):
        """
        Criação de imagem invalida.
        """
        data = self.image_data
        data["arquivo_temp"] = self.get_image(file="gif_teste.gif")
        resp = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_b_create(self):
        """
        Criação de documento invalido.
        """
        data = self.documento_data
        data["arquivo_temp"] = self.get_documento(file="gif_teste.gif")
        resp = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.format_print(metodo="create")

    def test_c_create(self):
        """
        Criação de objeto baixa.
        """
        data = self.image_data
        data["arquivo_temp"] = self.get_image(file="baixa.jpg", size=(60, 30))
        resp = self.client.post(self.url, data=data, format="multipart")

        if status.is_success(resp.status_code):
            resp_json = resp.json()
            self.assertEqual(resp_json["detail"], mensagens.IMG_BAIXA_RESOLUCAO)
        self.format_print(metodo="create")

    def test_d_create(self):
        """
        criar imagem valida.
        """

        resp = self.client.post(self.url, data=self.image_data, format="multipart")
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="create")

    def test_e_create(self):
        """
        criar documento valido.
        """
        data = self.documento_data

        data["arquivo_temp"] = self.get_image(file="baixa.jpg", size=(60, 30))

        resp = self.client.post(self.url, data=data, format="multipart")
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="create")

    def test_a_list(self):
        """
        Criação de objeto vazio.
        """
        resp = self.client.get(self.url)
        self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="list")

    def test_b_list(self):
        """
        List
        """
        resp = self.client.post(self.url, data=self.image_data, format="multipart")
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
        data = self.image_data
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
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.format_print(metodo="delete")

    def test_a_update(self):
        """
        Atualização de objeto invalido.
        """
        data = self.image_data
        resp = self.client.post(self.url, data=data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["arquivo_temp"] = self.get_image(file="gif_teste.gif")
            data["id"] = resp_json["id"]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=data, format="multipart")
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.format_print(metodo="update")

    def test_b_update(self):
        """
        Atualização para registro em baixa qualidade.
        """
        data = self.image_data
        resp = self.client.post(self.url, data=data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["arquivo_temp"] = self.get_image(file="baixa.jpg", size=(60, 30))
            data["id"] = resp_json["id"]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=data, format="multipart")
            if status.is_success(resp.status_code):
                resp_json = resp.json()
                self.assertEqual(resp_json["detail"], mensagens.IMG_BAIXA_RESOLUCAO)
        self.format_print(metodo="update")

    def test_c_update(self):
        """
        Atualização de documento válido
        """
        data = self.documento_data
        resp = self.client.post(self.url, data=data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            data["arquivo_temp"] = self.get_image(file="baixa.jpg", size=(60, 30))
            data["id"] = resp_json["id"]
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=data, format="multipart")
            self.assertTrue(status.is_success(resp.status_code))
            self.format_print(metodo="update")

    def test_d_update(self):
        """
        Inativar registro
        """
        data = self.image_data
        resp = self.client.post(self.url, data=data, format="multipart")
        if status.is_success(resp.status_code):
            resp_json = resp.json()
            obj = {"id": resp_json["id"], "ativo": False}
            url = f'{self.url}{resp_json["id"]}/'
            resp = self.client.patch(url, data=obj, format="multipart")
            self.assertTrue(status.is_success(resp.status_code))
        self.format_print(metodo="update")
