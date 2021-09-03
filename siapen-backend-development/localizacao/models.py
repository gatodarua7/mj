from django.db import models


class Pais(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=3)

    def __str__(self):
        return self.nome


class Estado(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT)
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=3)

    class Meta:
        unique_together = ["pais", "nome"]

    def __str__(self):
        return self.nome


class Cidade(models.Model):
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    nome = models.CharField(max_length=100)

    class Meta:
        unique_together = ["estado", "nome"]

    def __str__(self):
        return self.nome + " / " + self.estado.sigla
