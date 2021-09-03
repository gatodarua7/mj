from django.contrib import admin
from datetime import datetime

from cadastros.models import (
    Pessoa,
    TipoDocumento,
    Cargos,
    Foto,
    OrgaoExpedidor,
    RegimePrisional,
    Periculosidade,
    Documentos,
)


class PessoaAdmin(admin.ModelAdmin):
    search_fields = ("nome",)
    list_display = ["nome", "naturalidade", "nacionalidade"]


admin.site.register(Pessoa, PessoaAdmin)
admin.site.register(TipoDocumento)
admin.site.register(Cargos)
admin.site.register(Foto)
admin.site.register(OrgaoExpedidor)
admin.site.register(RegimePrisional)
admin.site.register(Periculosidade)
admin.site.register(Documentos)
