# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from prisional.models import UsuarioSistema, Setor, Cela, Bloco, SistemaPenal, Unidade


class UsuarioSistemaInline(admin.StackedInline):
    model = UsuarioSistema
    can_delete = False
    verbose_name_plural = "Dados Complementares"


class UsuarioAdmin(UserAdmin):
    list_display = ["username", "email", "nome", "is_superuser"]
    inlines = (UsuarioSistemaInline,)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("E-mail"), {"fields": ("email",)}),
        (
            ("Permissões"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    def nome(self, obj):
        return obj.usuariosistema.pessoa


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
admin.site.register(SistemaPenal)
admin.site.register(Unidade)
admin.site.register(Setor)
admin.site.register(Cela)
admin.site.register(Bloco)
