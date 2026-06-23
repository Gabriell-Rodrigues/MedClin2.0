# Boundaries (Telas) do Módulo Financeiro: registro de pagamento de consulta
# (UC-07, recepcionista) e relatório financeiro (UC-09 / UC-10, gestor).

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.acesso.decorators import perfis_permitidos
from apps.atendimento.entity_atendimento.models import Consulta
from apps.financeiro.boundary_tela_financeiro.forms import (
    PagamentoForm, RelatorioForm,
)
from apps.financeiro.control_ctr_pagamento.services import CTRFinanceiro


@perfis_permitidos('recepcionista')
def pagamentos_pendentes(request):
    """Lista as consultas que ainda não foram pagas (UC-07)."""
    return render(request, 'financeiro/pagamentos_pendentes.html', {
        'consultas': CTRFinanceiro.listar_pendentes(),
        'titulo': 'Pagamentos pendentes',
    })


@perfis_permitidos('recepcionista')
def registrar_pagamento(request, idConsulta):
    """Registra o pagamento de uma consulta (UC-07)."""
    consulta = get_object_or_404(Consulta, idConsulta=idConsulta)

    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            try:
                CTRFinanceiro.registrar_pagamento(
                    consulta,
                    form.cleaned_data['valor'],
                    form.cleaned_data['formaPagamento'],
                )
                messages.success(request, 'Pagamento registrado com sucesso.')
                return redirect('financeiro:pagamentos_pendentes')
            except ValidationError as erro:
                for m in erro.messages:
                    messages.error(request, m)
    else:
        form = PagamentoForm()

    return render(request, 'financeiro/registrar_pagamento.html', {
        'form': form,
        'consulta': consulta,
        'titulo': f'Registrar pagamento — Consulta {consulta.idConsulta}',
        'botao': 'Confirmar pagamento',
    })


@perfis_permitidos('gestor')
def relatorio_financeiro(request):
    """Relatório financeiro por período (UC-09 / UC-10)."""
    form = RelatorioForm(request.GET or None)
    relatorio = None

    if not request.GET or form.is_valid():
        relatorio = CTRFinanceiro.gerar_relatorio(
            form.cleaned_data.get('inicio') if form.is_valid() else None,
            form.cleaned_data.get('fim') if form.is_valid() else None,
        )

    return render(request, 'financeiro/relatorio.html', {
        'form': form,
        'relatorio': relatorio,
        'titulo': 'Relatório financeiro',
    })
