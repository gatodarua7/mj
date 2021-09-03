from rest_framework import routers

from prisional.views import (
    BlocoViewSet,
    CelaViewSet,
    DefeitoCelaViewSet,
    DefeitoViewSet,
    DesignacaoFuncaoServidorViewSet,
    ReparoCelaViewSet,
    SistemaPenalViewSet,
    UnidadeViewSet,
    PrisionalViewSet,
    UsuarioSistemaViewSet,
)

router = routers.DefaultRouter()

router.register(r"sistema-penal", SistemaPenalViewSet)
router.register(r"unidade", UnidadeViewSet)
router.register(r"", PrisionalViewSet)
router.register(r"bloco", BlocoViewSet)
router.register(r"defeito", DefeitoViewSet)
router.register(r"cela", CelaViewSet)
router.register(r"defeito-cela", DefeitoCelaViewSet)
router.register(r"reparo-cela", ReparoCelaViewSet)
router.register(r"designacao-funcao-servidor", DesignacaoFuncaoServidorViewSet)
router.register(r"usuario-sistema", UsuarioSistemaViewSet)
