from rest_framework import routers

from escolta.views import EscoltasViewSet


router = routers.DefaultRouter()

router.register(r'escoltas', EscoltasViewSet)