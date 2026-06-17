# Define as configurações principais do app de atendimento dentro do projeto.

from django.apps import AppConfig


class AtendimentoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.atendimento'
    verbose_name = 'Módulo de Fluxo de Atendimento'
