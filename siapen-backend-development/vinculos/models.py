from django.db import models
from cadastros.models import Pessoa
from core.models import BaseModel
from prisional.models import Bloco


class TipoVinculo(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
