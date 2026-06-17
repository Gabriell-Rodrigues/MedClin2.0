# Testes do módulo de Prontuário Eletrônico: registro de evolução como addendum
# (UC-12) e controle de acesso por profissional autorizado (UC-11).

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.prontuario.entity_prontuario.models import Prontuario
from apps.prontuario.control_ctr_prontuario.services import CTRProntuario


class EvolucaoTests(TestCase):
    def test_evolucao_acrescenta_sem_apagar_historico(self):
        pr = Prontuario.objects.create()
        CTRProntuario.conceder_acesso(pr, 'medico', 10)

        CTRProntuario.registrar_evolucao(pr, 10, 'Diagnostico A', 'Obs A', 'Presc A')
        CTRProntuario.registrar_evolucao(pr, 10, 'Diagnostico B', 'Obs B', 'Presc B')

        pr.refresh_from_db()
        # As duas evoluções aparecem no histórico (addendum, sem apagar a anterior).
        self.assertIn('Diagnostico A', pr.historicoEvolucoes)
        self.assertIn('Diagnostico B', pr.historicoEvolucoes)
        # Os campos atuais refletem a evolução mais recente.
        self.assertEqual(pr.diagnostico, 'Diagnostico B')

    def test_evolucao_exige_medico_autorizado(self):
        pr = Prontuario.objects.create()
        with self.assertRaises(ValidationError):
            CTRProntuario.registrar_evolucao(pr, 999, 'X', '', '')

    def test_evolucao_vazia_e_rejeitada(self):
        pr = Prontuario.objects.create()
        CTRProntuario.conceder_acesso(pr, 'medico', 10)
        with self.assertRaises(ValidationError):
            CTRProntuario.registrar_evolucao(pr, 10, '', '', '')


class AcessoProntuarioTests(TestCase):
    def test_conceder_e_verificar_acesso(self):
        pr = Prontuario.objects.create()
        self.assertFalse(CTRProntuario.verificar_acesso(pr, 'enfermeiro', 7))
        CTRProntuario.conceder_acesso(pr, 'enfermeiro', 7)
        self.assertTrue(CTRProntuario.verificar_acesso(pr, 'enfermeiro', 7))

    def test_conceder_acesso_e_idempotente(self):
        pr = Prontuario.objects.create()
        criado1 = CTRProntuario.conceder_acesso(pr, 'medico', 3)
        criado2 = CTRProntuario.conceder_acesso(pr, 'medico', 3)
        self.assertTrue(criado1)
        self.assertFalse(criado2)
