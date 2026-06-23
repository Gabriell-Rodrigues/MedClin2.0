# Representa as Entities do Módulo Farmacêutico (Material e Medicamento), além das
# tabelas de associação com o Gestor e dos registros de consumo e dispensação.
#
# Atributos conforme o Mapeamento Objeto-Relacional do grupo:
#   Material/Medicamento -> id, nome, descricao, numeroLote, quantidadeEstoque,
#                           quantidadeMinima, dataValidade
#   Gestor_Material / Gestor_Medicamento -> idGestor, idMaterial/idMedicamento
#   Material_Consumido    -> idConsumo, quantidade, idMaterial, idEnfermeiro
#   Medicamento_Dispensado-> idDispensacao, quantidade, idFarmaceutico,
#                            idMedicamento, idProntuario

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ItemEstoque(models.Model):
    """
    Base abstrata para itens controlados em estoque (Material e Medicamento).

    Implementa os comportamentos do diagrama de classes: adicionarEstoque,
    removerEstoque, verificarAlertaEstoqueMinimo e verificarValidadeProxima.
    """

    nome = models.CharField(max_length=120)
    descricao = models.TextField(blank=True, default='')
    numeroLote = models.CharField(max_length=50, blank=True, default='',
                                  db_column='numeroLote')
    quantidadeEstoque = models.PositiveIntegerField(
        default=0, db_column='quantidadeEstoque')
    quantidadeMinima = models.PositiveIntegerField(
        default=0, db_column='quantidadeMinima')
    dataValidade = models.DateField(null=True, blank=True, db_column='dataValidade')

    # Preço unitário do item (usado no controle financeiro).
    valor = models.DecimalField(max_digits=10, decimal_places=2,
                                null=True, blank=True)

    # Reposição solicitada ao gestor (vira notificação na caixa do gestor).
    reposicaoSolicitada = models.BooleanField(
        default=False, db_column='reposicaoSolicitada')
    quantidadeSolicitada = models.PositiveIntegerField(
        null=True, blank=True, db_column='quantidadeSolicitada')
    justificativaReposicao = models.TextField(
        blank=True, default='', db_column='justificativaReposicao')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.nome} ({self.quantidadeEstoque} em estoque)'

    def adicionar_estoque(self, quantidade, lote=None, validade=None):
        """Adiciona um novo lote ao estoque."""
        if quantidade is None or quantidade <= 0:
            raise ValidationError('A quantidade adicionada deve ser positiva.')
        self.quantidadeEstoque += quantidade
        if lote:
            self.numeroLote = lote
        if validade:
            self.dataValidade = validade
        self.save()
        return self

    def remover_estoque(self, quantidade):
        """Remove (dá baixa) uma quantidade do estoque."""
        if quantidade is None or quantidade <= 0:
            raise ValidationError('A quantidade removida deve ser positiva.')
        if quantidade > self.quantidadeEstoque:
            raise ValidationError('Quantidade indisponível em estoque.')
        self.quantidadeEstoque -= quantidade
        self.save()
        return self

    def abaixo_do_minimo(self):
        """Verifica o alerta de estoque mínimo."""
        return self.quantidadeEstoque <= self.quantidadeMinima

    def validade_proxima(self, dias=30):
        """Verifica se a validade está próxima (padrão: 30 dias)."""
        if not self.dataValidade:
            return False
        return self.dataValidade <= (timezone.now().date() + timedelta(days=dias))


class Material(ItemEstoque):
    idMaterial = models.AutoField(primary_key=True, db_column='idMaterial')

    class Meta:
        db_table = 'Material'
        verbose_name = 'Material'
        verbose_name_plural = 'Materiais'
        ordering = ['nome']


class Medicamento(ItemEstoque):
    idMedicamento = models.AutoField(primary_key=True, db_column='idMedicamento')

    class Meta:
        db_table = 'Medicamento'
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'
        ordering = ['nome']


class GestorMaterial(models.Model):
    """Tabela associativa Gestor_Material."""

    idGestor = models.IntegerField(db_column='idGestor')
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, db_column='idMaterial',
        related_name='gestores',
    )

    class Meta:
        db_table = 'Gestor_Material'
        verbose_name = 'Vínculo gestor-material'
        verbose_name_plural = 'Vínculos gestor-material'
        unique_together = (('idGestor', 'material'),)


class GestorMedicamento(models.Model):
    """Tabela associativa Gestor_Medicamento."""

    idGestor = models.IntegerField(db_column='idGestor')
    medicamento = models.ForeignKey(
        Medicamento, on_delete=models.CASCADE, db_column='idMedicamento',
        related_name='gestores',
    )

    class Meta:
        db_table = 'Gestor_Medicamento'
        verbose_name = 'Vínculo gestor-medicamento'
        verbose_name_plural = 'Vínculos gestor-medicamento'
        unique_together = (('idGestor', 'medicamento'),)


class MaterialConsumido(models.Model):
    """
    Registro de consumo de material por um enfermeiro (Material_Consumido).
    """

    idConsumo = models.AutoField(primary_key=True, db_column='idConsumo')
    quantidade = models.PositiveIntegerField()
    material = models.ForeignKey(
        Material, on_delete=models.PROTECT, db_column='idMaterial',
        related_name='consumos',
    )
    idEnfermeiro = models.IntegerField(db_column='idEnfermeiro')
    dataConsumo = models.DateTimeField(auto_now_add=True, db_column='dataConsumo')

    class Meta:
        db_table = 'Material_Consumido'
        verbose_name = 'Consumo de material'
        verbose_name_plural = 'Consumos de material'
        ordering = ['-idConsumo']

    def __str__(self):
        return f'Consumo {self.idConsumo} - {self.quantidade}x {self.material.nome}'


class MedicamentoDispensado(models.Model):
    """
    Registro de dispensação de medicamento por um farmacêutico
    (Medicamento_Dispensado).
    """

    idDispensacao = models.AutoField(primary_key=True, db_column='idDispensacao')
    quantidade = models.PositiveIntegerField()
    idFarmaceutico = models.IntegerField(db_column='idFarmaceutico')
    medicamento = models.ForeignKey(
        Medicamento, on_delete=models.PROTECT, db_column='idMedicamento',
        related_name='dispensacoes',
    )
    idProntuario = models.IntegerField(null=True, blank=True, db_column='idProntuario')
    dataDispensacao = models.DateTimeField(auto_now_add=True, db_column='dataDispensacao')

    class Meta:
        db_table = 'Medicamento_Dispensado'
        verbose_name = 'Dispensação de medicamento'
        verbose_name_plural = 'Dispensações de medicamento'
        ordering = ['-idDispensacao']

    def __str__(self):
        return f'Dispensação {self.idDispensacao} - {self.quantidade}x {self.medicamento.nome}'
