# Importa os models do Módulo de Gestão de Acesso para que o Django reconheça as
# tabelas nas migrations.

from apps.acesso.entity_funcionario.models import (
    Recepcionista,
    Medico,
    Enfermeiro,
    Farmaceutico,
    Gestor,
)
