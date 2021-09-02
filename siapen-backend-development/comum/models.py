from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from core.models import BaseModel
from localizacao.models import Cidade, Estado
from util import mensagens

class CaseInsensitiveFieldMixin:
    LOOKUP_CONVERSIONS = {
        'exact': 'iexact',
        'contains': 'icontains',
        'startswith': 'istartswith',
        'endswith': 'iendswith',
        'regex': 'iregex',
        'unaccent': 'unaccent'
    }

    def get_lookup(self, lookup_name):
        converted = self.LOOKUP_CONVERSIONS.get(lookup_name, lookup_name)
        return super().get_lookup(converted)


class CICharField(CaseInsensitiveFieldMixin, models.CharField):
    pass


class CITextField(CaseInsensitiveFieldMixin, models.TextField):
    pass


TIPO_TEL = (
    ('CELULAR', 'Celular'),
    ('FUNCIONAL', 'Celular Funcional'),
    ('RAMAL', 'Ramal'),
    ('RESIDENCIAL', 'Residencial')
)


class Endereco(BaseModel):
    logradouro = CICharField(max_length=250)
    bairro = CICharField(max_length=150)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = CITextField(null=True, blank=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)
    andar = models.CharField(max_length=20, blank=True, null=True)
    sala = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.logradouro

    class Meta:
        verbose_name = (u"Endereço")
        verbose_name_plural = (u"Endereços")

class Telefone(BaseModel):
    numero = models.CharField(max_length=11, validators=[RegexValidator(r'^\d{1,11}$')])
    tipo = models.CharField(choices=TIPO_TEL, max_length=15)
    observacao = models.TextField(max_length=200, null=True, blank=True)
    andar = models.CharField(max_length=20, blank=True, null=True)
    sala = models.CharField(max_length=20, blank=True, null=True)
    privado = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.numero

    class Meta:
        verbose_name = (u"Telefone")
        verbose_name_plural = (u"Telefones")