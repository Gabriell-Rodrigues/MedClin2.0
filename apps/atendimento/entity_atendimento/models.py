# Representa as Entities do Módulo de Fluxo de Atendimento (Agenda e Consulta),
# definindo seus dados e relacionamentos no banco de dados.
#
# Atributos conforme o Mapeamento Objeto-Relacional do grupo:
#   Agenda   -> idAgenda, data, horariosProfissionais, ocupacaoSalas
#   Consulta -> idConsulta, data, horario, status, idSala, idAgenda, idPaciente,
#               idMedico, idProntuario
#
# Tabela associativa:
#   Recepcionista_Agenda -> idRecepcionista, idAgenda
#
# Seguindo a convenção do projeto, relacionamentos dentro do mesmo app são FK
# reais (Consulta -> Agenda) e referências entre apps distintos são mantidas como
# IntegerField (idPaciente, idMedico, idProntuario, idRecepcionista, idSala).

from django.db import models


class Agenda(models.Model):
    idAgenda = models.AutoField(primary_key=True, db_column='idAgenda')

    data = models.DateField()

    # Map<Integer, String> do diagrama de classes: profissionalId -> horários.
    horariosProfissionais = models.JSONField(
        default=dict,
        blank=True,
        db_column='horariosProfissionais',
    )

    ocupacaoSalas = models.IntegerField(default=0, db_column='ocupacaoSalas')

    class Meta:
        db_table = 'Agenda'
        verbose_name = 'Agenda'
        verbose_name_plural = 'Agendas'
        ordering = ['-data']

    def __str__(self):
        return f'Agenda {self.idAgenda} - {self.data:%d/%m/%Y}'


class RecepcionistaAgenda(models.Model):
    """
    Tabela associativa Recepcionista_Agenda: vincula uma recepcionista a uma
    agenda que ela administra.
    """

    idRecepcionista = models.IntegerField(db_column='idRecepcionista')

    agenda = models.ForeignKey(
        Agenda,
        on_delete=models.CASCADE,
        db_column='idAgenda',
        related_name='recepcionistas',
    )

    class Meta:
        db_table = 'Recepcionista_Agenda'
        verbose_name = 'Vínculo recepcionista-agenda'
        verbose_name_plural = 'Vínculos recepcionista-agenda'
        unique_together = (('idRecepcionista', 'agenda'),)

    def __str__(self):
        return f'Recepcionista {self.idRecepcionista} -> Agenda {self.agenda_id}'


class Consulta(models.Model):
    STATUS_AGENDADA = 'agendada'
    STATUS_CONFIRMADA = 'confirmada'
    STATUS_CONCLUIDA = 'concluida'
    STATUS_CANCELADA = 'cancelada'

    STATUS_CHOICES = (
        (STATUS_AGENDADA, 'Agendada'),
        (STATUS_CONFIRMADA, 'Confirmada'),
        (STATUS_CONCLUIDA, 'Concluída'),
        (STATUS_CANCELADA, 'Cancelada'),
    )

    idConsulta = models.AutoField(primary_key=True, db_column='idConsulta')

    data = models.DateField()
    horario = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CONFIRMADA,
    )

    idSala = models.IntegerField(null=True, blank=True, db_column='idSala')

    agenda = models.ForeignKey(
        Agenda,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='idAgenda',
        related_name='consultas',
    )

    # Referências a outros módulos (loose coupling via IntegerField).
    idPaciente = models.IntegerField(db_column='idPaciente')
    idMedico = models.IntegerField(db_column='idMedico')
    idProntuario = models.IntegerField(null=True, blank=True, db_column='idProntuario')

    # --- Pagamento (UC-07): registrado pela recepcionista na própria consulta ---
    FORMA_DINHEIRO = 'dinheiro'
    FORMA_CARTAO = 'cartao'
    FORMA_PIX = 'pix'
    FORMA_PAGAMENTO_CHOICES = (
        (FORMA_DINHEIRO, 'Dinheiro'),
        (FORMA_CARTAO, 'Cartão'),
        (FORMA_PIX, 'PIX'),
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2,
                                null=True, blank=True)
    formaPagamento = models.CharField(max_length=20, blank=True, default='',
                                      choices=FORMA_PAGAMENTO_CHOICES,
                                      db_column='formaPagamento')
    pago = models.BooleanField(default=False)
    dataPagamento = models.DateTimeField(null=True, blank=True,
                                         db_column='dataPagamento')

    class Meta:
        db_table = 'Consulta'
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'
        ordering = ['-data', '-horario']

    def __str__(self):
        return f'Consulta {self.idConsulta} - {self.data:%d/%m/%Y} {self.horario:%H:%M}'

    @property
    def ativa(self):
        """Indica se a consulta não foi cancelada."""
        return self.status != self.STATUS_CANCELADA
