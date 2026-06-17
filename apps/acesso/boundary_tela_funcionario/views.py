# Representa as Boundaries (Telas) do Módulo de Gestão de Acesso, controlando as
# telas e requisições de login, redefinição de senha e gestão de funcionários.

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from apps.acesso.decorators import perfis_permitidos
from apps.acesso.boundary_tela_funcionario.forms import (
    FORMS_POR_PERFIL,
    LoginForm,
    SolicitarRedefinicaoForm,
    NovaSenhaForm,
)
from apps.acesso.control_ctr_funcionario.services import (
    PERFIS,
    obter_ctr,
    CTRAutenticacao,
)

# Rótulos amigáveis para títulos das telas.
ROTULOS = {
    'recepcionista': 'Recepcionista',
    'medico': 'Médico',
    'enfermeiro': 'Enfermeiro',
    'farmaceutico': 'Farmacêutico',
    'gestor': 'Gestor',
}


def _validar_perfil(perfil):
    """Garante que o perfil informado na URL é válido."""
    if perfil not in PERFIS:
        raise Http404('Perfil de funcionário inválido.')


# ----------------------------------------------------------------------
# Autenticação (UC-01 / UC-02)
# ----------------------------------------------------------------------
def login_view(request):
    """Tela de login do sistema (UC-01)."""

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            resultado = CTRAutenticacao.autenticar(
                form.cleaned_data['email_ou_cpf'],
                form.cleaned_data['senha'],
            )

            if resultado:
                perfil, usuario = resultado
                request.session['usuario_id'] = usuario.pk
                request.session['usuario_perfil'] = perfil
                request.session['usuario_nome'] = usuario.nome
                messages.success(request, f'Bem-vindo(a), {usuario.nome}!')

                destino = request.POST.get('next') or request.GET.get('next')
                if destino and url_has_allowed_host_and_scheme(
                    destino, allowed_hosts=None
                ):
                    return redirect(destino)
                return redirect('home')

            messages.error(request, 'Credenciais inválidas.')
    else:
        form = LoginForm()

    return render(request, 'acesso/login.html', {
        'form': form,
        'titulo': 'Entrar no sistema',
        'next': request.GET.get('next', ''),
    })


def logout_view(request):
    """Encerra a sessão autenticada (UC-01 - logout)."""

    for chave in ('usuario_id', 'usuario_perfil', 'usuario_nome'):
        request.session.pop(chave, None)

    messages.info(request, 'Sessão encerrada.')
    return redirect('acesso:login')


def redefinir_senha_view(request):
    """Solicita o link de redefinição de senha por e-mail (UC-02, passo 1)."""

    if request.method == 'POST':
        form = SolicitarRedefinicaoForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            resultado = CTRAutenticacao.gerar_token_redefinicao(email)

            if resultado:
                token, _usuario = resultado
                link = request.build_absolute_uri(
                    reverse('acesso:redefinir_senha_confirmar', args=[token])
                )
                send_mail(
                    'Redefinição de senha — MedClin',
                    'Recebemos uma solicitação para redefinir a sua senha.\n\n'
                    f'Abra o link a seguir (válido por 30 minutos):\n{link}\n\n'
                    'Se não foi você, ignore este e-mail.',
                    None,
                    [email],
                    fail_silently=True,
                )

            # Mensagem genérica: não revela se o e-mail está ou não cadastrado.
            messages.success(
                request,
                'Se o e-mail estiver cadastrado, enviamos um link de '
                'redefinição (válido por 30 minutos).',
            )
            return redirect('acesso:login')
    else:
        form = SolicitarRedefinicaoForm()

    return render(request, 'acesso/redefinir_senha.html', {
        'form': form,
        'titulo': 'Redefinir senha',
    })


