# Representa os Controls (CTR) do Módulo Farmacêutico, concentrando as regras de
# negócio de estoque de materiais e medicamentos, dispensação e consumo.
#
# Casos de uso atendidos:
#   UC-13 - Liberar Medicamentos (Dispensação)
#   UC-14 - Solicitar Novos Medicamentos ao Gestor
#   UC-15 - Verificar Estoque de Materiais
#   UC-16 - Verificar Estoque de Medicamentos
#   UC-17 - Solicitar Novos Materiais ao Gestor
#   UC-20 - Gerenciar Estoques
#
# Observação (decisão de projeto): o Mapeamento Objeto-Relacional não define uma
# entidade de "solicitação de reposição". Portanto, UC-14/UC-17 são tratados como
# uma notificação registrada (sem tabela dedicada), respeitando a prioridade do
# mapeamento sobre os casos de uso.

import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from apps.farmacia.entity_estoque.models import (
    Material,
    Medicamento,
    MaterialConsumido,
    MedicamentoDispensado,
)

_auditoria = logging.getLogger('medclin.auditoria')


class CTRItemEstoque:
    """Regras comuns de estoque para Material e Medicamento."""

    model = None
    label = 'Item'

    @classmethod
    def cadastrar(cls, dados):
        item = cls.model(
            nome=dados.get('nome'),
            descricao=dados.get('descricao', ''),
            numeroLote=dados.get('numeroLote', ''),
            quantidadeEstoque=dados.get('quantidadeEstoque') or 0,
            quantidadeMinima=dados.get('quantidadeMinima') or 0,
            dataValidade=dados.get('dataValidade'),
        )
        item.full_clean()
        item.save()
        cls._log(item, f'{cls.label} cadastrado.')
        return item

    @classmethod
    def editar(cls, item, dados):
        item.nome = dados.get('nome')
        item.descricao = dados.get('descricao', '')
        item.numeroLote = dados.get('numeroLote', '')
        item.quantidadeEstoque = dados.get('quantidadeEstoque') or 0
        item.quantidadeMinima = dados.get('quantidadeMinima') or 0
        item.dataValidade = dados.get('dataValidade')
        item.full_clean()
        item.save()
        cls._log(item, f'{cls.label} atualizado.')
        return item

    @classmethod
    def listar(cls):
        return cls.model.objects.all()

    @classmethod
    def buscar_por_id(cls, pk):
        return cls.model.objects.filter(pk=pk).first()

    @classmethod
    def buscar(cls, termo):
        termo = (termo or '').strip()
        if not termo:
            return cls.model.objects.none()
        return cls.model.objects.filter(
            Q(nome__icontains=termo) | Q(descricao__icontains=termo)
        ).order_by('nome')

    @classmethod
    def adicionar_lote(cls, item, quantidade, lote=None, validade=None):
        """Inserção de novo lote pelo Gestor (UC-20)."""
        item.adicionar_estoque(quantidade, lote, validade)
        cls._log(item, f'Lote adicionado (+{quantidade}).')
        return item

    @classmethod
    def listar_criticos(cls):
        """Itens com estoque igual ou abaixo do mínimo."""
        return [i for i in cls.model.objects.all() if i.abaixo_do_minimo()]

    @classmethod
    def solicitar_reposicao(cls, item, quantidade, justificativa, id_solicitante=None):
        """
        Solicita reposição ao gestor (UC-14 / UC-17).

        Sem entidade no mapeamento OR; registrada como notificação simples.
        """
        if not quantidade or quantidade <= 0:
            raise ValidationError('Informe uma quantidade válida para reposição.')
        cls._log(
            item,
            f'Solicitação de reposição: +{quantidade} '
            f'(solicitante {id_solicitante}). Justificativa: {justificativa}',
        )
        return True

    @staticmethod
    def _log(item, mensagem):
        _auditoria.info(f'farmacia | {type(item).__name__}#{item.pk} | {mensagem}')


class CTRMateriais(CTRItemEstoque):
    model = Material
    label = 'Material'

    @classmethod
    @transaction.atomic
    def registrar_consumo(cls, material, quantidade, id_enfermeiro):
        """Registra o consumo de material por um enfermeiro."""
        if not id_enfermeiro:
            raise ValidationError('Informe o enfermeiro responsável.')
        # Trava a linha do material até o fim da transação, evitando baixa
        # concorrente (no-op em SQLite; lock real em PostgreSQL).
        material = cls.model.objects.select_for_update().get(pk=material.pk)
        material.remover_estoque(quantidade)
        consumo = MaterialConsumido.objects.create(
            quantidade=quantidade,
            material=material,
            idEnfermeiro=id_enfermeiro,
        )
        cls._log(material, f'Consumo registrado ({quantidade}) pelo enfermeiro {id_enfermeiro}.')
        return consumo


class CTRMedicamento(CTRItemEstoque):
    model = Medicamento
    label = 'Medicamento'

    @classmethod
    @transaction.atomic
    def dispensar(cls, medicamento, quantidade, id_farmaceutico, id_prontuario=None):
        """Dispensa um medicamento, dando baixa no estoque (UC-13)."""
        if not id_farmaceutico:
            raise ValidationError('Informe o farmacêutico responsável.')
        # Trava a linha do medicamento até o fim da transação, evitando baixa
        # concorrente (no-op em SQLite; lock real em PostgreSQL).
        medicamento = cls.model.objects.select_for_update().get(pk=medicamento.pk)
        medicamento.remover_estoque(quantidade)
        dispensacao = MedicamentoDispensado.objects.create(
            quantidade=quantidade,
            idFarmaceutico=id_farmaceutico,
            medicamento=medicamento,
            idProntuario=id_prontuario,
        )
        cls._log(medicamento, f'Dispensação de {quantidade} pelo farmacêutico {id_farmaceutico}.')
        return dispensacao
