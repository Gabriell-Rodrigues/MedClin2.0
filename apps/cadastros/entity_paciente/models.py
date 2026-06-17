# Representa a Entity Paciente, definindo seus dados e relacionamentos no banco de dados.

from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from apps.cadastros.validators import formatar_cpf


class Paciente(models.Model):
    idPaciente = models.AutoField(
        primary_key=True,
        db_column='idPaciente'
    )

    nome = models.CharField(
        max_length=120
    )

    cpf = models.CharField(
        max_length=11,
        unique=True
    )

    telefone = models.CharField(
        max_length=20
    )

    dataNascimento = models.DateField(
        db_column='dataNascimento'
    )

    email = models.EmailField(
        unique=True
    )

    senha = models.CharField(
        max_length=128
    )
    
    # Integração futura com o módulo de acesso.
# Este relacionamento será reativado quando o model Recepcionista estiver pronto.
# idRecepcionista = models.ForeignKey(
#     'acesso.Recepcionista',
#     on_delete=models.SET_NULL,
#     null=True,
#     blank=True,
#     db_column='idRecepcionista',
#     related_name='pacientes_cadastrados'
# )

    idRecepcionista = models.IntegerField(
    null=True,
    blank=True,
    db_column='idRecepcionista'
    )


# Integração futura com o módulo de atendimento.
# Este relacionamento será reativado quando o model Agenda estiver pronto.
# idAgenda = models.ForeignKey(
#     'atendimento.Agenda',
#     on_delete=models.SET_NULL,
#     null=True,
#     blank=True,
#     db_column='idAgenda',
#     related_name='pacientes'
# )

    idAgenda = models.IntegerField(
    null=True,
    blank=True,
    db_column='idAgenda'
    )

# Integração futura com o módulo de prontuário.
# Este relacionamento será reativado quando o model Prontuario estiver pronto.
# idProntuario = models.ForeignKey(
#     'prontuario.Prontuario',
#     on_delete=models.SET_NULL,
#     null=True,
#     blank=True,
#     db_column='idProntuario',
#     related_name='pacientes'
# )

    idProntuario = models.IntegerField(
    null=True,
    blank=True,
    db_column='idProntuario'
)

    class Meta:
        db_table = 'Paciente'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'

    def __str__(self):
        return f'{self.nome} - {self.cpf}'

    def set_senha(self, senha_pura):
        """
        Criptografa a senha antes de salvar no banco.
        """

        self.senha = make_password(senha_pura)

    def conferir_senha(self, senha_pura):
        """
        Verifica se a senha digitada corresponde à senha criptografada.
        """

        return check_password(senha_pura, self.senha)

    @property
    def cpf_formatado(self):
        """
        Retorna o CPF formatado para exibição na tela.
        """

        return formatar_cpf(self.cpf)