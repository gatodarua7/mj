"""configuracao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from autenticacao.token import TokenView
from decouple import config
from localizacao.urls import router as localizacao_router
from cadastros.urls import router as cadastros_router
from orcrim.urls import router as orcrim_router
from social.urls import router as social_router
from vinculos.urls import router as vinculos_router
from pessoas.urls import router as pessoas_router
from prisional.urls import router as prisional_router
from juridico.urls import router as juridico_router
from movimentacao.urls import router as movimentacao_router
from comum.urls import router as comum_router
from escolta.urls import router as escolta_router
from visitante.urls import router as visitante_router
from core.urls import router as configuracoes_router
from configuracao import versao
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


BASE_URL = config("BASE_URL")

schema_view = get_schema_view(
    openapi.Info(
        title="SIAPEN API",
        default_version=f"{versao.read_file()}",
        description="API SIAPEN",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name=""),
    ),
    url=BASE_URL,
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(
        r"^doc(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "doc/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/cadastros/", include(cadastros_router.urls)),
    path("api/comum/", include(comum_router.urls)),
    path("api/localizacao/", include(localizacao_router.urls)),
    path("api/orcrim/", include(orcrim_router.urls)),
    path("api/prisional/", include(prisional_router.urls)),
    path("api/pessoas/", include(pessoas_router.urls)),
    path("api/escoltas/", include(escolta_router.urls)),
    path('api/juridico/', include(juridico_router.urls)),
    path('api/movimentacao/', include(movimentacao_router.urls)),
    path("api/social/", include(social_router.urls)),
    path("api/vinculos/", include(vinculos_router.urls)),
    path("api/visitante/", include(visitante_router.urls)),
    path("api/configuracao/", include(configuracoes_router.urls)),
    path("admin/", admin.site.urls),
    path("api/versao/", versao.get_versao),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/", TokenView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
