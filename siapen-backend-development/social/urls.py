from rest_framework import routers

from social.views import (
    EstadoCivilViewSet,
    GrauDeInstrucaoViewSet,
    NecessidadeEspecialViewSet,
    OrientacaoSexualViewSet,
    ProfissaoViewSet,
    RacaViewSet,
    ReligiaoViewSet,
)

router = routers.DefaultRouter()

router.register(r"raca", RacaViewSet)
router.register(r"grau-de-instrucao", GrauDeInstrucaoViewSet)
router.register(r"religiao", ReligiaoViewSet)
router.register(r"orientacao-sexual", OrientacaoSexualViewSet)
router.register(r"profissao", ProfissaoViewSet)
router.register(r"estado-civil", EstadoCivilViewSet)
router.register(r"necessidade-especial", NecessidadeEspecialViewSet)
