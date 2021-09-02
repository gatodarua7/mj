from django.contrib import admin

from localizacao.models import Pais, Estado, Cidade

class PaisAdmin(admin.ModelAdmin):
    search_fields = ('nome', 'sigla')
    list_display = ['nome', 'sigla']


class EstadoAdmin(admin.ModelAdmin):
    search_fields = ('nome', 'sigla')
    list_display = ['nome', 'sigla']


class CidadeAdmin(admin.ModelAdmin):
    search_fields = ('nome', 'sigla')
    list_display = ['nome', 'estado']
    list_filter = ['estado']

# Register your models here.
admin.site.register(Pais, PaisAdmin)
admin.site.register(Estado, EstadoAdmin)
admin.site.register(Cidade, CidadeAdmin)