# Formulários do Módulo Financeiro.

from django import forms

from apps.atendimento.entity_atendimento.models import Consulta


class PagamentoForm(forms.Form):
    """Registro do pagamento de uma consulta (UC-07)."""

    valor = forms.DecimalField(
        label='Valor (R$)', max_digits=10, decimal_places=2, min_value=0.01,
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0,00'}),
    )
    formaPagamento = forms.ChoiceField(
        label='Forma de pagamento', choices=Consulta.FORMA_PAGAMENTO_CHOICES,
    )


class RelatorioForm(forms.Form):
    """Filtro de período do relatório financeiro (UC-09 / UC-10)."""

    inicio = forms.DateField(
        label='De', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    fim = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
