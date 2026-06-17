# Registra os models do Módulo de Prontuário Eletrônico para gerenciamento no
# painel administrativo do Django.

from django.contrib import admin

from apps.prontuario.entity_prontuario.models import (
    Prontuario,
    MedicoProntuario,
    EnfermeiroProntuario,
    FarmaceuticoProntuario,
)


@admin.register(Prontuario)
class ProntuarioAdmin(admin.ModelAdmin):
    list_display = (
        'idProntuario',
        'dataCriacao',
        'diagnostico',
    )

    search_fields = (
        'idProntuario',
        'diagnostico',
        'observacoes',
    )

    list_filter = (
        'dataCriacao',
    )

    ordering = (
        '-idProntuario',
    )


@admin.register(MedicoProntuario)
class MedicoProntuarioAdmin(admin.ModelAdmin):
    list_display = ('idMedico', 'prontuario')
    search_fields = ('idMedico',)


@admin.register(EnfermeiroProntuario)
class EnfermeiroProntuarioAdmin(admin.ModelAdmin):
    list_display = ('idEnfermeiro', 'prontuario')
    search_fields = ('idEnfermeiro',)


@admin.register(FarmaceuticoProntuario)
class FarmaceuticoProntuarioAdmin(admin.ModelAdmin):
    list_display = ('idFarmaceutico', 'prontuario')
    search_fields = ('idFarmaceutico',)
