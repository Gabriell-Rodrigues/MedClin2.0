# Define as rotas do Módulo de Prontuário Eletrônico e direciona cada URL para
# sua view correspondente.

from django.urls import path

from apps.prontuario.boundary_tela_prontuario import views


app_name = 'prontuario'


urlpatterns = [
    path(
        'prontuarios/',
        views.listar_prontuarios,
        name='prontuario_listar'
    ),

    path(
        'meu-prontuario/',
        views.meu_prontuario,
        name='meu_prontuario'
    ),

    path(
        'prontuarios/novo/',
        views.inicializar_prontuario,
        name='prontuario_inicializar'
    ),

    path(
        'prontuarios/<int:idProntuario>/',
        views.detalhe_prontuario,
        name='prontuario_detalhe'
    ),

    path(
        'prontuarios/<int:idProntuario>/evolucao/',
        views.registrar_evolucao,
        name='prontuario_registrar_evolucao'
    ),

    path(
        'prontuarios/<int:idProntuario>/acesso/',
        views.conceder_acesso,
        name='prontuario_conceder_acesso'
    ),

    path(
        'prontuarios/<int:idProntuario>/acesso/verificar/',
        views.verificar_acesso,
        name='prontuario_verificar_acesso'
    ),
]
