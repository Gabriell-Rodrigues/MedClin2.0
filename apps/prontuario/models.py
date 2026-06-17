# Importa os models do Módulo de Prontuário Eletrônico para que o Django
# reconheça as tabelas nas migrations.

from apps.prontuario.entity_prontuario.models import (
    Prontuario,
    MedicoProntuario,
    EnfermeiroProntuario,
    FarmaceuticoProntuario,
)
