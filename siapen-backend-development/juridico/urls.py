from rest_framework import routers

from juridico.views import NormasJuridicasViewSet, TituloLeiViewSet

router = routers.DefaultRouter()

router.register(r"titulo", TituloLeiViewSet)
router.register(r"norma-juridica", NormasJuridicasViewSet)
