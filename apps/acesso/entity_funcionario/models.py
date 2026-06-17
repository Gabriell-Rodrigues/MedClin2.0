# Representa as Entities do Módulo de Gestão de Acesso (funcionários/profissionais
# da clínica), definindo seus dados e relacionamentos no banco de dados.
#
# Atributos conforme o Mapeamento Objeto-Relacional do grupo:
#   Recepcionista  -> idRecepcionista, nome, cpf, email, senha, telefone
#   Medico         -> idMedico, nome, cpf, email, senha, telefone, crm,
#                     especializacao, idAgenda
#   Enfermeiro     -> idEnfermeiro, nome, cpf, email, senha, telefone, coren
#   Farmaceutico   -> idFarmaceutico, nome, cpf, telefone, email, senha, crf
#   Gestor         -> idGestor, nome, cpf, telefone, email, senha
#
# Os métodos efetuarLogin/efetuarLogout/solicitarRedefinicaoSenha do diagrama de
# classes são implementados na camada de controle (CTRFuncionario), mantendo a
# Entity responsável apenas pelos dados e pela criptografia da senha.

from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from apps.cadastros.validators import formatar_cpf


class Funcionario(models.Model):
    """
    Classe base abstrata dos funcionários/profissionais da clínica.

    Concentra os atributos e comportamentos comuns a todos os perfis com acesso
    ao sistema (nome, cpf, email, senha, telefone), evitando duplicação. Cada
    perfil concreto define sua própria tabela e chave primária, conforme o
    Mapeamento Objeto-Relacional.
    """

    nome = models.CharField(max_length=120)
    cpf = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    telefone = models.CharField(max_length=20)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.nome} - {self.cpf}'

    def set_senha(self, senha_pura):
        """Criptografa a senha antes de salvar no banco."""
        self.senha = make_password(senha_pura)

    def conferir_senha(self, senha_pura):
        """Verifica se a senha digitada corresponde à senha criptografada."""
        return check_password(senha_pura, self.senha)

    @property
    def cpf_formatado(self):
        """Retorna o CPF formatado para exibição na tela."""
        return formatar_cpf(self.cpf)


class Recepcionista(Funcionario):
    idRecepcionista = models.AutoField(primary_key=True, db_column='idRecepcionista')

    class Meta:
        db_table = 'Recepcionista'
        verbose_name = 'Recepcionista'
        verbose_name_plural = 'Recepcionistas'
        ordering = ['nome']


class Medico(Funcionario):
    idMedico = models.AutoField(primary_key=True, db_column='idMedico')
    crm = models.CharField(max_length=20, unique=True)
    especializacao = models.CharField(max_length=120, blank=True, default='')

    # Referência ao módulo de atendimento (Agenda). Mantida como IntegerField por
    # ser um vínculo entre apps distintos, seguindo a convenção do projeto.
    idAgenda = models.IntegerField(null=True, blank=True, db_column='idAgenda')

    class Meta:
        db_table = 'Medico'
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['nome']


class Enfermeiro(Funcionario):
    idEnfermeiro = models.AutoField(primary_key=True, db_column='idEnfermeiro')
    coren = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'Enfermeiro'
        verbose_name = 'Enfermeiro'
        verbose_name_plural = 'Enfermeiros'
        ordering = ['nome']


class Farmaceutico(Funcionario):
    idFarmaceutico = models.AutoField(primary_key=True, db_column='idFarmaceutico')
    crf = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'Farmaceutico'
        verbose_name = 'Farmacêutico'
        verbose_name_plural = 'Farmacêuticos'
        ordering = ['nome']


class Gestor(Funcionario):
    idGestor = models.AutoField(primary_key=True, db_column='idGestor')

    class Meta:
        db_table = 'Gestor'
        verbose_name = 'Gestor'
        verbose_name_plural = 'Gestores'
        ordering = ['nome']
