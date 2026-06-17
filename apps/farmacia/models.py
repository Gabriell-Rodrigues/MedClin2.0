# Importa os models do Módulo Farmacêutico para que o Django reconheça as tabelas
# nas migrations.

from apps.farmacia.entity_estoque.models import (
    Material,
    Medicamento,
    GestorMaterial,
    GestorMedicamento,
    MaterialConsumido,
    MedicamentoDispensado,
)
