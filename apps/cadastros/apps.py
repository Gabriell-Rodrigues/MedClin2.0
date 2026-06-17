# Define as configurações principais do app de cadastros dentro do projeto Django.

from django.apps import AppConfig


class CadastrosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cadastros'
    verbose_name = 'Módulo de Gestão de Cadastros'