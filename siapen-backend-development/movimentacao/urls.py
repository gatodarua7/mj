from rest_framework import routers

from movimentacao.views import (
    AnalisePedidoViewSet,
    FasesPedidoViewSet,
    PedidoInclusaoViewSet,
    PedidoInclusaoOutroNomeViewSet,
    PedidoInclusaoMovimentacaoViewSet,
)

router = routers.DefaultRouter()

router.register(r"fases-pedido", FasesPedidoViewSet)
router.register(r"pedido-inclusao", PedidoInclusaoViewSet)
router.register(r"outro-nome", PedidoInclusaoOutroNomeViewSet)
router.register(r"pedido-movimentacao", PedidoInclusaoMovimentacaoViewSet)
router.register(r"analise-pedido", AnalisePedidoViewSet)
