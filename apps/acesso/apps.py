# Define as configurações principais do app de acesso dentro do projeto Django.

from django.apps import AppConfig


class AcessoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.acesso'
    verbose_name = 'Módulo de Gestão de Acesso'
