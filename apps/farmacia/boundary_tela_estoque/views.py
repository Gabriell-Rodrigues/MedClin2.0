# Representa as Boundaries (Telas) do Módulo Farmacêutico, controlando as telas e
# requisições de estoque, dispensação, consumo, reposição e gestão de estoques.

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.acesso.decorators import perfis_permitidos
from apps.farmacia.boundary_tela_estoque.forms import (
    MaterialForm,
    MedicamentoForm,
    LoteForm,
    DispensarForm,
    ConsumoForm,
    ReposicaoForm,
)
from apps.farmacia.control_ctr_estoque.services import CTRMateriais, CTRMedicamento

# Registro tipo -> controle, formulário e rótulos.
ITENS = {
    'material': {
        'ctr': CTRMateriais, 'form': MaterialForm,
        'label': 'Material', 'plural': 'Materiais',
    },
    'medicamento': {
        'ctr': CTRMedicamento, 'form': MedicamentoForm,
        'label': 'Medicamento', 'plural': 'Medicamentos',
    },
}


def _cfg(tipo):
    cfg = ITENS.get(tipo)
    if cfg is None:
        raise Http404('Tipo de item inválido.')
    return cfg


# ----------------------------------------------------------------------
# CRUD de itens de estoque (genérico para material/medicamento)
# ----------------------------------------------------------------------
@perfis_permitidos('enfermeiro', 'farmaceutico', 'gestor')
def listar_itens(request, tipo):
    cfg = _cfg(tipo)
    return render(request, 'farmacia/estoque/listar.html', {
        'itens': cfg['ctr'].listar(),
        'tipo': tipo,
        'titulo': cfg['plural'],
    })


@perfis_permitidos('gestor')
def cadastrar_item(request, tipo):
    cfg = _cfg(tipo)
    if request.method == 'POST':
        form = cfg['form'](request.POST)
        if form.is_valid():
            try:
                item = cfg['ctr'].cadastrar(form.cleaned_data)
                messages.success(request, f'{cfg["label"]} cadastrado com sucesso.')
                return redirect('farmacia:item_detalhe', tipo=tipo, pk=item.pk)
            except ValidationError as erro:
                for m in erro.messages:
                    messages.error(request, m)
    else:
        form = cfg['form']()
    return render(request, 'farmacia/estoque/formulario.html', {
        'form': form, 'tipo': tipo,
        'titulo': f'Cadastrar {cfg["label"].lower()}', 'botao': 'Cadastrar',
    })


@perfis_permitidos('enfermeiro', 'farmaceutico', 'gestor')
def detalhe_item(request, tipo, pk):
    cfg = _cfg(tipo)
    item = get_object_or_404(cfg['ctr'].model, pk=pk)
    return render(request, 'farmacia/estoque/detalhe.html', {
        'item': item, 'tipo': tipo,
        'titulo': f'{cfg["label"]}: {item.nome}',
    })


@perfis_permitidos('gestor')
def editar_item(request, tipo, pk):
    cfg = _cfg(tipo)
    item = get_object_or_404(cfg['ctr'].model, pk=pk)
    if request.method == 'POST':
        form = cfg['form'](request.POST, instance=item)
        if form.is_valid():
            try:
                cfg['ctr'].editar(item, form.cleaned_data)
                messages.success(request, f'{cfg["label"]} atualizado com sucesso.')
                return redirect('farmacia:item_detalhe', tipo=tipo, pk=item.pk)
            except ValidationError as erro:
                for m in erro.messages:
                    messages.error(request, m)
    else:
        form = cfg['form'](instance=item)
    return render(request, 'farmacia/estoque/formulario.html', {
        'form': form, 'tipo': tipo, 'item': item,
        'titulo': f'Editar {cfg["label"].lower()}', 'botao': 'Salvar alterações',
    })


@perfis_permitidos('gestor')
def adicionar_lote(request, tipo, pk):
    """Inserção de novo lote pelo gestor (UC-20)."""
    cfg = _cfg(tipo)
    item = get_object_or_404(cfg['ctr'].model, pk=pk)
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            try:
                cfg['ctr'].adicionar_lote(
                    item,
                    form.cleaned_data['quantidade'],
                    form.cleaned_data.get('numeroLote'),
                    form.cleaned_data.get('dataValidade'),
                )
                messages.success(request, 'Lote adicionado ao estoque.')
                return redirect('farmacia:item_detalhe', tipo=tipo, pk=item.pk)
            except ValidationError as erro:
                for m in erro.messages:
                    messages.error(request, m)
    else:
        form = LoteForm()
    return render(request, 'farmacia/estoque/acao.html', {
        'form': form, 'tipo': tipo, 'item': item,
        'titulo': f'Adicionar lote - {item.nome}', 'botao': 'Adicionar',
    })


