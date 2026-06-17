# Importa os models do Módulo de Fluxo de Atendimento para que o Django reconheça
# as tabelas nas migrations.

from apps.atendimento.entity_atendimento.models import (
    Agenda,
    RecepcionistaAgenda,
    Consulta,
)
