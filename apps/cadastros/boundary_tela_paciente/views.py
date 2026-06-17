# Representa a Boundary TelaPaciente, controlando as telas e as requisições relacionadas aos pacientes.

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.acesso.decorators import perfis_permitidos
from apps.cadastros.boundary_tela_paciente.forms import (
    PacienteForm,
    BuscaPacienteCPFForm,
    BuscaPacienteNomeForm,
)
from apps.cadastros.control_ctr_paciente.services import CTRPaciente
from apps.cadastros.entity_paciente.models import Paciente


@perfis_permitidos('recepcionista')
def listar_pacientes(request):
    """
    Exibe a lista de pacientes cadastrados.
    """

    pacientes = CTRPaciente.listar_pacientes()

    return render(
        request,
        'cadastros/paciente/listar.html',
        {
            'pacientes': pacientes,
            'titulo': 'Pacientes cadastrados',
        }
    )


@perfis_permitidos('recepcionista')
def cadastrar_paciente(request):
    """
    Exibe o formulário e realiza o cadastro de um novo paciente.
    """

    if request.method == 'POST':
        form = PacienteForm(request.POST)

        if form.is_valid():
            try:
                paciente = CTRPaciente.cadastrar_paciente(form.cleaned_data)

                messages.success(
                    request,
                    'Paciente cadastrado com sucesso.'
                )

                return redirect(
                    'cadastros:paciente_detalhe',
                    idPaciente=paciente.idPaciente
                )

            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)

    else:
        form = PacienteForm()

    return render(
        request,
        'cadastros/paciente/formulario.html',
        {
            'form': form,
            'titulo': 'Cadastrar paciente',
            'botao': 'Cadastrar',
        }
    )


@perfis_permitidos('recepcionista')
def detalhe_paciente(request, idPaciente):
    """
    Exibe os dados completos de um paciente.
    """

    paciente = get_object_or_404(
        Paciente,
        idPaciente=idPaciente
    )

    return render(
        request,
        'cadastros/paciente/detalhe.html',
        {
            'paciente': paciente,
            'titulo': 'Detalhes do paciente',
        }
    )


@perfis_permitidos('recepcionista')
def editar_paciente(request, idPaciente):
    """
    Exibe o formulário e realiza a edição dos dados de um paciente.
    """

    paciente = get_object_or_404(
        Paciente,
        idPaciente=idPaciente
    )

    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)

        if form.is_valid():
            try:
                paciente = CTRPaciente.editar_paciente(
                    paciente,
                    form.cleaned_data
                )

                messages.success(
                    request,
                    'Paciente atualizado com sucesso.'
                )

                return redirect(
                    'cadastros:paciente_detalhe',
                    idPaciente=paciente.idPaciente
                )

            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)

    else:
        form = PacienteForm(instance=paciente)

    return render(
        request,
        'cadastros/paciente/formulario.html',
        {
            'form': form,
            'titulo': 'Editar paciente',
            'botao': 'Salvar alterações',
            'paciente': paciente,
        }
    )


@perfis_permitidos('recepcionista')
def buscar_paciente_cpf(request):
    """
    Busca um paciente pelo CPF.
    """

    form = BuscaPacienteCPFForm(request.GET or None)
    pacientes = []

    if request.GET and form.is_valid():
        cpf = form.cleaned_data.get('cpf')
        paciente = CTRPaciente.buscar_por_cpf(cpf)

        if paciente:
            pacientes = [paciente]
        else:
            messages.warning(
                request,
                'Nenhum paciente encontrado com este CPF.'
            )

    return render(
        request,
        'cadastros/paciente/buscar_cpf.html',
        {
            'form': form,
            'pacientes': pacientes,
            'titulo': 'Buscar paciente por CPF',
        }
    )


@perfis_permitidos('recepcionista')
def buscar_paciente_nome(request):
    """
    Busca pacientes pelo nome.
    """

    form = BuscaPacienteNomeForm(request.GET or None)
    pacientes = Paciente.objects.none()

    if request.GET and form.is_valid():
        nome = form.cleaned_data.get('nome')
        pacientes = CTRPaciente.buscar_por_nome(nome)

        if not pacientes.exists():
            messages.warning(
                request,
                'Nenhum paciente encontrado com este nome.'
            )

    return render(
        request,
        'cadastros/paciente/buscar_nome.html',
        {
            'form': form,
            'pacientes': pacientes,
            'titulo': 'Buscar paciente por nome',
        }
    )