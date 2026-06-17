# Representa as Boundaries (Telas) do Módulo de Fluxo de Atendimento, contendo os
# formulários de agendamento, reagendamento e consulta de agenda.

from django import forms

from apps.atendimento.entity_atendimento.models import Agenda, Consulta


class ConsultaForm(forms.Form):
    """Formulário de agendamento de consulta (UC-05)."""

    idPaciente = forms.IntegerField(
        label='ID do paciente', min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'ID do paciente'}),
    )
    idMedico = forms.IntegerField(
        label='ID do médico', min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'ID do médico'}),
    )
    data = forms.DateField(
        label='Data', widget=forms.DateInput(attrs={'type': 'date'}),
    )
    horario = forms.TimeField(
        label='Horário', widget=forms.TimeInput(attrs={'type': 'time'}),
    )
    idSala = forms.IntegerField(
        label='Sala (opcional)', required=False, min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Nº da sala'}),
    )
    agenda = forms.ModelChoiceField(
        label='Agenda (opcional)', required=False,
        queryset=Agenda.objects.all(), empty_label='— sem agenda —',
    )
    idProntuario = forms.IntegerField(
        label='Prontuário (opcional)', required=False, min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'ID do prontuário'}),
    )


class ReagendarForm(forms.Form):
    """Formulário de reagendamento de consulta."""

    nova_data = forms.DateField(
        label='Nova data', widget=forms.DateInput(attrs={'type': 'date'}),
    )
    novo_horario = forms.TimeField(
        label='Novo horário', widget=forms.TimeInput(attrs={'type': 'time'}),
    )


class AgendaForm(forms.ModelForm):
    """Formulário de criação de agenda."""

    class Meta:
        model = Agenda
        fields = ['data', 'ocupacaoSalas']
        labels = {'data': 'Data', 'ocupacaoSalas': 'Salas ocupadas'}
        widgets = {'data': forms.DateInput(attrs={'type': 'date'})}


class ConsultarAgendaMedicoForm(forms.Form):
    """Filtro da agenda do médico (UC-19)."""

    idMedico = forms.IntegerField(label='ID do médico', min_value=1)
    data = forms.DateField(
        label='Data (opcional)', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )


class ConsultarAgendaPacienteForm(forms.Form):
    """Filtro dos agendamentos do paciente (UC-04)."""

    idPaciente = forms.IntegerField(label='ID do paciente', min_value=1)
