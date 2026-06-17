# Controle de acesso por perfil (RBAC) do MedClin.
#
# Implementado na camada de apresentação (boundary), sem alterar models,
# services ou regras de negócio. As permissões seguem a Matriz de Atores x
# Casos de Uso da documentação (Descrição de Casos de Uso, Seção 3).
#
# Sessão usada (definida no login - UC-01):
#   request.session['usuario_id'], ['usuario_perfil'], ['usuario_nome']

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def _esta_logado(request):
    return bool(request.session.get('usuario_id'))


def _redirecionar_login(request):
    """Envia para o login preservando o destino pretendido (?next=)."""
    login_url = reverse('acesso:login')
    destino = request.get_full_path()
    if url_has_allowed_host_and_scheme(destino, allowed_hosts=None):
        return redirect(f'{login_url}?next={destino}')
    return redirect(login_url)


def login_obrigatorio(view):
    """Exige que exista uma sessão autenticada (qualquer perfil)."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not _esta_logado(request):
            messages.warning(request, 'Faça login para acessar esta página.')
            return _redirecionar_login(request)
        return view(request, *args, **kwargs)

    return wrapper


def perfis_permitidos(*perfis):
    """
    Restringe a view aos perfis informados (UC correspondente).

    - Não logado  -> redireciona para o login (com ?next=).
    - Logado sem permissão -> página 403 (Acesso negado).
    """

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not _esta_logado(request):
                messages.warning(request, 'Faça login para acessar esta página.')
                return _redirecionar_login(request)

            if request.session.get('usuario_perfil') not in perfis:
                return render(
                    request,
                    'acesso/403.html',
                    {
                        'titulo': 'Acesso negado',
                        'perfis_necessarios': perfis,
                        'perfil_atual': request.session.get('usuario_perfil'),
                    },
                    status=403,
                )

            return view(request, *args, **kwargs)

        return wrapper

    return decorator
