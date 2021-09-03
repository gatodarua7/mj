from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.translation import gettext_lazy as _


class TokenSerializer(TokenObtainPairSerializer):
    default_error_messages = {"no_active_account": _("Usuário ou senha inválidos.")}

    @classmethod
    def get_token(cls, user):
        token = super(TokenSerializer, cls).get_token(user)

        # Add custom claims
        token["login"] = user.username
        token["nome_completo"] = user.first_name + " " + user.last_name
        token["email"] = user.email
        token["admin"] = user.is_superuser
        token["permissoes"] = []

        return token


class TokenView(TokenObtainPairView):
    serializer_class = TokenSerializer
