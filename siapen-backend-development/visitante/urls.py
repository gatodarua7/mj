from rest_framework import routers

from visitante.views import (
    VisitanteViewSet,
    RgVisitanteViewSet,
    EmailVisitanteViewSet,
    AnuenciaViewSet,
    ManifestacaoViewSet,
    VisitanteMovimentacaoViewSet,
    DocumentosVisitanteViewSet,
    VisitanteRecursoViewSet,
    ManifestacaoDiretoriaViewSet,
)


router = routers.DefaultRouter()

router.register(r"visitante", VisitanteViewSet)
router.register(r"rg-visitante", RgVisitanteViewSet)
router.register(r"email-visitante", EmailVisitanteViewSet)
router.register(r"anuencia", AnuenciaViewSet)
router.register(r"manifestacao", ManifestacaoViewSet)
router.register(r"movimentacao", VisitanteMovimentacaoViewSet)
router.register(r"documentos", DocumentosVisitanteViewSet)
router.register(r"recurso", VisitanteRecursoViewSet)
router.register(r"manifestacao-diretoria", ManifestacaoDiretoriaViewSet)