@perfis_permitidos('enfermeiro', 'farmaceutico')
def solicitar_reposicao(request, tipo, pk):
    """Solicita reposição ao gestor (UC-14 / UC-17)."""
    cfg = _cfg(tipo)
    item = get_object_or_404(cfg['ctr'].model, pk=pk)
    if request.method == 'POST':
        form = ReposicaoForm(request.POST)
        if form.is_valid():
            try:
                cfg['ctr'].solicitar_reposicao(
                    item,
                    form.cleaned_data['quantidade'],
                    form.cleaned_data.get('justificativa', ''),
                    form.cleaned_data.get('idSolicitante'),
                )
                messages.success(request, 'Solicitação de reposição registrada.')
                return redirect('farmacia:item_detalhe', tipo=tipo, pk=item.pk)
            except ValidationError as erro:
                for m in erro.messages:
                    messages.error(request, m)
    else:
        form = ReposicaoForm()
    return render(request, 'farmacia/estoque/acao.html', {
        'form': form, 'tipo': tipo, 'item': item,
        'titulo': f'Solicitar reposição - {item.nome}', 'botao': 'Solicitar',
    })


@perfis_permitidos('enfermeiro', 'farmaceutico', 'gestor')
def verificar_estoque(request, tipo):
    """Verifica o estoque, destacando itens críticos (UC-15 / UC-16)."""
    cfg = _cfg(tipo)
    itens = cfg['ctr'].listar()
    criticos = cfg['ctr'].listar_criticos()
    return render(request, 'farmacia/estoque/verificar.html', {
        'itens': itens, 'criticos': criticos, 'tipo': tipo,
        'titulo': f'Estoque de {cfg["plural"].lower()}',
    })


# ----------------------------------------------------------------------
# Operações específicas
# ----------------------------------------------------------------------
@perfis_permitidos('farmaceutico')
def dispensar_medicamento(request, pk):
    """Dispensação de medicamento (UC-13)."""
    medicamento = get_object_or_404(CTRMedicamento.model, pk=pk)
    if request.method == 'POST':
        form = DispensarForm(request.POST)
        if form.is_valid():
            try:
                CTRMedicamento.dispensar(
                    medicamento,
                    form.cleaned_data['quantidade'],
                    form.cleaned_data['idFarmaceutico'],
                    form.cleaned_data.get('idProntuario'),
                )
                messages.success(request, 'Medicamento dispensado com sucesso.')
                return redirect('farmacia:item_detalhe', tipo='medicamento', pk=medicamento.pk)
            except ValidationError as erro:
                for m in erro.messages:
                    messages.error(request, m)
    else:
        form = DispensarForm()
    return render(request, 'farmacia/estoque/acao.html', {
        'form': form, 'tipo': 'medicamento', 'item': medicamento,
        'titulo': f'Dispensar - {medicamento.nome}', 'botao': 'Dispensar',
    })


@perfis_permitidos('enfermeiro')
def registrar_consumo(request, pk):
    """Registro de consumo de material por enfermeiro."""
    material = get_object_or_404(CTRMateriais.model, pk=pk)
    if request.method == 'POST':
        form = ConsumoForm(request.POST)
        if form.is_valid():
            try:
                CTRMateriais.registrar_consumo(
                    material,
                    form.cleaned_data['quantidade'],
                    form.cleaned_data['idEnfermeiro'],
                )
                messages.success(request, 'Consumo de material registrado.')
                return redirect('farmacia:item_detalhe', tipo='material', pk=material.pk)
            except ValidationError as erro:
                for m in erro.messages:
                    messages.error(request, m)
    else:
        form = ConsumoForm()
    return render(request, 'farmacia/estoque/acao.html', {
        'form': form, 'tipo': 'material', 'item': material,
        'titulo': f'Registrar consumo - {material.nome}', 'botao': 'Registrar',
    })


@perfis_permitidos('gestor')
def gerenciar_estoque(request):
    """Visão geral dos estoques para o gestor (UC-20)."""
    return render(request, 'farmacia/estoque/gerenciar.html', {
        'materiais': CTRMateriais.listar(),
        'medicamentos': CTRMedicamento.listar(),
        'materiais_criticos': CTRMateriais.listar_criticos(),
        'medicamentos_criticos': CTRMedicamento.listar_criticos(),
        'titulo': 'Gerenciar estoques',
    })
