# Testes do Módulo Financeiro (pagamento UC-07, relatório UC-09/10) e da caixa
# de notificações do gestor (reposição UC-14/17 + estoque mínimo, UC-20).

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.atendimento.entity_atendimento.models import Consulta
from apps.farmacia.entity_estoque.models import Medicamento
from apps.farmacia.control_ctr_estoque.services import CTRMedicamento
from apps.financeiro.control_ctr_pagamento.services import CTRFinanceiro
from .helpers import (criar_recepcionista, criar_gestor, criar_farmaceutico,
                      SENHA)


class PagamentoTests(TestCase):
    def _consulta(self, **kw):
        base = dict(data='2026-09-01', horario='09:00', idPaciente=1, idMedico=1)
        base.update(kw)
        return Consulta.objects.create(**base)

    def test_registrar_pagamento_marca_consulta(self):
        c = self._consulta()
        CTRFinanceiro.registrar_pagamento(c, Decimal('150.00'), 'pix')
        c.refresh_from_db()
        self.assertTrue(c.pago)
        self.assertEqual(c.valor, Decimal('150.00'))
        self.assertEqual(c.formaPagamento, 'pix')
        self.assertIsNotNone(c.dataPagamento)

    def test_nao_paga_consulta_cancelada(self):
        c = self._consulta(status=Consulta.STATUS_CANCELADA)
        with self.assertRaises(ValidationError):
            CTRFinanceiro.registrar_pagamento(c, Decimal('100'), 'dinheiro')

    def test_nao_paga_duas_vezes(self):
        c = self._consulta()
        CTRFinanceiro.registrar_pagamento(c, Decimal('100'), 'dinheiro')
        with self.assertRaises(ValidationError):
            CTRFinanceiro.registrar_pagamento(c, Decimal('100'), 'dinheiro')

    def test_forma_invalida_rejeitada(self):
        c = self._consulta()
        with self.assertRaises(ValidationError):
            CTRFinanceiro.registrar_pagamento(c, Decimal('100'), 'boleto')

    def test_relatorio_agrega_total_e_quantidade(self):
        c1 = self._consulta()
        c2 = self._consulta(horario='10:00')
        CTRFinanceiro.registrar_pagamento(c1, Decimal('100'), 'pix')
        CTRFinanceiro.registrar_pagamento(c2, Decimal('50'), 'dinheiro')
        rel = CTRFinanceiro.gerar_relatorio()
        self.assertEqual(rel['quantidade'], 2)
        self.assertEqual(rel['total'], Decimal('150'))


class ReposicaoNotificacaoTests(TestCase):
    def test_solicitar_reposicao_e_atender(self):
        med = Medicamento.objects.create(nome='Dipirona', quantidadeEstoque=1,
                                         quantidadeMinima=10)
        CTRMedicamento.solicitar_reposicao(med, 20, 'acabando', id_solicitante=5)
        med.refresh_from_db()
        self.assertTrue(med.reposicaoSolicitada)
        self.assertEqual(med.quantidadeSolicitada, 20)

        CTRMedicamento.atender_reposicao(med, atendida=True)
        med.refresh_from_db()
        self.assertFalse(med.reposicaoSolicitada)
        self.assertIsNone(med.quantidadeSolicitada)

    def test_reposicao_apenas_para_item_abaixo_do_minimo(self):
        med = Medicamento.objects.create(nome='Soro', quantidadeEstoque=50,
                                         quantidadeMinima=10)
        with self.assertRaises(ValidationError):
            CTRMedicamento.solicitar_reposicao(med, 5, 'x', id_solicitante=5)


class FinanceiroRBACTests(TestCase):
    def setUp(self):
        criar_recepcionista('r@t.com')
        criar_gestor('g@t.com')
        criar_farmaceutico('f@t.com')

    def _login(self, email):
        self.client.post(reverse('acesso:login'),
                         {'email_ou_cpf': email, 'senha': SENHA})

    def test_recepcionista_acessa_pagamentos(self):
        self._login('r@t.com')
        resp = self.client.get(reverse('financeiro:pagamentos_pendentes'))
        self.assertEqual(resp.status_code, 200)

    def test_gestor_acessa_relatorio_e_notificacoes(self):
        self._login('g@t.com')
        self.assertEqual(
            self.client.get(reverse('financeiro:relatorio')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('farmacia:notificacoes_gestor')).status_code, 200)

    def test_farmaceutico_nao_acessa_relatorio(self):
        self._login('f@t.com')
        resp = self.client.get(reverse('financeiro:relatorio'))
        self.assertEqual(resp.status_code, 403)
