from rest_framework import routers
from comum.views import EnderecoViewSet, TelefoneViewSet

router = routers.DefaultRouter()

router.register(r"endereco", EnderecoViewSet)
router.register(r"telefones", TelefoneViewSet)
