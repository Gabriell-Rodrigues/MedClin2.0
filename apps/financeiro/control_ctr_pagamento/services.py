# Control do Módulo Financeiro. Concentra as regras de pagamento de consulta
# (UC-07) e do relatório financeiro (UC-09 / UC-10).
#
# Decisão de modelagem: não há tabela "Pagamento" — os dados de pagamento são
# colunas da própria Consulta (valor, formaPagamento, pago, dataPagamento),
# conforme o OR atualizado. O relatório é uma agregação sobre essas colunas.

import logging
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.atendimento.entity_atendimento.models import Consulta

_auditoria = logging.getLogger('medclin.auditoria')


class CTRFinanceiro:
    @staticmethod
    def registrar_pagamento(consulta, valor, forma):
        """Registra o pagamento de uma consulta (UC-07)."""
        if consulta.pago:
            raise ValidationError('Esta consulta já está paga.')
        if consulta.status == Consulta.STATUS_CANCELADA:
            raise ValidationError(
                'Não é possível registrar pagamento de consulta cancelada.'
            )
        try:
            valor = Decimal(valor)
        except (TypeError, InvalidOperation):
            raise ValidationError('Informe um valor válido.')
        if valor <= 0:
            raise ValidationError('O valor deve ser maior que zero.')
        if forma not in dict(Consulta.FORMA_PAGAMENTO_CHOICES):
            raise ValidationError('Forma de pagamento inválida.')

        consulta.valor = valor
        consulta.formaPagamento = forma
        consulta.pago = True
        consulta.dataPagamento = timezone.now()
        consulta.save(update_fields=['valor', 'formaPagamento', 'pago',
                                     'dataPagamento'])
        _auditoria.info(
            f'financeiro | Consulta#{consulta.idConsulta} | '
            f'Pagamento registrado ({forma}, R$ {valor}).'
        )
        return consulta

    @staticmethod
    def listar_pendentes():
        """Consultas não canceladas e ainda não pagas (UC-07)."""
        return Consulta.objects.exclude(
            status=Consulta.STATUS_CANCELADA
        ).filter(pago=False).order_by('-data', '-horario')

    @staticmethod
    def listar_pagas(inicio=None, fim=None):
        """Consultas pagas, opcionalmente filtradas por período de pagamento."""
        qs = Consulta.objects.filter(pago=True)
        if inicio:
            qs = qs.filter(dataPagamento__date__gte=inicio)
        if fim:
            qs = qs.filter(dataPagamento__date__lte=fim)
        return qs.order_by('-dataPagamento')

    @staticmethod
    def gerar_relatorio(inicio=None, fim=None):
        """Relatório financeiro: total recebido e quebra por forma (UC-09/10)."""
        pagas = list(CTRFinanceiro.listar_pagas(inicio, fim))
        total = sum((c.valor or Decimal('0')) for c in pagas)
        por_forma = {}
        for c in pagas:
            rotulo = c.get_formaPagamento_display() or '—'
            por_forma[rotulo] = por_forma.get(rotulo, Decimal('0')) + (c.valor or Decimal('0'))
        return {
            'consultas': pagas,
            'quantidade': len(pagas),
            'total': total,
            'por_forma': por_forma,
        }
