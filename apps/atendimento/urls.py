# Define as rotas do Módulo de Fluxo de Atendimento e direciona cada URL para sua
# view correspondente.

from django.urls import path

from apps.atendimento.boundary_tela_consulta import views


app_name = 'atendimento'


urlpatterns = [
    # Consultas
    path('consultas/', views.listar_consultas, name='consulta_listar'),
    path('consultas/nova/', views.agendar_consulta, name='consulta_agendar'),
    path('consultas/agenda-medico/', views.agenda_medico, name='agenda_medico'),
    path('consultas/agenda-paciente/', views.agenda_paciente, name='agenda_paciente'),
    path('consultas/<int:idConsulta>/', views.detalhe_consulta, name='consulta_detalhe'),
    path('consultas/<int:idConsulta>/reagendar/', views.reagendar_consulta, name='consulta_reagendar'),
    path('consultas/<int:idConsulta>/cancelar/', views.cancelar_consulta, name='consulta_cancelar'),

    # Agendas
    path('agendas/', views.listar_agendas, name='agenda_listar'),
    path('agendas/nova/', views.criar_agenda, name='agenda_criar'),
]
