from django.contrib import admin
from .servidor.models import Servidor
from .interno.models import (
    Interno,
    Vulgo,
    OutroNome,
    Rg,
    InternoVulgosThroughModel,
    Contatos,
)


admin.site.register(Servidor)
admin.site.register(Interno)
admin.site.register(Rg)
admin.site.register(Vulgo)
admin.site.register(OutroNome)
admin.site.register(Contatos)
admin.site.register(InternoVulgosThroughModel)
