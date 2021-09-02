from django.contrib import admin
from .models import PedidoInclusao, PedidoInclusaoOutroNome, FasesPedido

admin.site.register(PedidoInclusao)
admin.site.register(PedidoInclusaoOutroNome)
admin.site.register(FasesPedido)
