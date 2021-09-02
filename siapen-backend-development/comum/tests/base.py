from rest_framework.test import APITestCase
from decouple import config
import datetime
import json
from django.contrib.auth.models import User
import requests


class SiapenTestCase(APITestCase):
    base_url = config('BASE_URL')
    proxies = {'http': None, 'https': None}
    headers = {'content-type': 'application/json'}
    entidade: str = ''

    def setUp(self) -> None:
        url = "{0}/api/token/".format(self.base_url)
        payload = {'username': 'meta', 'password': 'meta@123'}
        response = requests.post(
            url,
            data=json.dumps(payload),
            proxies=self.proxies,
            headers=self.headers
        )

        response = response.json()
        token = response['access']
        self.headers.update({'Authorization': f'Bearer {token}'})

        validated_data = {
            "username": "metateste",
            "email": "admin@admin.com",
            "password": "meta@123",
            "is_staff": True,
            "is_active": True,
            "is_superuser": True
        }

        self.user = User.objects.create(**validated_data)
        self.client.force_login(self.user)

    def format_print(self, metodo):
        print(f'[{datetime.datetime.now()}] [{self.entidade.upper()}] Método {metodo}() testado com sucesso')
