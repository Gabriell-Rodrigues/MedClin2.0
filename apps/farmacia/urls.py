# Define as rotas do Módulo Farmacêutico e direciona cada URL para sua view.

from django.urls import path

from apps.farmacia.boundary_tela_estoque import views


app_name = 'farmacia'


urlpatterns = [
    # Atalhos de listagem por tipo (usados na navegação).
    path('medicamentos/', views.listar_itens, {'tipo': 'medicamento'}, name='medicamento_listar'),
    path('materiais/', views.listar_itens, {'tipo': 'material'}, name='material_listar'),

    # Visão geral dos estoques (UC-20)
    path('estoques/', views.gerenciar_estoque, name='estoque_gerenciar'),

    # Caixa de notificações do gestor (reposições / estoque mínimo) (UC-20)
    path('notificacoes/', views.notificacoes_gestor, name='notificacoes_gestor'),
    path('notificacoes/<str:tipo>/<int:pk>/atender/', views.atender_reposicao,
         name='atender_reposicao'),

    # CRUD genérico de itens de estoque (tipo = material | medicamento)
    path('itens/<str:tipo>/', views.listar_itens, name='item_listar'),
    path('itens/<str:tipo>/novo/', views.cadastrar_item, name='item_cadastrar'),
    path('itens/<str:tipo>/verificar/', views.verificar_estoque, name='item_verificar'),
    path('itens/<str:tipo>/<int:pk>/', views.detalhe_item, name='item_detalhe'),
    path('itens/<str:tipo>/<int:pk>/editar/', views.editar_item, name='item_editar'),
    path('itens/<str:tipo>/<int:pk>/lote/', views.adicionar_lote, name='item_lote'),
    path('itens/<str:tipo>/<int:pk>/reposicao/', views.solicitar_reposicao, name='item_reposicao'),

    # Operações específicas
    path('medicamentos/<int:pk>/dispensar/', views.dispensar_medicamento, name='medicamento_dispensar'),
    path('materiais/<int:pk>/consumo/', views.registrar_consumo, name='material_consumo'),
]
