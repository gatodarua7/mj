from rest_framework import routers

from localizacao.views import PaisViewSet
from localizacao.views import EstadoViewSet
from localizacao.views import CidadeViewSet

router = routers.DefaultRouter()

router.register(r'paises', PaisViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'cidades', CidadeViewSet)
