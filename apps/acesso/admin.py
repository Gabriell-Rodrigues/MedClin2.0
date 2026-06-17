# Registra os models do Módulo de Gestão de Acesso no painel administrativo.

from django.contrib import admin

from apps.acesso.entity_funcionario.models import (
    Recepcionista,
    Medico,
    Enfermeiro,
    Farmaceutico,
    Gestor,
)


@admin.register(Recepcionista)
class RecepcionistaAdmin(admin.ModelAdmin):
    list_display = ('idRecepcionista', 'nome', 'cpf', 'email', 'telefone')
    search_fields = ('nome', 'cpf', 'email')
    ordering = ('nome',)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('idMedico', 'nome', 'cpf', 'crm', 'especializacao', 'email')
    search_fields = ('nome', 'cpf', 'crm', 'especializacao')
    ordering = ('nome',)


@admin.register(Enfermeiro)
class EnfermeiroAdmin(admin.ModelAdmin):
    list_display = ('idEnfermeiro', 'nome', 'cpf', 'coren', 'email')
    search_fields = ('nome', 'cpf', 'coren')
    ordering = ('nome',)


@admin.register(Farmaceutico)
class FarmaceuticoAdmin(admin.ModelAdmin):
    list_display = ('idFarmaceutico', 'nome', 'cpf', 'crf', 'email')
    search_fields = ('nome', 'cpf', 'crf')
    ordering = ('nome',)


@admin.register(Gestor)
class GestorAdmin(admin.ModelAdmin):
    list_display = ('idGestor', 'nome', 'cpf', 'email', 'telefone')
    search_fields = ('nome', 'cpf', 'email')
    ordering = ('nome',)
