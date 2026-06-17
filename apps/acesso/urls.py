# Define as rotas do Módulo de Gestão de Acesso (login, redefinição de senha e
# gestão de funcionários) e direciona cada URL para sua view correspondente.

from django.urls import path

from apps.acesso.boundary_tela_funcionario import views


app_name = 'acesso'


urlpatterns = [
    # Autenticação (UC-01 / UC-02)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('senha/redefinir/', views.redefinir_senha_view, name='redefinir_senha'),
    path('senha/redefinir/<str:token>/', views.redefinir_senha_confirmar_view, name='redefinir_senha_confirmar'),

    # Gestão de funcionários por perfil (UC-08)
    path('funcionarios/<str:perfil>/', views.listar_funcionarios, name='funcionario_listar'),
    path('funcionarios/<str:perfil>/novo/', views.cadastrar_funcionario, name='funcionario_cadastrar'),
    path('funcionarios/<str:perfil>/buscar/', views.buscar_funcionario, name='funcionario_buscar'),
    path('funcionarios/<str:perfil>/<int:pk>/', views.detalhe_funcionario, name='funcionario_detalhe'),
    path('funcionarios/<str:perfil>/<int:pk>/editar/', views.editar_funcionario, name='funcionario_editar'),
]
