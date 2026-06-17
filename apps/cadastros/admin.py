# Registra os models do módulo de cadastros para gerenciamento no painel administrativo do Django.

from django.contrib import admin

from apps.cadastros.entity_paciente.models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        'idPaciente',
        'nome',
        'cpf',
        'telefone',
        'email',
        'dataNascimento',
    )

    search_fields = (
        'nome',
        'cpf',
        'email',
    )

    list_filter = (
        'dataNascimento',
    )

    ordering = (
        'nome',
    )