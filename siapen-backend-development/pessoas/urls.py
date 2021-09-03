from rest_framework import routers

from pessoas.servidor.views import ServidorViewSet
from pessoas.interno.views import (
    InternoViewSet,
    VulgoViewSet,
    OutroNomeViewSet,
    ContatosViewSet,
    SinaisParticularesViewSet,
    RgViewSet,
)
from pessoas.advogado.views import (
    AdvogadoViewSet,
    RgAdvogadoViewSet,
    EmailViewSet,
    OABViewSet,
)


router = routers.DefaultRouter()


router.register(r"servidor", ServidorViewSet)
router.register(r"interno", InternoViewSet)
router.register(r"outro-nome", OutroNomeViewSet)
router.register(r"vulgo", VulgoViewSet)
router.register(r"rg-interno", RgViewSet)
router.register(r"contatos-interno", ContatosViewSet)
router.register(r"sinais", SinaisParticularesViewSet)
router.register(r"advogado", AdvogadoViewSet)
router.register(r"email", EmailViewSet)
router.register(r"rg-advogado", RgAdvogadoViewSet)
router.register(r"oab", OABViewSet)
