# Define as rotas do módulo de cadastros e direciona cada URL para sua view correspondente.

from django.urls import path

from apps.cadastros.boundary_tela_paciente import views


app_name = 'cadastros'


urlpatterns = [
    path(
        'pacientes/',
        views.listar_pacientes,
        name='paciente_listar'
    ),

    path(
        'pacientes/novo/',
        views.cadastrar_paciente,
        name='paciente_cadastrar'
    ),

    path(
        'pacientes/buscar/cpf/',
        views.buscar_paciente_cpf,
        name='paciente_buscar_cpf'
    ),

    path(
        'pacientes/buscar/nome/',
        views.buscar_paciente_nome,
        name='paciente_buscar_nome'
    ),

    path(
        'pacientes/<int:idPaciente>/',
        views.detalhe_paciente,
        name='paciente_detalhe'
    ),

    path(
        'pacientes/<int:idPaciente>/editar/',
        views.editar_paciente,
        name='paciente_editar'
    ),
]