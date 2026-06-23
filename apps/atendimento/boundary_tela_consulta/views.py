# Representa as Boundaries (Telas) do Módulo de Fluxo de Atendimento, controlando
# as telas e requisições de consultas e agendas.

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.acesso.decorators import perfis_permitidos
from apps.atendimento.boundary_tela_consulta.forms import (
    ConsultaForm,
    ReagendarForm,
    AgendaForm,
    ConsultarAgendaMedicoForm,
    ConsultarAgendaPacienteForm,
)
from apps.atendimento.control_ctr_consulta.services import CTRConsulta, CTRAgenda
from apps.atendimento.entity_atendimento.models import Consulta


# ----------------------------------------------------------------------
# Consultas
# ----------------------------------------------------------------------
@perfis_permitidos('recepcionista', 'medico')
def listar_consultas(request):
    return render(request, 'atendimento/consulta/listar.html', {
        'consultas': CTRConsulta.listar_consultas(),
        'titulo': 'Consultas',
    })


@perfis_permitidos('recepcionista')
def agendar_consulta(request):
    """Agenda uma nova consulta (UC-05).

    O agendamento é exclusivo da recepcionista; o paciente apenas consulta
    seus próprios agendamentos em "Minhas consultas".
    """

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            dados = dict(form.cleaned_data)
            try:
                consulta = CTRConsulta.agendar_consulta(dados)
                messages.success(request, 'Consulta agendada com sucesso.')
                return redirect('atendimento:consulta_detalhe', idConsulta=consulta.idConsulta)
            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)
    else:
        form = ConsultaForm()

    return render(request, 'atendimento/consulta/formulario.html', {
        'form': form,
        'titulo': 'Agendar consulta',
        'botao': 'Agendar',
    })


@perfis_permitidos('recepcionista', 'medico', 'paciente')
def detalhe_consulta(request, idConsulta):
    consulta = get_object_or_404(Consulta, idConsulta=idConsulta)

    # O paciente só pode ver as próprias consultas.
    if request.session.get('usuario_perfil') == 'paciente' and \
            consulta.idPaciente != request.session.get('usuario_id'):
        messages.error(request, 'Você só pode visualizar as suas próprias consultas.')
        return redirect('atendimento:agenda_paciente')

    return render(request, 'atendimento/consulta/detalhe.html', {
        'consulta': consulta,
        'titulo': f'Consulta {consulta.idConsulta}',
    })


@perfis_permitidos('recepcionista')
def reagendar_consulta(request, idConsulta):
    consulta = get_object_or_404(Consulta, idConsulta=idConsulta)

    if request.method == 'POST':
        form = ReagendarForm(request.POST)
        if form.is_valid():
            try:
                CTRConsulta.reagendar_consulta(
                    consulta,
                    form.cleaned_data['nova_data'],
                    form.cleaned_data['novo_horario'],
                )
                messages.success(request, 'Consulta reagendada com sucesso.')
                return redirect('atendimento:consulta_detalhe', idConsulta=consulta.idConsulta)
            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)
    else:
        form = ReagendarForm()

    return render(request, 'atendimento/consulta/reagendar.html', {
        'form': form,
        'consulta': consulta,
        'titulo': f'Reagendar consulta {consulta.idConsulta}',
        'botao': 'Reagendar',
    })


@perfis_permitidos('recepcionista')
def cancelar_consulta(request, idConsulta):
    consulta = get_object_or_404(Consulta, idConsulta=idConsulta)

    if request.method == 'POST':
        CTRConsulta.cancelar_consulta(consulta)
        messages.success(request, 'Consulta cancelada.')
        return redirect('atendimento:consulta_detalhe', idConsulta=consulta.idConsulta)

    return render(request, 'atendimento/consulta/cancelar.html', {
        'consulta': consulta,
        'titulo': f'Cancelar consulta {consulta.idConsulta}',
    })


@perfis_permitidos('medico')
def agenda_medico(request):
    """Consulta a agenda do médico logado (UC-19 - 'Minha agenda')."""

    # O médico vê a própria agenda: o idMedico vem da sessão (não é digitado),
    # restando apenas o filtro opcional por data.
    id_medico = request.session.get('usuario_id')

    form = ConsultarAgendaMedicoForm(request.GET or None)
    if 'idMedico' in form.fields:
        del form.fields['idMedico']

    data = None
    if request.GET and form.is_valid():
        data = form.cleaned_data.get('data')

    consultas = CTRConsulta.listar_por_medico(id_medico, data)

    return render(request, 'atendimento/consulta/agenda_medico.html', {
        'form': form,
        'consultas': consultas,
        'titulo': 'Minha agenda',
    })


@perfis_permitidos('paciente', 'recepcionista')
def agenda_paciente(request):
    """Consulta os agendamentos de um paciente (UC-04)."""

    # O paciente vê automaticamente os próprios agendamentos (escopo da sessão);
    # a recepcionista informa o paciente pelo formulário.
    if request.session.get('usuario_perfil') == 'paciente':
        consultas = CTRConsulta.listar_por_paciente(request.session.get('usuario_id'))
        return render(request, 'atendimento/consulta/agenda_paciente.html', {
            'form': None,
            'consultas': consultas,
            'titulo': 'Minhas consultas',
        })

    form = ConsultarAgendaPacienteForm(request.GET or None)
    consultas = None

    if request.GET and form.is_valid():
        consultas = CTRConsulta.listar_por_paciente(form.cleaned_data['idPaciente'])

    return render(request, 'atendimento/consulta/agenda_paciente.html', {
        'form': form,
        'consultas': consultas,
        'titulo': 'Agendamentos do paciente',
    })


# ----------------------------------------------------------------------
# Agendas
# ----------------------------------------------------------------------
@perfis_permitidos('recepcionista')
def listar_agendas(request):
    return render(request, 'atendimento/agenda/listar.html', {
        'agendas': CTRAgenda.listar_agendas(),
        'titulo': 'Agendas',
    })


@perfis_permitidos('recepcionista')
def criar_agenda(request):
    if request.method == 'POST':
        form = AgendaForm(request.POST)
        if form.is_valid():
            try:
                CTRAgenda.criar_agenda(
                    form.cleaned_data['data'],
                    form.cleaned_data['ocupacaoSalas'],
                )
                messages.success(request, 'Agenda criada com sucesso.')
                return redirect('atendimento:agenda_listar')
            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)
    else:
        form = AgendaForm()

    return render(request, 'atendimento/agenda/formulario.html', {
        'form': form,
        'titulo': 'Criar agenda',
        'botao': 'Criar',
    })
