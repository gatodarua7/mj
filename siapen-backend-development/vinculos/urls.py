from rest_framework import routers

from vinculos.views import TipoVinculoViewSet

router = routers.DefaultRouter()

router.register(r"tipo-vinculo", TipoVinculoViewSet)
