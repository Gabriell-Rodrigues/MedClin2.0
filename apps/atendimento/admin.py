# Registra os models do Módulo de Fluxo de Atendimento no painel administrativo.

from django.contrib import admin

from apps.atendimento.entity_atendimento.models import (
    Agenda,
    RecepcionistaAgenda,
    Consulta,
)


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ('idAgenda', 'data', 'ocupacaoSalas')
    list_filter = ('data',)
    ordering = ('-data',)


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('idConsulta', 'data', 'horario', 'status',
                    'idPaciente', 'idMedico')
    list_filter = ('status', 'data')
    search_fields = ('idPaciente', 'idMedico')
    ordering = ('-data', '-horario')


@admin.register(RecepcionistaAgenda)
class RecepcionistaAgendaAdmin(admin.ModelAdmin):
    list_display = ('idRecepcionista', 'agenda')
    search_fields = ('idRecepcionista',)
