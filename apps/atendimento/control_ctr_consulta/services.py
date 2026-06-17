# Representa os Controls (CTR) do Módulo de Fluxo de Atendimento, concentrando as
# regras de negócio de agendamento e gestão de consultas e agendas.
#
# Casos de uso atendidos:
#   UC-04 - Visualizar Agendamentos (paciente)
#   UC-05 - Agendar Consulta (recepcionista)
#   UC-19 - Consultar Agenda de Consultas (médico)

import logging

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.atendimento.entity_atendimento.models import Agenda, Consulta

_auditoria = logging.getLogger('medclin.auditoria')


class CTRAgenda:
    """Regras de negócio relacionadas à Agenda."""

    @staticmethod
    def criar_agenda(data, ocupacao_salas=0, horarios_profissionais=None):
        agenda = Agenda(
            data=data,
            ocupacaoSalas=ocupacao_salas or 0,
            horariosProfissionais=horarios_profissionais or {},
        )
        agenda.full_clean()
        agenda.save()
        return agenda

    @staticmethod
    def listar_agendas():
        return Agenda.objects.all()

    @staticmethod
    def buscar_por_id(id_agenda):
        return Agenda.objects.filter(idAgenda=id_agenda).first()


class CTRConsulta:
    """Regras de negócio relacionadas à Consulta."""

    @staticmethod
    def _horario_ocupado(id_medico, data, horario, excluir=None):
        """
        Verifica se o médico já possui consulta ativa no mesmo dia/horário.
        """
        qs = Consulta.objects.filter(
            idMedico=id_medico,
            data=data,
            horario=horario,
        ).exclude(status=Consulta.STATUS_CANCELADA)

        if excluir is not None:
            qs = qs.exclude(pk=excluir.pk)

        return qs.exists()

    @staticmethod
    @transaction.atomic
    def agendar_consulta(dados):
        """
        Agenda uma nova consulta (UC-05).

        Valida a existência do paciente e do médico, verifica a disponibilidade
        do horário e persiste a consulta com status 'confirmada'.
        """

        id_paciente = dados.get('idPaciente')
        id_medico = dados.get('idMedico')
        data = dados.get('data')
        horario = dados.get('horario')

        if not id_paciente or not id_medico:
            raise ValidationError('Paciente e médico são obrigatórios.')

        if not data or not horario:
            raise ValidationError('Data e horário são obrigatórios.')

        CTRConsulta._validar_paciente(id_paciente)
        CTRConsulta._validar_medico(id_medico)

        if CTRConsulta._horario_ocupado(id_medico, data, horario):
            raise ValidationError(
                'O médico já possui uma consulta neste dia e horário.'
            )

        consulta = Consulta(
            data=data,
            horario=horario,
            status=Consulta.STATUS_CONFIRMADA,
            idSala=dados.get('idSala'),
            agenda=dados.get('agenda'),
            idPaciente=id_paciente,
            idMedico=id_medico,
            idProntuario=dados.get('idProntuario'),
        )
        consulta.full_clean()
        consulta.save()

        CTRConsulta._log(consulta, 'Consulta agendada (status confirmada).')
        return consulta

    @staticmethod
    @transaction.atomic
    def reagendar_consulta(consulta, nova_data, novo_horario):
        """Reagenda uma consulta para nova data/horário."""

        if consulta.status == Consulta.STATUS_CANCELADA:
            raise ValidationError('Não é possível reagendar uma consulta cancelada.')

        if CTRConsulta._horario_ocupado(
            consulta.idMedico, nova_data, novo_horario, excluir=consulta
        ):
            raise ValidationError(
                'O médico já possui uma consulta neste dia e horário.'
            )

        consulta.data = nova_data
        consulta.horario = novo_horario
        consulta.status = Consulta.STATUS_CONFIRMADA
        consulta.full_clean()
        consulta.save()

        CTRConsulta._log(consulta, 'Consulta reagendada.')
        return consulta

    @staticmethod
    def cancelar_consulta(consulta):
        """Cancela uma consulta."""
        consulta.status = Consulta.STATUS_CANCELADA
        consulta.save(update_fields=['status'])
        CTRConsulta._log(consulta, 'Consulta cancelada.')
        return consulta

    @staticmethod
    def alterar_status(consulta, novo_status):
        """Altera o status de uma consulta para um valor válido."""
        validos = dict(Consulta.STATUS_CHOICES)
        if novo_status not in validos:
            raise ValidationError('Status de consulta inválido.')
        consulta.status = novo_status
        consulta.save(update_fields=['status'])
        CTRConsulta._log(consulta, f'Status alterado para {novo_status}.')
        return consulta

    @staticmethod
    def listar_consultas():
        return Consulta.objects.all()

    @staticmethod
    def buscar_por_id(id_consulta):
        return Consulta.objects.filter(idConsulta=id_consulta).first()

    @staticmethod
    def listar_por_medico(id_medico, data=None):
        """Agenda do médico (UC-19)."""
        qs = Consulta.objects.filter(idMedico=id_medico)
        if data:
            qs = qs.filter(data=data)
        return qs.order_by('data', 'horario')

    @staticmethod
    def listar_por_paciente(id_paciente):
        """Agendamentos/histórico do paciente (UC-03 / UC-04)."""
        return Consulta.objects.filter(
            idPaciente=id_paciente
        ).order_by('-data', '-horario')

    # ------------------------------------------------------------------
    @staticmethod
    def _validar_paciente(id_paciente):
        from apps.cadastros.entity_paciente.models import Paciente
        if not Paciente.objects.filter(idPaciente=id_paciente).exists():
            raise ValidationError('Não existe paciente com o ID informado.')

    @staticmethod
    def _validar_medico(id_medico):
        from apps.acesso.entity_funcionario.models import Medico
        if not Medico.objects.filter(idMedico=id_medico).exists():
            raise ValidationError('Não existe médico com o ID informado.')

    @staticmethod
    def _log(consulta, mensagem):
        _auditoria.info(f'atendimento | Consulta#{consulta.idConsulta} | {mensagem}')
