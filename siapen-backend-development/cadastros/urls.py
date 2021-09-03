from rest_framework import routers

from cadastros.views import (
    FotoViewSet,
    GeneroViewSet,
    PessoaViewSet,
    TipoDocumentoViewSet,
    FuncaoViewSet,
    CargosViewSet,
    OrgaoExpedidorViewSet,
    RegimePrisionalViewSet,
    PericulosidadeViewSet,
    DocumentosViewSet,
    SetorViewSet,
    ComportamentoInternoViewSet,
)

router = routers.DefaultRouter()


router.register(r"cargos", CargosViewSet)
router.register(r"funcao", FuncaoViewSet)
router.register(r"generos", GeneroViewSet)
router.register(r"tipo-documento", TipoDocumentoViewSet)
router.register(r"pessoas", PessoaViewSet)
router.register(r"foto", FotoViewSet)
router.register(r"setor", SetorViewSet)
router.register(r"orgao-expedidor", OrgaoExpedidorViewSet)
router.register(r"regime-prisional", RegimePrisionalViewSet)
router.register(r"periculosidade", PericulosidadeViewSet)
router.register(r"documento", DocumentosViewSet)
router.register(r"comportamento-interno", ComportamentoInternoViewSet)
