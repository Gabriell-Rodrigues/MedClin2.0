# Registra os models do Módulo Farmacêutico no painel administrativo.

from django.contrib import admin

from apps.farmacia.entity_estoque.models import (
    Material,
    Medicamento,
    GestorMaterial,
    GestorMedicamento,
    MaterialConsumido,
    MedicamentoDispensado,
)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('idMaterial', 'nome', 'quantidadeEstoque',
                    'quantidadeMinima', 'dataValidade')
    search_fields = ('nome', 'descricao')
    list_filter = ('dataValidade',)
    ordering = ('nome',)


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('idMedicamento', 'nome', 'quantidadeEstoque',
                    'quantidadeMinima', 'dataValidade')
    search_fields = ('nome', 'descricao')
    list_filter = ('dataValidade',)
    ordering = ('nome',)


@admin.register(MaterialConsumido)
class MaterialConsumidoAdmin(admin.ModelAdmin):
    list_display = ('idConsumo', 'material', 'quantidade', 'idEnfermeiro', 'dataConsumo')
    ordering = ('-idConsumo',)


@admin.register(MedicamentoDispensado)
class MedicamentoDispensadoAdmin(admin.ModelAdmin):
    list_display = ('idDispensacao', 'medicamento', 'quantidade',
                    'idFarmaceutico', 'idProntuario', 'dataDispensacao')
    ordering = ('-idDispensacao',)


admin.site.register(GestorMaterial)
admin.site.register(GestorMedicamento)
