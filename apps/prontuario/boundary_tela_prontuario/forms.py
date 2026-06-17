# Representa a Boundary TelaProntuario, contendo os formulários de inicialização,
# registro de evolução e controle de acesso ao prontuário.

from django import forms

from apps.prontuario.control_ctr_prontuario.services import CTRProntuario


class InicializarProntuarioForm(forms.Form):
    """
    Formulário para inicializar um novo prontuário (UC-06).

    O vínculo com um paciente é opcional. Quando informado, o prontuário é
    associado ao paciente por meio do atributo idProntuario do cadastro.
    """

    idPaciente = forms.IntegerField(
        label='ID do paciente (opcional)',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Informe o ID do paciente para vincular'
        })
    )

    def clean_idPaciente(self):
        """
        Valida que o paciente informado existe no módulo de cadastros.
        """

        id_paciente = self.cleaned_data.get('idPaciente')

        if not id_paciente:
            return None

        try:
            from apps.cadastros.entity_paciente.models import Paciente
        except ImportError:
            raise forms.ValidationError(
                'O módulo de cadastros não está disponível para vincular o paciente.'
            )

        if not Paciente.objects.filter(idPaciente=id_paciente).exists():
            raise forms.ValidationError('Não existe paciente com o ID informado.')

        return id_paciente


class EvolucaoForm(forms.Form):
    """
    Formulário de registro de evolução clínica (UC-12).

    Apenas médicos autorizados podem registrar a evolução, por isso o
    identificador do médico é solicitado e validado no controle.
    """

    idMedico = forms.IntegerField(
        label='ID do médico responsável',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Informe o ID do médico autorizado'
        })
    )

    diagnostico = forms.CharField(
        label='Diagnóstico',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Diagnóstico clínico (CID-10, hipóteses, etc.)'
        })
    )

    observacoes = forms.CharField(
        label='Observações',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Queixas, conduta e observações do atendimento'
        })
    )

    prescricaoAtiva = forms.CharField(
        label='Prescrição ativa',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Medicação prescrita e posologia'
        })
    )

    def clean(self):
        """
        Garante que ao menos um campo clínico da evolução tenha sido preenchido.
        """

        cleaned = super().clean()

        diagnostico = (cleaned.get('diagnostico') or '').strip()
        observacoes = (cleaned.get('observacoes') or '').strip()
        prescricao = (cleaned.get('prescricaoAtiva') or '').strip()

        if not diagnostico and not observacoes and not prescricao:
            raise forms.ValidationError(
                'Informe ao menos um campo da evolução clínica.'
            )

        return cleaned


class AcessoProntuarioForm(forms.Form):
    """
    Formulário de controle de acesso ao prontuário (UC-11).

    Usado tanto para conceder acesso a um profissional quanto para verificar
    se um profissional possui acesso autorizado.
    """

    perfil = forms.ChoiceField(
        label='Perfil profissional',
        choices=CTRProntuario.PERFIS
    )

    idProfissional = forms.IntegerField(
        label='ID do profissional',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Informe o ID do profissional'
        })
    )
