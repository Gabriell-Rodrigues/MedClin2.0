# Representa a Entity Prontuario, definindo os dados clínicos do paciente e os
# relacionamentos de acesso por perfil profissional no banco de dados.
#
# Atributos conforme o Mapeamento Objeto-Relacional do grupo (tabela Prontuario):
#   idProntuario, dataCriacao, diagnostico, observacoes, historicoEvolucoes, prescricaoAtiva
#
# As tabelas associativas Medico_Prontuario, Enfermeiro_Prontuario e
# Farmaceutico_Prontuario representam os profissionais autorizados a acessar o
# prontuário, conforme a Tabela 18 do Documento de Arquitetura (Módulo de
# Prontuário Eletrônico).

from django.db import models


class Prontuario(models.Model):
    idProntuario = models.AutoField(
        primary_key=True,
        db_column='idProntuario'
    )

    dataCriacao = models.DateTimeField(
        auto_now_add=True,
        db_column='dataCriacao'
    )

    diagnostico = models.TextField(
        blank=True,
        default=''
    )

    observacoes = models.TextField(
        blank=True,
        default=''
    )

    historicoEvolucoes = models.TextField(
        blank=True,
        default='',
        db_column='historicoEvolucoes'
    )

    prescricaoAtiva = models.TextField(
        blank=True,
        default='',
        db_column='prescricaoAtiva'
    )

    class Meta:
        db_table = 'Prontuario'
        verbose_name = 'Prontuário'
        verbose_name_plural = 'Prontuários'
        ordering = ['-idProntuario']

    def __str__(self):
        return f'Prontuário {self.idProntuario}'


class MedicoProntuario(models.Model):
    """
    Tabela associativa Medico_Prontuario.

    Representa o acesso autorizado de um médico a um prontuário.
    """

    # Integração futura com o módulo de acesso.
    # Este relacionamento será reativado quando o model Medico estiver pronto.
    # idMedico = models.ForeignKey(
    #     'acesso.Medico',
    #     on_delete=models.CASCADE,
    #     db_column='idMedico',
    #     related_name='prontuarios_autorizados'
    # )

    idMedico = models.IntegerField(
        db_column='idMedico'
    )

    prontuario = models.ForeignKey(
        Prontuario,
        on_delete=models.CASCADE,
        db_column='idProntuario',
        related_name='medicos_autorizados'
    )

    class Meta:
        db_table = 'Medico_Prontuario'
        verbose_name = 'Acesso de médico ao prontuário'
        verbose_name_plural = 'Acessos de médicos aos prontuários'
        unique_together = (('idMedico', 'prontuario'),)

    def __str__(self):
        return f'Médico {self.idMedico} -> Prontuário {self.prontuario_id}'


class EnfermeiroProntuario(models.Model):
    """
    Tabela associativa Enfermeiro_Prontuario.

    Representa o acesso autorizado de um enfermeiro a um prontuário.
    """

    # Integração futura com o módulo de acesso.
    # Este relacionamento será reativado quando o model Enfermeiro estiver pronto.
    # idEnfermeiro = models.ForeignKey(
    #     'acesso.Enfermeiro',
    #     on_delete=models.CASCADE,
    #     db_column='idEnfermeiro',
    #     related_name='prontuarios_autorizados'
    # )

    idEnfermeiro = models.IntegerField(
        db_column='idEnfermeiro'
    )

    prontuario = models.ForeignKey(
        Prontuario,
        on_delete=models.CASCADE,
        db_column='idProntuario',
        related_name='enfermeiros_autorizados'
    )

    class Meta:
        db_table = 'Enfermeiro_Prontuario'
        verbose_name = 'Acesso de enfermeiro ao prontuário'
        verbose_name_plural = 'Acessos de enfermeiros aos prontuários'
        unique_together = (('idEnfermeiro', 'prontuario'),)

    def __str__(self):
        return f'Enfermeiro {self.idEnfermeiro} -> Prontuário {self.prontuario_id}'


class FarmaceuticoProntuario(models.Model):
    """
    Tabela associativa Farmaceutico_Prontuario.

    Representa o acesso autorizado de um farmacêutico a um prontuário.
    """

    # Integração futura com o módulo de acesso.
    # Este relacionamento será reativado quando o model Farmaceutico estiver pronto.
    # idFarmaceutico = models.ForeignKey(
    #     'acesso.Farmaceutico',
    #     on_delete=models.CASCADE,
    #     db_column='idFarmaceutico',
    #     related_name='prontuarios_autorizados'
    # )

    idFarmaceutico = models.IntegerField(
        db_column='idFarmaceutico'
    )

    prontuario = models.ForeignKey(
        Prontuario,
        on_delete=models.CASCADE,
        db_column='idProntuario',
        related_name='farmaceuticos_autorizados'
    )

    class Meta:
        db_table = 'Farmaceutico_Prontuario'
        verbose_name = 'Acesso de farmacêutico ao prontuário'
        verbose_name_plural = 'Acessos de farmacêuticos aos prontuários'
        unique_together = (('idFarmaceutico', 'prontuario'),)

    def __str__(self):
        return f'Farmacêutico {self.idFarmaceutico} -> Prontuário {self.prontuario_id}'
