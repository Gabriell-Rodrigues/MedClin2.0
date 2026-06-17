# Representa a Boundary TelaProntuario, controlando as telas e as requisições
# relacionadas ao prontuário eletrônico.

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.acesso.decorators import perfis_permitidos
from apps.prontuario.boundary_tela_prontuario.forms import (
    InicializarProntuarioForm,
    EvolucaoForm,
    AcessoProntuarioForm,
)
from apps.prontuario.control_ctr_prontuario.services import CTRProntuario
from apps.prontuario.entity_prontuario.models import Prontuario


@perfis_permitidos('medico', 'enfermeiro', 'farmaceutico')
def listar_prontuarios(request):
    """
    Exibe a lista de prontuários cadastrados.
    """

    prontuarios = CTRProntuario.listar_prontuarios()

    return render(
        request,
        'prontuario/prontuario/listar.html',
        {
            'prontuarios': prontuarios,
            'titulo': 'Prontuários',
        }
    )


@perfis_permitidos('medico', 'recepcionista')
def inicializar_prontuario(request):
    """
    Exibe o formulário e realiza a inicialização de um novo prontuário (UC-06).
    """

    if request.method == 'POST':
        form = InicializarProntuarioForm(request.POST)

        if form.is_valid():
            paciente = None
            id_paciente = form.cleaned_data.get('idPaciente')

            if id_paciente:
                from apps.cadastros.entity_paciente.models import Paciente
                paciente = Paciente.objects.filter(idPaciente=id_paciente).first()

            try:
                prontuario = CTRProntuario.inicializar_prontuario(paciente)

                messages.success(
                    request,
                    'Prontuário inicializado com sucesso.'
                )

                return redirect(
                    'prontuario:prontuario_detalhe',
                    idProntuario=prontuario.idProntuario
                )

            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)

    else:
        form = InicializarProntuarioForm()

    return render(
        request,
        'prontuario/prontuario/inicializar.html',
        {
            'form': form,
            'titulo': 'Inicializar prontuário',
            'botao': 'Inicializar',
        }
    )


@perfis_permitidos('paciente')
def meu_prontuario(request):
    """Atalho do paciente para o próprio prontuário."""

    from apps.cadastros.entity_paciente.models import Paciente

    paciente = Paciente.objects.filter(
        idPaciente=request.session.get('usuario_id')
    ).first()

    if not paciente or not paciente.idProntuario:
        messages.info(request, 'Você ainda não possui um prontuário cadastrado.')
        return redirect('home')

    return redirect(
        'prontuario:prontuario_detalhe',
        idProntuario=paciente.idProntuario
    )


@perfis_permitidos('medico', 'enfermeiro', 'farmaceutico', 'paciente')
def detalhe_prontuario(request, idProntuario):
    """
    Exibe os dados completos de um prontuário, incluindo o paciente vinculado,
    os profissionais autorizados e o histórico de evoluções.
    """

    prontuario = get_object_or_404(
        Prontuario,
        idProntuario=idProntuario
    )

    # O paciente só pode visualizar o próprio prontuário.
    if request.session.get('usuario_perfil') == 'paciente':
        from apps.cadastros.entity_paciente.models import Paciente
        paciente = Paciente.objects.filter(
            idPaciente=request.session.get('usuario_id')
        ).first()
        if not paciente or paciente.idProntuario != prontuario.idProntuario:
            messages.error(request, 'Você só pode visualizar o seu próprio prontuário.')
            return redirect('home')

    return render(
        request,
        'prontuario/prontuario/detalhe.html',
        {
            'prontuario': prontuario,
            'paciente': CTRProntuario.obter_paciente_vinculado(prontuario),
            'autorizados': CTRProntuario.listar_profissionais_autorizados(prontuario),
            'titulo': f'Prontuário {prontuario.idProntuario}',
        }
    )


@perfis_permitidos('medico')
def registrar_evolucao(request, idProntuario):
    """
    Exibe o formulário e registra a evolução clínica do prontuário (UC-12).
    """

    prontuario = get_object_or_404(
        Prontuario,
        idProntuario=idProntuario
    )

    if request.method == 'POST':
        form = EvolucaoForm(request.POST)

        if form.is_valid():
            try:
                CTRProntuario.registrar_evolucao(
                    prontuario,
                    form.cleaned_data['idMedico'],
                    form.cleaned_data['diagnostico'],
                    form.cleaned_data['observacoes'],
                    form.cleaned_data['prescricaoAtiva'],
                )

                messages.success(
                    request,
                    'Evolução registrada com sucesso.'
                )

                return redirect(
                    'prontuario:prontuario_detalhe',
                    idProntuario=prontuario.idProntuario
                )

            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)

    else:
        form = EvolucaoForm()

    return render(
        request,
        'prontuario/prontuario/evolucao.html',
        {
            'form': form,
            'prontuario': prontuario,
            'titulo': f'Registrar evolução - Prontuário {prontuario.idProntuario}',
            'botao': 'Registrar evolução',
        }
    )


@perfis_permitidos('medico')
def conceder_acesso(request, idProntuario):
    """
    Concede a um profissional acesso autorizado ao prontuário (UC-11).
    """

    prontuario = get_object_or_404(
        Prontuario,
        idProntuario=idProntuario
    )

    if request.method == 'POST':
        form = AcessoProntuarioForm(request.POST)

        if form.is_valid():
            try:
                criado = CTRProntuario.conceder_acesso(
                    prontuario,
                    form.cleaned_data['perfil'],
                    form.cleaned_data['idProfissional'],
                )

                if criado:
                    messages.success(request, 'Acesso concedido com sucesso.')
                else:
                    messages.info(request, 'Este profissional já possuía acesso.')

                return redirect(
                    'prontuario:prontuario_detalhe',
                    idProntuario=prontuario.idProntuario
                )

            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)

    else:
        form = AcessoProntuarioForm()

    return render(
        request,
        'prontuario/prontuario/acesso.html',
        {
            'form': form,
            'prontuario': prontuario,
            'titulo': f'Conceder acesso - Prontuário {prontuario.idProntuario}',
            'botao': 'Conceder acesso',
        }
    )


@perfis_permitidos('medico', 'enfermeiro', 'farmaceutico')
def verificar_acesso(request, idProntuario):
    """
    Verifica se um profissional possui acesso autorizado ao prontuário (UC-11).
    """

    prontuario = get_object_or_404(
        Prontuario,
        idProntuario=idProntuario
    )

    resultado = None
    form = AcessoProntuarioForm(request.GET or None)

    if request.GET and form.is_valid():
        try:
            tem_acesso = CTRProntuario.verificar_acesso(
                prontuario,
                form.cleaned_data['perfil'],
                form.cleaned_data['idProfissional'],
            )

            resultado = {
                'perfil': form.cleaned_data['perfil'],
                'idProfissional': form.cleaned_data['idProfissional'],
                'tem_acesso': tem_acesso,
            }

        except ValidationError as erro:
            for mensagem in erro.messages:
                messages.error(request, mensagem)

    return render(
        request,
        'prontuario/prontuario/verificar_acesso.html',
        {
            'form': form,
            'prontuario': prontuario,
            'resultado': resultado,
            'titulo': f'Verificar acesso - Prontuário {prontuario.idProntuario}',
        }
    )
