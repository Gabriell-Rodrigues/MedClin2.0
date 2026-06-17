# Testes do módulo de Fluxo de Atendimento: regra de conflito de horário no
# agendamento (UC-05, fluxo de exceção FE-05-1) e no reagendamento.
#
# Regra: um médico não pode ter duas consultas ATIVAS (não canceladas) na mesma
# data e horário.

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.atendimento.entity_atendimento.models import Consulta
from apps.atendimento.control_ctr_consulta.services import CTRConsulta
from .helpers import criar_medico, criar_paciente


class ConflitoHorarioTests(TestCase):
    def setUp(self):
        self.medico = criar_medico('m@test.com')
        self.medico2 = criar_medico('m2@test.com')
        self.paciente = criar_paciente('p@test.com')
        self.paciente2 = criar_paciente('p2@test.com')

    def _dados(self, medico, paciente, data='2026-09-01', horario='09:00'):
        return dict(idMedico=medico.pk, idPaciente=paciente.pk,
                    data=data, horario=horario)

    def test_mesmo_medico_mesmo_horario_e_barrado(self):
        CTRConsulta.agendar_consulta(self._dados(self.medico, self.paciente))
        with self.assertRaises(ValidationError):
            CTRConsulta.agendar_consulta(self._dados(self.medico, self.paciente2))
        self.assertEqual(
            Consulta.objects.filter(idMedico=self.medico.pk).count(), 1
        )

    def test_medicos_diferentes_no_mesmo_horario_sao_permitidos(self):
        CTRConsulta.agendar_consulta(self._dados(self.medico, self.paciente))
        CTRConsulta.agendar_consulta(self._dados(self.medico2, self.paciente))
        self.assertEqual(Consulta.objects.count(), 2)

    def test_consulta_cancelada_libera_o_horario(self):
        consulta = CTRConsulta.agendar_consulta(
            self._dados(self.medico, self.paciente)
        )
        CTRConsulta.cancelar_consulta(consulta)
        nova = CTRConsulta.agendar_consulta(
            self._dados(self.medico, self.paciente2)
        )
        self.assertEqual(nova.status, Consulta.STATUS_CONFIRMADA)

    def test_reagendar_para_horario_ocupado_e_barrado(self):
        CTRConsulta.agendar_consulta(self._dados(self.medico, self.paciente,
                                                 horario='09:00'))
        outra = CTRConsulta.agendar_consulta(self._dados(self.medico,
                                                         self.paciente2,
                                                         horario='10:00'))
        with self.assertRaises(ValidationError):
            CTRConsulta.reagendar_consulta(outra, '2026-09-01', '09:00')

    def test_agendar_exige_paciente_e_medico_existentes(self):
        with self.assertRaises(ValidationError):
            CTRConsulta.agendar_consulta(
                dict(idMedico=999999, idPaciente=999999,
                     data='2026-09-01', horario='11:00')
            )