def redefinir_senha_confirmar_view(request, token):
    """Define a nova senha a partir do link recebido (UC-02, passo 2)."""

    # Valida o token antes de exibir ou processar o formulário.
    try:
        CTRAutenticacao.validar_token_redefinicao(token)
    except ValidationError as erro:
        for mensagem in erro.messages:
            messages.error(request, mensagem)
        return redirect('acesso:redefinir_senha')

    if request.method == 'POST':
        form = NovaSenhaForm(request.POST)

        if form.is_valid():
            try:
                CTRAutenticacao.redefinir_senha_com_token(
                    token, form.cleaned_data['nova_senha']
                )
                messages.success(
                    request, 'Senha redefinida com sucesso. Faça login.'
                )
                return redirect('acesso:login')
            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)
    else:
        form = NovaSenhaForm()

    return render(request, 'acesso/redefinir_senha_confirmar.html', {
        'form': form,
        'titulo': 'Definir nova senha',
    })


# ----------------------------------------------------------------------
# Gestão de funcionários (UC-08)
# ----------------------------------------------------------------------
@perfis_permitidos('gestor')
def listar_funcionarios(request, perfil):
    """Lista os funcionários de um perfil."""

    _validar_perfil(perfil)
    ctr = obter_ctr(perfil)

    return render(request, 'acesso/funcionario/listar.html', {
        'funcionarios': ctr.listar(),
        'perfil': perfil,
        'titulo': f'{ROTULOS[perfil]}s cadastrados',
    })


@perfis_permitidos('gestor')
def cadastrar_funcionario(request, perfil):
    """Cadastra um novo funcionário do perfil (UC-08)."""

    _validar_perfil(perfil)
    ctr = obter_ctr(perfil)
    FormClass = FORMS_POR_PERFIL[perfil]

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            try:
                obj = ctr.cadastrar(form.cleaned_data)
                messages.success(request, f'{ROTULOS[perfil]} cadastrado com sucesso.')
                return redirect('acesso:funcionario_detalhe', perfil=perfil, pk=obj.pk)
            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)
    else:
        form = FormClass()

    return render(request, 'acesso/funcionario/formulario.html', {
        'form': form,
        'perfil': perfil,
        'titulo': f'Cadastrar {ROTULOS[perfil].lower()}',
        'botao': 'Cadastrar',
    })


@perfis_permitidos('gestor')
def detalhe_funcionario(request, perfil, pk):
    """Exibe os dados de um funcionário."""

    _validar_perfil(perfil)
    ctr = obter_ctr(perfil)
    funcionario = get_object_or_404(ctr.model, pk=pk)

    return render(request, 'acesso/funcionario/detalhe.html', {
        'funcionario': funcionario,
        'perfil': perfil,
        'titulo': f'Detalhes do {ROTULOS[perfil].lower()}',
    })


@perfis_permitidos('gestor')
def editar_funcionario(request, perfil, pk):
    """Edita os dados de um funcionário."""

    _validar_perfil(perfil)
    ctr = obter_ctr(perfil)
    FormClass = FORMS_POR_PERFIL[perfil]
    funcionario = get_object_or_404(ctr.model, pk=pk)

    if request.method == 'POST':
        form = FormClass(request.POST, instance=funcionario)
        if form.is_valid():
            try:
                ctr.editar(funcionario, form.cleaned_data)
                messages.success(request, f'{ROTULOS[perfil]} atualizado com sucesso.')
                return redirect('acesso:funcionario_detalhe', perfil=perfil, pk=funcionario.pk)
            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)
    else:
        form = FormClass(instance=funcionario)

    return render(request, 'acesso/funcionario/formulario.html', {
        'form': form,
        'perfil': perfil,
        'funcionario': funcionario,
        'titulo': f'Editar {ROTULOS[perfil].lower()}',
        'botao': 'Salvar alterações',
    })


@perfis_permitidos('gestor')
def buscar_funcionario(request, perfil):
    """Busca funcionários por nome ou CPF."""

    _validar_perfil(perfil)
    ctr = obter_ctr(perfil)

    termo = request.GET.get('termo', '').strip()
    funcionarios = ctr.buscar(termo) if termo else ctr.model.objects.none()

    if termo and not funcionarios.exists():
        messages.warning(request, 'Nenhum funcionário encontrado.')

    return render(request, 'acesso/funcionario/buscar.html', {
        'funcionarios': funcionarios,
        'perfil': perfil,
        'termo': termo,
        'titulo': f'Buscar {ROTULOS[perfil].lower()}',
    })
