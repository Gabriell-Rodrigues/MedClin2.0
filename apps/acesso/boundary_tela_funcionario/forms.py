# Representa as Boundaries (Telas) do Módulo de Gestão de Acesso, contendo os
# formulários de cadastro/edição de funcionários, login e redefinição de senha.

from django import forms

from apps.cadastros.validators import validar_cpf
from apps.acesso.entity_funcionario.models import (
    Recepcionista,
    Medico,
    Enfermeiro,
    Farmaceutico,
    Gestor,
)


class FuncionarioForm(forms.ModelForm):
    """
    Formulário base de cadastro/edição de funcionários.

    No cadastro a senha é obrigatória; na edição pode ficar em branco para
    manter a senha atual.
    """

    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Digite a senha'}),
        required=False,
    )

    campos_comuns = ['nome', 'cpf', 'telefone', 'email', 'senha']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['senha'].required = False
            self.fields['senha'].help_text = 'Deixe em branco para manter a senha atual.'
        else:
            self.fields['senha'].required = True

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        cpf_limpo = validar_cpf(cpf)

        duplicado = self._meta.model.objects.filter(cpf=cpf_limpo)
        if self.instance and self.instance.pk:
            duplicado = duplicado.exclude(pk=self.instance.pk)

        if duplicado.exists():
            raise forms.ValidationError('Já existe um funcionário com este CPF.')

        return cpf_limpo

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()

        duplicado = self._meta.model.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            duplicado = duplicado.exclude(pk=self.instance.pk)

        if duplicado.exists():
            raise forms.ValidationError('Já existe um funcionário com este e-mail.')

        return email

    def clean_senha(self):
        senha = self.cleaned_data.get('senha')

        if not self.instance.pk and not senha:
            raise forms.ValidationError('A senha é obrigatória.')

        return senha


class RecepcionistaForm(FuncionarioForm):
    class Meta:
        model = Recepcionista
        fields = ['nome', 'cpf', 'telefone', 'email', 'senha']


class MedicoForm(FuncionarioForm):
    class Meta:
        model = Medico
        fields = ['nome', 'cpf', 'telefone', 'email', 'senha',
                  'crm', 'especializacao', 'idAgenda']
        labels = {'crm': 'CRM', 'especializacao': 'Especialização',
                  'idAgenda': 'Agenda vinculada (ID)'}


class EnfermeiroForm(FuncionarioForm):
    class Meta:
        model = Enfermeiro
        fields = ['nome', 'cpf', 'telefone', 'email', 'senha', 'coren']
        labels = {'coren': 'COREN'}


class FarmaceuticoForm(FuncionarioForm):
    class Meta:
        model = Farmaceutico
        fields = ['nome', 'cpf', 'telefone', 'email', 'senha', 'crf']
        labels = {'crf': 'CRF'}


class GestorForm(FuncionarioForm):
    class Meta:
        model = Gestor
        fields = ['nome', 'cpf', 'telefone', 'email', 'senha']


FORMS_POR_PERFIL = {
    'recepcionista': RecepcionistaForm,
    'medico': MedicoForm,
    'enfermeiro': EnfermeiroForm,
    'farmaceutico': FarmaceuticoForm,
    'gestor': GestorForm,
}


class LoginForm(forms.Form):
    """Formulário de login (UC-01)."""

    email_ou_cpf = forms.CharField(
        label='E-mail ou CPF',
        max_length=120,
        widget=forms.TextInput(attrs={'placeholder': 'E-mail ou CPF'}),
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}),
    )


class SolicitarRedefinicaoForm(forms.Form):
    """Solicitação do link de redefinição de senha por e-mail (UC-02, passo 1)."""

    email = forms.EmailField(
        label='E-mail cadastrado',
        widget=forms.EmailInput(attrs={'placeholder': 'seu@email.com'}),
    )


class NovaSenhaForm(forms.Form):
    """Definição da nova senha a partir do link recebido (UC-02, passo 2)."""

    nova_senha = forms.CharField(
        label='Nova senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Nova senha'}),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita a nova senha'}),
    )

    def clean(self):
        cleaned = super().clean()
        nova = cleaned.get('nova_senha')
        confirmar = cleaned.get('confirmar_senha')

        if nova and confirmar and nova != confirmar:
            raise forms.ValidationError('As senhas não conferem.')

        return cleaned
