from rest_framework import routers

from orcrim.views import (
    FaccaoPessoaViewSet,
    FaccaoViewSet,
    FaccaoGrupoViewSet,
    FaccaoCargoViewSet,
)

router = routers.DefaultRouter()

router.register(r"faccao", FaccaoViewSet)
router.register(r"faccao-pessoa", FaccaoPessoaViewSet)
router.register(r"faccao-grupo", FaccaoGrupoViewSet)
router.register(r"faccao-cargo", FaccaoCargoViewSet)
