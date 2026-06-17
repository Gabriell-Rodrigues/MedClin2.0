# Representa as Boundaries (Telas) do Módulo Farmacêutico, contendo os formulários
# de cadastro de itens, entrada de lote, dispensação, consumo e reposição.

from django import forms

from apps.farmacia.entity_estoque.models import Material, Medicamento


class _ItemEstoqueForm(forms.ModelForm):
    campos = ['nome', 'descricao', 'numeroLote', 'quantidadeEstoque',
              'quantidadeMinima', 'dataValidade']
    rotulos = {
        'numeroLote': 'Número do lote',
        'quantidadeEstoque': 'Quantidade em estoque',
        'quantidadeMinima': 'Quantidade mínima',
        'dataValidade': 'Data de validade',
    }
    widgets_comuns = {'dataValidade': forms.DateInput(attrs={'type': 'date'})}


class MaterialForm(_ItemEstoqueForm):
    class Meta:
        model = Material
        fields = _ItemEstoqueForm.campos
        labels = _ItemEstoqueForm.rotulos
        widgets = _ItemEstoqueForm.widgets_comuns


class MedicamentoForm(_ItemEstoqueForm):
    class Meta:
        model = Medicamento
        fields = _ItemEstoqueForm.campos
        labels = _ItemEstoqueForm.rotulos
        widgets = _ItemEstoqueForm.widgets_comuns


class LoteForm(forms.Form):
    """Entrada de novo lote (UC-20 / inserirNovoLote)."""

    quantidade = forms.IntegerField(label='Quantidade', min_value=1)
    numeroLote = forms.CharField(label='Número do lote', required=False, max_length=50)
    dataValidade = forms.DateField(
        label='Data de validade', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )


class DispensarForm(forms.Form):
    """Dispensação de medicamento (UC-13)."""

    quantidade = forms.IntegerField(label='Quantidade', min_value=1)
    idFarmaceutico = forms.IntegerField(label='ID do farmacêutico', min_value=1)
    idProntuario = forms.IntegerField(label='ID do prontuário (opcional)',
                                      required=False, min_value=1)


class ConsumoForm(forms.Form):
    """Registro de consumo de material por enfermeiro."""

    quantidade = forms.IntegerField(label='Quantidade', min_value=1)
    idEnfermeiro = forms.IntegerField(label='ID do enfermeiro', min_value=1)


class ReposicaoForm(forms.Form):
    """Solicitação de reposição ao gestor (UC-14 / UC-17)."""

    quantidade = forms.IntegerField(label='Quantidade solicitada', min_value=1)
    justificativa = forms.CharField(
        label='Justificativa', required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
    )
    idSolicitante = forms.IntegerField(label='ID do solicitante', required=False,
                                       min_value=1)
