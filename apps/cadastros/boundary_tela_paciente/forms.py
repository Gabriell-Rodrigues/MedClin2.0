# Representa a Boundary TelaPaciente, contendo os formulários de cadastro, edição e busca de pacientes.

from django import forms

from apps.cadastros.entity_paciente.models import Paciente
from apps.cadastros.validators import validar_cpf


class PacienteForm(forms.ModelForm):
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Digite a senha do paciente'
        }),
        required=False
    )

    class Meta:
        model = Paciente

        fields = [
            'nome',
            'cpf',
            'telefone',
            'dataNascimento',
            'email',
            'senha',
    # Campos de integração com outros módulos.
    # Comentados temporariamente até os apps acesso, atendimento e prontuario
    # estarem prontos no projeto.
    # 'idRecepcionista',
    # 'idAgenda',
    # 'idProntuario',
        ]

        labels = {
            'nome': 'Nome completo',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'dataNascimento': 'Data de nascimento',
            'email': 'E-mail',
            'senha': 'Senha',
    # Labels de integração com outros módulos.
    # Comentados temporariamente até os apps correspondentes existirem.
    # 'idRecepcionista': 'Recepcionista responsável',
    # 'idAgenda': 'Agenda vinculada',
    # 'idProntuario': 'Prontuário vinculado
        }

        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Digite o nome completo'
            }),
            'cpf': forms.TextInput(attrs={
                'placeholder': '000.000.000-00'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(00) 00000-0000'
            }),
            'dataNascimento': forms.DateInput(attrs={
                'type': 'date'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'paciente@email.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Define regras diferentes para cadastro e edição.

        No cadastro, a senha é obrigatória.
        Na edição, a senha pode ficar em branco para manter a senha atual.
        """

        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['senha'].required = False
            self.fields['senha'].help_text = 'Deixe em branco para manter a senha atual.'
        else:
            self.fields['senha'].required = True

    def clean_cpf(self):
        """
        Valida o CPF e impede CPF duplicado.
        """

        cpf = self.cleaned_data.get('cpf')
        cpf_limpo = validar_cpf(cpf)

        paciente_duplicado = Paciente.objects.filter(cpf=cpf_limpo)

        if self.instance and self.instance.pk:
            paciente_duplicado = paciente_duplicado.exclude(pk=self.instance.pk)

        if paciente_duplicado.exists():
            raise forms.ValidationError('Já existe um paciente cadastrado com este CPF.')

        return cpf_limpo

    def clean_email(self):
        """
        Impede cadastro de e-mail duplicado.
        """

        email = self.cleaned_data.get('email')

        if email:
            email = email.strip().lower()

        paciente_duplicado = Paciente.objects.filter(email__iexact=email)

        if self.instance and self.instance.pk:
            paciente_duplicado = paciente_duplicado.exclude(pk=self.instance.pk)

        if paciente_duplicado.exists():
            raise forms.ValidationError('Já existe um paciente cadastrado com este e-mail.')

        return email

    def clean_senha(self):
        """
        No cadastro, a senha é obrigatória.
        Na edição, pode ficar vazia.
        """

        senha = self.cleaned_data.get('senha')

        if not self.instance.pk and not senha:
            raise forms.ValidationError('A senha é obrigatória.')

        return senha


class BuscaPacienteCPFForm(forms.Form):
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '000.000.000-00'
        })
    )

    def clean_cpf(self):
        """
        Valida o CPF informado na busca.
        """

        cpf = self.cleaned_data.get('cpf')
        return validar_cpf(cpf)


class BuscaPacienteNomeForm(forms.Form):
    nome = forms.CharField(
        label='Nome',
        max_length=120,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite o nome do paciente'
        })
    )

    def clean_nome(self):
        """
        Remove espaços extras do nome buscado.
        """

        nome = self.cleaned_data.get('nome')

        if nome:
            nome = nome.strip()

        if not nome:
            raise forms.ValidationError('Digite um nome para buscar.')

        return nome