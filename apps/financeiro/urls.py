# Rotas do Módulo Financeiro (UC-07, UC-09, UC-10).

from django.urls import path

from apps.financeiro.boundary_tela_financeiro import views


app_name = 'financeiro'


urlpatterns = [
    path('pagamentos/', views.pagamentos_pendentes, name='pagamentos_pendentes'),
    path('pagamentos/<int:idConsulta>/', views.registrar_pagamento,
         name='registrar_pagamento'),
    path('relatorio/', views.relatorio_financeiro, name='relatorio'),
]
